import base64
import hashlib 
import hmac
import time

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, nowdate, nowtime

MST = "Maintenance Schedule Task"
IST = "Installation Task"
TASK_DOCTYPES = (MST, IST)

TASK_FIELDS = {
	MST: [
		"name", "customer", "item_code", "serial_no", "scheduled_date", "start_date", "end_date", "completion_status",
		"service_engineer", "customer_current_address", "customer_billing_address", "contact",
		"email", "territory", "maintenance_schedule", "maintenance_schedule_detail", "work_done",
	],
	IST: [
		"name", "customer", "item_code", "serial_no", "scheduled_date", "completion_status",
		"service_engineer", "customer_current_address", "customer_billing_address", "contact",
		"email", "territory", "installation", "installation_detail", "task_type", "installed_qty",
	],
}

# ------------------------------ OTP (generation lives in tq_crm_support) ------------------------------ #
OTP_VALIDITY_SECONDS = 300  # 5 minutes
VISIT = "CRM Maintenance Visit"
VISIT_PURPOSE = "CRM Maintenance Visit Purpose"
NOTE = "Installation Note"

def _otp_lock_key(scope):																		#Creates a unique cache key for an OTP request
	return f"visit_otp_sent:{frappe.session.user}:{scope}"

def _otp_scope(task_names):																		#Generates a consistent identifier for one task or a combined group of tasks
	names = sorted(set(task_names))
	if len(names) == 1:
		return names[0]
	return hashlib.sha1("|".join(names).encode()).hexdigest()[:20]

def _check_resend_lock(scope):																					 #Gets the timestamp when the OTP was last sent.
	sent_at = frappe.cache.get_value(_otp_lock_key(scope))
	if sent_at:
		wait = OTP_VALIDITY_SECONDS - int(time.time() - float(sent_at))
		if wait > 0:
			frappe.throw(_("OTP already sent. Try again in {0}:{1}").format(wait // 60, str(wait % 60).zfill(2)))

def _start_otp_window(scope):					                                                                  #Starts the five-minute OTP resend restriction.
	frappe.cache.set_value(_otp_lock_key(scope), time.time(), expires_in_sec=OTP_VALIDITY_SECONDS)

def _verify_draft_code(doctype, name, scope, code):																  #Verifies the OTP entered by the customer.
	if not frappe.cache.get_value(_otp_lock_key(scope)):
		frappe.throw(_("The code has expired. Please generate a new one."))
	saved = frappe.db.get_value(doctype, name, "customer_confirmation_code")
	if not saved or not hmac.compare_digest(str(saved), str(code or "").strip()):
		frappe.throw(_("Invalid confirmation code"))
	return str(saved)

def _otp_response(res):																							#Prepares the API response after generating an OTP
	code = (res or {}).get("code")
	return {
		"confirmation_required": True,
		"expires_in": OTP_VALIDITY_SECONDS,
		# "dev_code": code if frappe.conf.developer_mode else None,  # never the code itself otherwise
	}

def _find_draft_visit(names):																		#Finds an existing Draft CRM Maintenance Visit for the selected task or tasks
	wanted = set(names)
	parents = frappe.get_all(
		VISIT_PURPOSE,
		filters={"parenttype": VISIT, "prevdoc_docname": ["in", list(names)]},
		pluck="parent",
	)
	for parent in dict.fromkeys(parents):
		d = frappe.db.get_value(VISIT, parent, ["docstatus", "owner"], as_dict=True)
		if not d or d.docstatus != 0 or d.owner != frappe.session.user:
			continue
		rows = set(frappe.get_all(VISIT_PURPOSE, filters={"parent": parent, "parenttype": VISIT}, pluck="prevdoc_docname"))
		if rows == wanted:
			return parent
	return None

def _find_draft_note(task_name):															#Finds an existing Draft Installation Note belonging to the current user and linked to the given Installation Task
	return frappe.db.get_value(
		NOTE, {"installation_task": task_name, "docstatus": 0, "owner": frappe.session.user}, "name"
	)

def _new_draft_visit(task, data):															#Creates a new Draft CRM Maintenance Visit for a single Maintenance Schedule Task.
	from tq_crm_support.api.maintenance_schedule_api import make_maintenance_visit_from_task
	mv = _as_admin(make_maintenance_visit_from_task, task.name)
	series = _default_naming_series(mv.doctype)
	if series:
		mv.naming_series = series
	if mv.customer:
		mv.customer_name = frappe.db.get_value("Customer", mv.customer, "customer_name")
	mv.company = (
		mv.company
		or frappe.db.get_value("CRM Maintenance Schedule", task.maintenance_schedule, "company")
		or frappe.defaults.get_global_default("company")
	)
	resolution = data.get("resolution_status") or "Fully Resolved"
	mv.completion_status = (
		"Fully Completed"
		if resolution == "Fully Resolved"
		else "Partially Completed"
	)
	mv.mntc_date = nowdate()
	mv.mntc_time = nowtime()
	mv.insert(ignore_permissions=True)
	return mv.name

def _new_draft_combined(names):																		#Creates a Draft CRM Maintenance Visit for multiple tasks.
	from tq_crm_support.api.combined_maintenance_visit_api import create_combined_maintenance_visit
	res = _as_admin(create_combined_maintenance_visit, names)
	frappe.db.set_value(VISIT, res["name"], "owner", frappe.session.user)
	return res["name"]

def _otp_remaining(scope):
	sent_at = frappe.cache.get_value(_otp_lock_key(scope))
	if not sent_at:
		return 0
	return max(OTP_VALIDITY_SECONDS - int(time.time() - float(sent_at)), 0)


def _draft_materials(doc):
	out = []
	for m in doc.get("consumed_materials") or []:
		info = frappe.db.get_value(
			"Item", m.item_code, ["item_name", "has_serial_no", "has_batch_no"], as_dict=True
		) or {}
		out.append({
			"item_code": m.item_code,
			"item_name": info.get("item_name") or m.item_code,
			"uom": m.uom,
			"qty": flt(m.qty),
			"rate": flt(m.rate),
			"warehouse": m.warehouse,
			"stock_qty": None,
			"billing_type": m.billing_type or "Free",
			"serial_no": m.serial_no or "",
			"serial_nos": _split_serials(m.serial_no),
			"batch_no": m.batch_no or "",
			"has_serial_no": bool(info.get("has_serial_no")),
			"has_batch_no": bool(info.get("has_batch_no")),
		})
	return out


def _fill_visit(mv, data, otp_code=None, combined=False):							#Copies the information submitted by the frontend into a CRM Maintenance Visit document.
	resolution = data.get("resolution_status") or "Fully Resolved"
	fully = resolution == "Fully Resolved"
	note = (data.get("work_done") or "").strip()
	work_done = f"{resolution}: {note}" if note else resolution
	status = "Fully Completed" if fully else "Partially Completed"
	lat, lon = _coords(data)

	mv.mntc_date = nowdate()
	mv.mntc_time = nowtime()
	mv.completion_status = status
	mv.customer_feedback = data.get("feedback")
	_set_if_field(mv, "checkin_lat", lat)
	_set_if_field(mv, "checkin_long", lon)
	_set_if_field(mv, "resolution_status", resolution)
	_set_if_field(mv, "customer_confirmation_code", otp_code)
	if combined:
		for p in mv.purposes:
			p.work_done = work_done
			p.task_completion_status = status
	elif mv.purposes:
		mv.purposes[0].work_done = work_done

	mv.set("consumed_materials", [])          # Save can run many times: no duplicate rows
	_append_consumed_materials(mv, data.get("materials"))
	return work_done, status


def _fill_note(note, task, data, otp_code=None, strict=True):								#Copies installation form data into an Installation Note.
	fully = (data.get("completion_status") or "Fully Completed") == "Fully Completed"
	qty = flt(data.get("installed_qty")) or flt(task.installed_qty) or 1
	lat, lon = _coords(data)

	lines = [f"{'[x]' if c.get('checked') else '[ ]'} {c.get('label')}" for c in (data.get("checklist") or [])]
	if data.get("handover_notes"):
		lines += ["", data["handover_notes"]]

	note.inst_date = nowdate()
	note.inst_time = nowtime()
	note.completion_status = "Fully Completed" if fully else "Partially Completed"
	note.remarks = "\n".join(lines)
	if not note.territory:
		note.territory = (
			task.territory
			or frappe.db.get_value("Customer", task.customer, "territory")
			or frappe.db.get_single_value("Selling Settings", "territory")
			or "All Territories"
		)
	_set_if_field(note, "checkin_lat", lat)
	_set_if_field(note, "checkin_long", lon)
	_set_if_field(note, "customer_confirmation_code", otp_code)

	if note.items:
		note.items[0].qty = qty
		if frappe.db.get_value("Item", task.item_code, "has_serial_no"):
			serials = _split_serials(data.get("serial_no"))
			if len(serials) == int(qty):
				note.items[0].serial_no = "\n".join(serials)
			elif strict:
				frappe.throw(_("Enter {0} serial no(s) for the installed unit").format(int(qty)))
		else:
			note.items[0].serial_no = None

	note.set("consumed_materials", [])
	_append_consumed_materials(note, data.get("materials"))
	return qty, fully

#_visit_form() and _note_form() allow engineers to resume previously saved drafts.
def _visit_form(doc):												
	resolution = doc.get("resolution_status") or "Fully Resolved"
	work = (doc.purposes[0].work_done if doc.purposes else "") or ""
	if work.startswith(f"{resolution}: "):
		work = work[len(resolution) + 2:]
	elif work == resolution:
		work = ""
	return {
		"resolution_status": resolution,
		"work_done": work,
		"feedback": doc.get("customer_feedback") or "",
		"materials": _draft_materials(doc),
	}


def _note_form(note):												
	checked, rest = [], []
	lines = (note.remarks or "").split("\n")
	for i, line in enumerate(lines):
		if line.startswith("[x] ") or line.startswith("[ ] "):
			if line.startswith("[x] "):
				checked.append(line[4:])
		else:
			rest = lines[i:]
			break
	first = note.items[0] if note.items else None
	return {
		"completion_status": note.completion_status if note.completion_status in ("Fully Completed", "Partially Completed") else "Fully Completed",
		"installed_qty": flt(first.qty) if first else 1,
		"serial_no": ", ".join(_split_serials(first.serial_no)) if first else "",
		"checked": checked,
		"handover_notes": "\n".join(rest).strip(),
		"materials": _draft_materials(note),
	}

# ------------------------------ helpers ------------------------------ #
def _current_employee():
	user = frappe.session.user
	if not user or user == "Guest":
		return None
	return frappe.db.get_value(
		"Employee", {"user_id": user, "status": "Active"}, ["name", "employee_name"], as_dict=True
	)


def _get_my_team():
	if not frappe.db.exists("DocType", "CRM Service Team"):
		return None
	emp = _current_employee()
	if not emp:
		return None
	return frappe.db.get_value(
		"CRM Service Team",
		{"employee": emp.name, "enabled": 1},
		["name", "employee", "is_group", "parent_crm_service_team"],
		as_dict=True,
	)


def _require_team():
	team = _get_my_team()
	if not team:
		frappe.throw(_("You are not part of an active CRM Service Team"), frappe.PermissionError)
	return team


def _subordinate_teams(team_name: str) -> list:
	found, queue = [], [team_name]
	while queue:
		children = frappe.get_all(
			"CRM Service Team",
			filters={"parent_crm_service_team": ["in", queue], "enabled": 1},
			pluck="name",
		)
		children = [c for c in children if c != team_name and c not in found]
		found.extend(children)
		queue = children
	return found


def _get_my_task(doctype: str, name: str):
	me = _require_team()
	if doctype not in TASK_DOCTYPES:
		frappe.throw(_("Invalid task type"))
	if not name or not frappe.db.exists(doctype, name):
		frappe.throw(_("Task not found"))
	task = frappe.get_doc(doctype, name)
	if task.docstatus != 1 or task.service_engineer != me.name:
		frappe.throw(_("This task is not assigned to you"), frappe.PermissionError)
	return task


def _parse(data):
	return frappe.parse_json(data) if isinstance(data, str) else (data or {})

def _default_warehouse():
	"""Default warehouse from CRM Support Settings, or None if not set."""
	return frappe.db.get_single_value(
		"CRM Support Settings", "default_consumable_warehouse"
	) or None

def _stock_map(item_codes, warehouse):
	"""{item_code: actual_qty} for the given warehouse."""
	if not item_codes or not warehouse:
		return {}
	return {
		b.item_code: flt(b.actual_qty)
		for b in frappe.get_all(
			"Bin",
			filters={"item_code": ["in", item_codes], "warehouse": warehouse},
			fields=["item_code", "actual_qty"],
		)
	}                                                                          

def _split_serials(value):
	"""Accept a list or a string (newline/comma separated) and return a clean list."""
	if not value:
		return []
	if isinstance(value, str):
		value = value.replace(",", "\n").splitlines()
	return [s.strip() for s in value if s and s.strip()]


def _validate_spare_serials(item_code, warehouse, qty, serials):
	if not frappe.db.get_value("Item", item_code, "has_serial_no"):
		return
	if len(serials) != int(qty):
		frappe.throw(_("{0}: select exactly {1} serial no(s)").format(item_code, int(qty)))
	valid = frappe.get_all(
		"Serial No",
		filters={
			"name": ["in", serials],
			"item_code": item_code,
			"warehouse": warehouse,
			"status": "Active",
		},
		pluck="name",
	)
	invalid = set(serials) - set(valid)
	if invalid:
		frappe.throw(_("Not available in {0}: {1}").format(warehouse, ", ".join(invalid)))


def _append_consumed_materials(doc, materials):
	default_wh = _default_warehouse()
	for m in materials or []:
		qty = flt(m.get("qty"))
		if qty <= 0:
			continue
		rate = flt(m.get("rate"))
		warehouse = m.get("warehouse") or default_wh
		if not warehouse:
			frappe.throw(_("Select a warehouse for {0}").format(m.get("item_code")))
		serials = _split_serials(m.get("serial_nos") or m.get("serial_no"))

		_validate_spare_serials(m.get("item_code"), warehouse, qty, serials)

		doc.append("consumed_materials", {
			"item_code": m.get("item_code"),
			"warehouse": warehouse,
			"qty": qty,
			"uom": m.get("uom"),
			"rate": rate,
			"amount": qty * rate,
			"billing_type": m.get("billing_type") or "Free",
			"serial_no": "\n".join(serials),
			"batch_no": m.get("batch_no"),
		})

def _as_admin(fn, *args, **kwargs):
	"""Run one trusted call with full rights, then restore the engineer's session."""
	user = frappe.session.user
	frappe.set_user("Administrator")
	try:
		return fn(*args, **kwargs)
	finally:
		frappe.set_user(user)

def _coords(data):
	try:
		lat, lon = float(data.get("latitude")), float(data.get("longitude"))
		return (lat, lon) if (lat or lon) else (None, None)
	except (TypeError, ValueError):
		return None, None


def _set_if_field(doc, fieldname, value):
	if value not in (None, "") and doc.meta.has_field(fieldname):
		doc.set(fieldname, value)

def _default_naming_series(doctype):
	field = frappe.get_meta(doctype).get_field("naming_series")
	if not field:
		return None
	options = [o.strip() for o in (field.options or "").split("\n") if o.strip()]
	return field.default or (options[0] if options else None)


def _save_signature(doctype: str, name: str, data_url: str):
	if not data_url:
		return None
	from frappe.utils.file_manager import save_file

	saved = save_file(
		fname=f"signature-{name}.png",
		content=base64.b64decode(data_url.split(",", 1)[-1]),
		dt=doctype,
		dn=name,
		is_private=1,
	)
	return saved.file_url

def _clean_address(text):
	"""Return (address without Phone/Email lines, phone, email)."""
	text = frappe.utils.strip_html((text or "").replace("<br>", "\n"))
	phone = email = None
	keep = []
	for line in text.splitlines():
		s = line.strip()
		low = s.lower()
		if low.startswith("phone:"):
			phone = s.split(":", 1)[1].strip() or None
		elif low.startswith("email:"):
			email = s.split(":", 1)[1].strip() or None
		elif low.startswith("fax:"):
			continue
		elif s:
			keep.append(s)
	return ", ".join(keep), phone, email

def _decorate(rows: list) -> list:
	"""Add customer name/phone, item name, address and visit count to task rows."""
	if not rows:
		return rows
	cust_meta = frappe.get_meta("Customer")
	geo = [f for f in ("latitude", "longitude") if frappe.db.has_column("Customer", f)]
	customers = {
		c.name: c
		for c in frappe.get_all(
			"Customer",
			filters={"name": ["in", list({r.customer for r in rows})]},
			fields=["name", "customer_name", "mobile_no", "email_id", "territory", "primary_address"] + geo,
		)
	}
	item_rows = frappe.get_all(
		"Item",
		filters={"name": ["in", list({r.item_code for r in rows})]},
		fields=["name", "item_name", "has_serial_no"],
	)
	items = {i.name: i.item_name for i in item_rows}
	serial_items = {i.name for i in item_rows if i.has_serial_no}

	visit_counts = {}
	mst_names = [r.name for r in rows if r["kind"] == "maintenance"]
	if mst_names:
		for t in frappe.get_all(
			"CRM Maintenance Visit",
			filters={"maintenance_schedule_task": ["in", mst_names], "docstatus": 1},
			pluck="maintenance_schedule_task",
		):
			visit_counts[t] = visit_counts.get(t, 0) + 1

		purposes = frappe.get_all(
			"CRM Maintenance Visit Purpose",
			filters={
				"parenttype": "CRM Maintenance Visit",
				"prevdoc_doctype": MST,
				"prevdoc_docname": ["in", mst_names],
			},
			fields=["parent", "prevdoc_docname"],
		)
		submitted = set(frappe.get_all(
			"CRM Maintenance Visit",
			filters={
				"name": ["in", [p.parent for p in purposes]],
				"docstatus": 1,
				"is_combined_visit": 1,
			},
			pluck="name",
		))
		for p in purposes:
			if p.parent in submitted:
				visit_counts[p.prevdoc_docname] = visit_counts.get(p.prevdoc_docname, 0) + 1
	
	schedule_names = list({r.get("maintenance_schedule") for r in rows if r.get("maintenance_schedule")})
	invoices, visit_pos = {}, {}
	if schedule_names:
		invoices = {
			s.name: s.sales_invoice
			for s in frappe.get_all(
				"CRM Maintenance Schedule",
				filters={"name": ["in", schedule_names]},
				fields=["name", "sales_invoice"],
			)
		}
		siblings = frappe.get_all(
			MST,
			filters={"docstatus": 1, "maintenance_schedule": ["in", schedule_names]},
			fields=["name", "maintenance_schedule"],
			order_by="scheduled_date asc, creation asc",
		)
		groups = {}
		for t in siblings:
			groups.setdefault(t.maintenance_schedule, []).append(t.name)
		for names in groups.values():
			for i, n in enumerate(names, 1):
				visit_pos[n] = (i, len(names))

	inst_invoices = {}
	installation_names = list({r.get("installation") for r in rows if r.get("installation")})
	if installation_names:
		inst_invoices = {
			i.name: i.sales_invoice
			for i in frappe.get_all(
				"Installation",
				filters={"name": ["in", installation_names]},
				fields=["name", "sales_invoice"],
			)
		}

	for r in rows:
		c = customers.get(r.customer) or {}
		r["customer_name"] = c.get("customer_name") or r.customer
		raw = r.customer_current_address or r.customer_billing_address or c.get("primary_address")
		addr, addr_phone, addr_email = _clean_address(raw)
		r["latitude"] = c.get("latitude")
		r["longitude"] = c.get("longitude")
		r["phone"] = c.get("mobile_no") or addr_phone
		r["email"] = r.get("email") or c.get("email_id") or addr_email
		r["territory"] = r.get("territory") or c.get("territory")
		r["address"] = addr
		r["billing_address"] = _clean_address(r.customer_billing_address)[0]
		r["item_name"] = items.get(r.item_code) or r.item_code
		r["has_serial_no"] = 1 if r.item_code in serial_items else 0
		r["visit_count"] = visit_counts.get(r.name, 0)
		r["sales_invoice"] = invoices.get(r.get("maintenance_schedule")) or inst_invoices.get(r.get("installation"))
		pos = visit_pos.get(r.name) if r["kind"] == "maintenance" else None
		r["visit_no"], r["visit_total"] = pos if pos else (None, None)
	return rows


def _fetch_tasks(engineers: list, date: str, include_overdue: bool) -> list:
	rows = []
	for doctype, fields in TASK_FIELDS.items():
		found = frappe.get_all(
			doctype,
			filters={
				"docstatus": 1,
				"service_engineer": ["in", engineers],
				"scheduled_date": ["<=", date] if include_overdue else date,
			},
			fields=fields,
			order_by="scheduled_date asc",
		)
		for r in found:
			is_today = getdate(r.scheduled_date) == getdate(date)
			if not is_today and r.completion_status == "Fully Completed":
				continue
			r["doctype"] = doctype
			r["kind"] = "maintenance" if doctype == MST else "installation"
			r["is_overdue"] = (not is_today) and r.completion_status != "Fully Completed"
			rows.append(r)
	return _decorate(rows)


# ------------------------------------------------------------- role / team

@frappe.whitelist()
def get_user_service_team() -> dict:
	team = _get_my_team()
	if not team:
		return {"is_service_engineer": False, "is_service_supervisor": False, "team": None, "subordinates_count": 0}
	subs = _subordinate_teams(team.name)
	return {
		"is_service_engineer": True,
		"is_service_supervisor": bool(team.is_group or subs),
		"team": team.name,
		"subordinates_count": len(subs),
	}


# ----------------------------------------------------------------- tasks


@frappe.whitelist()
def get_engineer_tasks(date: str = None, include_overdue: int = 1, engineer: str = None) -> dict:
    me = _require_team()
    date = str(getdate(date or nowdate()))
    target = engineer or me.name

    if target != me.name and target not in _subordinate_teams(me.name):
        frappe.throw(
            _("You can only view tasks of your own team"),
            frappe.PermissionError
        )

    tasks = _fetch_tasks([target], date, bool(cint(include_overdue)))

    # Count all completed maintenance tasks across all dates
    completed_maintenance = frappe.db.count(
        MST,
        filters={
            "docstatus": 1,
            "service_engineer": target,
            "completion_status": "Fully Completed"
        }
    )

    # Count all completed installation tasks across all dates
    completed_installation = frappe.db.count(
        IST,
        filters={
            "docstatus": 1,
            "service_engineer": target,
            "completion_status": "Fully Completed"
        }
    )

    # Total completed tasks across all dates
    completed = completed_maintenance + completed_installation

    # Keep pending count based on the existing task list
    pending = len(tasks) - sum(
        1 for t in tasks
        if t.completion_status == "Fully Completed"
    )

    return {
        "date": date,
        "team": target,
        "summary": {
            "assigned": len(tasks),
            "completed": completed,
            "pending": pending
        },
        "tasks": tasks
    }


def _search_tasks(rows, text):
	"""Keep rows matching customer, item, task number or serial number."""
	like = f"%{text}%"
	t = text.lower()
	cust_ids = set(frappe.get_all(
		"Customer",
		or_filters=[["name", "like", like], ["customer_name", "like", like]],
		pluck="name",
	))
	item_ids = set(frappe.get_all(
		"Item",
		or_filters=[["name", "like", like], ["item_name", "like", like]],
		pluck="name",
	))
	return [
		r for r in rows
		if r.customer in cust_ids
		or r.item_code in item_ids
		or t in (r.name or "").lower()
		or t in (r.get("serial_no") or "").lower()
	]


@frappe.whitelist()
def get_service_visits(status: str = "pending", days: int = 30, limit: int = 10,
                       search: str = None, from_date: str = None, to_date: str = None,
                       kind: str = None) -> dict:
	"""status: pending | upcoming | overdue | completed | spares"""
	me = _require_team()
	today = getdate(nowdate())

	date_filter = None
	if from_date and to_date:
		date_filter = ["between", [from_date, to_date]]
	elif from_date:
		date_filter = [">=", from_date]
	elif to_date:
		date_filter = ["<=", to_date]

	rows = []
	for doctype, fields in TASK_FIELDS.items():
		if kind == "installation" and doctype != IST:
			continue
		if kind == "maintenance" and doctype != MST:
			continue
		filters = {"docstatus": 1, "service_engineer": me.name}
		if date_filter:
			filters["scheduled_date"] = date_filter
		found = frappe.get_all(
			doctype, filters=filters, fields=fields + ["creation"], order_by="creation asc"
		)
		for r in found:
			r["doctype"] = doctype
			r["kind"] = "maintenance" if doctype == MST else "installation"
			r["is_overdue"] = getdate(r.scheduled_date) < today and r.completion_status != "Fully Completed"
			rows.append(r)

	def needs_spares(r):
		return (r.get("work_done") or "").startswith("Pending Spare Parts")

	if status == "completed":
		rows = [r for r in rows if r.completion_status == "Fully Completed"]
		rows.sort(key=lambda r: str(r.scheduled_date or ""), reverse=True)
	else:
		rows = [r for r in rows if r.completion_status != "Fully Completed"]
		if status == "spares":
			rows = [r for r in rows if needs_spares(r)]
		elif status == "upcoming":
			rows = [r for r in rows if not r["is_overdue"]]
		elif status == "overdue":
			rows = [r for r in rows if r["is_overdue"]]
		rows.sort(key=lambda r: (str(r.creation), str(r.scheduled_date or "")), reverse=True)

	if search and search.strip():
		rows = _search_tasks(rows, search.strip())

	total = len(rows)
	rows = rows[: (cint(limit) or 10)]
	return {"status": status, "tasks": _decorate(rows), "total": total}

@frappe.whitelist()
def get_my_maintenance_visits(status: str = "all", limit: int = 10, search: str = None, from_date: str = None, to_date: str = None) -> dict:
	"""status: all | partial | combined"""
	me = _require_team()
	VISIT = "CRM Maintenance Visit"
	PURPOSE = "CRM Maintenance Visit Purpose"

	my_tasks = frappe.get_all(MST, filters={"docstatus": 1, "service_engineer": me.name}, pluck="name")
	if not my_tasks:
		return {"visits": []}

	visit_names = set(frappe.get_all(
		PURPOSE,
		filters={"parenttype": VISIT, "parentfield": "purposes",
		         "prevdoc_doctype": MST, "prevdoc_docname": ["in", my_tasks]},
		pluck="parent",
	))
	visit_names |= set(frappe.get_all(
		VISIT, filters={"maintenance_schedule_task": ["in", my_tasks]}, pluck="name"
	))
	if not visit_names:
		return {"visits": []}

	filters = {"name": ["in", list(visit_names)], "docstatus": ["<", 2]}
	if status == "partial":
		filters["completion_status"] = "Partially Completed"
	elif status == "completed":
		filters["completion_status"] = "Fully Completed"
	elif status == "combined":
		filters["is_combined_visit"] = 1
	if from_date and to_date:
		filters["mntc_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["mntc_date"] = [">=", from_date]
	elif to_date:
		filters["mntc_date"] = ["<=", to_date]

	or_filters = None
	if search and search.strip():
		like = f"%{search.strip()}%"
		matched = frappe.get_all(
			PURPOSE,
			filters={"parenttype": VISIT, "parentfield": "purposes", "parent": ["in", list(visit_names)]},
			or_filters=[["item_name", "like", like], ["serial_no", "like", like], ["prevdoc_docname", "like", like]],
			pluck="parent",
		)
		or_filters = [
			["name", "like", like],
			["customer_name", "like", like],
			["name", "in", matched or ["__none__"]],
		]

	visits = frappe.get_all(
		VISIT,
		filters=filters,
		or_filters=or_filters,
		fields=["name", "customer_name", "mntc_date", "mntc_time", "completion_status",
		        "is_combined_visit", "maintenance_schedule", "maintenance_schedule_task", "docstatus"],
		order_by="mntc_date desc, creation desc",
		limit=cint(limit) or 10,
	)
	total = len(frappe.get_all(VISIT, filters=filters, or_filters=or_filters, pluck="name"))
	if not visits:
		return {"visits": [], "total": 0}

	names = [v.name for v in visits]
	purpose_fields = ["parent", "prevdoc_docname", "item_name", "serial_no"]
	if frappe.get_meta(PURPOSE).has_field("task_completion_status"):
		purpose_fields.append("task_completion_status")
	purposes = frappe.get_all(
		PURPOSE,
		filters={"parenttype": VISIT, "parentfield": "purposes", "parent": ["in", names]},
		fields=purpose_fields,
		order_by="idx asc",
	)
	mat_doctype = frappe.get_meta(VISIT).get_field("consumed_materials").options
	materials = frappe.get_all(
		mat_doctype,
		filters={"parenttype": VISIT, "parent": ["in", names]},
		fields=["parent", "item_code", "qty", "uom", "serial_no"],
		order_by="idx asc",
	)
	schedules = list({v.maintenance_schedule for v in visits if v.maintenance_schedule})
	invoices = {
		s.name: s.sales_invoice
		for s in frappe.get_all(
			"CRM Maintenance Schedule",
			filters={"name": ["in", schedules]},
			fields=["name", "sales_invoice"],
		)
	} if schedules else {}

	tasks_by, mats_by = {}, {}
	for p in purposes:
		tasks_by.setdefault(p.parent, []).append(p)
	for m in materials:
		mats_by.setdefault(m.parent, []).append(m)

	for v in visits:
		v["tasks"] = [
			{
				"task": p.prevdoc_docname or v.maintenance_schedule_task,
				"item_name": p.item_name,
				"serial_no": p.serial_no,
				"status": p.get("task_completion_status") or v.completion_status,
			}
			for p in tasks_by.get(v.name, [])
		]
		v["materials"] = mats_by.get(v.name, [])
		v["sales_invoice"] = invoices.get(v.maintenance_schedule)
	return {"status": status, "visits": visits, "total": total}

@frappe.whitelist()
def search_spare_items(txt: str = "", limit: int = 15) -> dict:
	_require_team()
	or_filters = None
	if txt:
		or_filters = [["item_code", "like", f"%{txt}%"], ["item_name", "like", f"%{txt}%"]]
	items = frappe.get_all(
		"Item",
		filters={"disabled": 0, "is_stock_item": 1},
		or_filters=or_filters,
		fields=["name as item_code", "item_name", "stock_uom", "has_serial_no", "has_batch_no"],
		order_by="item_name asc",
		limit=min(cint(limit) or 15, 30),
	)
	rates = {}
	if items:
		for p in frappe.get_all(
			"Item Price",
			filters={"item_code": ["in", [i.item_code for i in items]], "selling": 1},
			fields=["item_code", "price_list_rate"],
		):
			rates.setdefault(p.item_code, flt(p.price_list_rate))
	default_wh = _default_warehouse()
	stock = _stock_map([i.item_code for i in items], default_wh)
	for i in items:
		i["rate"] = rates.get(i.item_code, 0)
		i["stock_qty"] = stock.get(i.item_code, 0)
	return {
		"items": items,
		"default_warehouse": default_wh,
		"warehouses": frappe.get_all("Warehouse", filters={"disabled": 0, "is_group": 0}, pluck="name"),
	}

@frappe.whitelist()
def get_available_serial_nos(item_code: str, warehouse: str, search: str = None, limit: int = 50) -> dict:
	_require_team()
	if not frappe.db.get_value("Item", item_code, "has_serial_no"):
		return {"has_serial_no": 0, "serial_nos": []}

	filters = {"item_code": item_code, "warehouse": warehouse, "status": "Active"}
	if search:
		filters["name"] = ["like", f"%{search}%"]

	serials = frappe.get_all(
		"Serial No",
		filters=filters,
		pluck="name",
		order_by="creation asc",
		limit=min(cint(limit) or 50, 200),
	)
	return {"has_serial_no": 1, "serial_nos": serials}

@frappe.whitelist()
def get_spare_stock(item_code: str, warehouse: str = None) -> dict:
	_require_team()
	warehouse = warehouse or _default_warehouse()
	if not warehouse:
		return {"warehouse": None, "stock_qty": 0}
	return {
		"warehouse": warehouse,
		"stock_qty": _stock_map([item_code], warehouse).get(item_code, 0),
	}                                                         
# ------------------------------------------------------ maintenance visit

@frappe.whitelist(methods=["POST"])
def submit_maintenance_visit(data) -> dict:
	data = _parse(data)
	task = _get_my_task(MST, data.get("task"))
	draft = _find_draft_visit([task.name])
	otp_code = None
	if _otp_required():
		if not draft:
			frappe.throw(_("Please save the visit and generate the OTP first."))
		otp_code = _verify_draft_code(VISIT, draft, task.name, data.get("otp"))

	mv = frappe.get_doc(VISIT, draft or _new_draft_visit(task, data))
	work_done, status = _fill_visit(mv, data, otp_code)
	mv.save(ignore_permissions=True)
	signature_url = _save_signature(mv.doctype, mv.name, data.get("signature"))
	mv.submit()  # existing hooks: stock checks, task status, optional invoice

	if otp_code:
		frappe.cache.delete_value(_otp_lock_key(task.name))

	task.db_set("work_done", work_done, update_modified=False)
	return {"name": mv.name, "signature": signature_url, "completion_status": mv.completion_status}


@frappe.whitelist(methods=["POST"])
def submit_combined_maintenance_visit(data) -> dict:
	data = _parse(data)
	names = list(dict.fromkeys(data.get("tasks") or []))
	if len(names) < 2:
		frappe.throw(_("Select at least two tasks"))
	for n in names:
		_get_my_task(MST, n)

	otp_scope = _otp_scope(names)
	draft = _find_draft_visit(names)
	otp_code = None
	if _otp_required():
		if not draft:
			frappe.throw(_("Please save the visit and generate the OTP first."))
		otp_code = _verify_draft_code(VISIT, draft, otp_scope, data.get("otp"))

	mv = frappe.get_doc(VISIT, draft or _new_draft_combined(names))
	work_done, status = _fill_visit(mv, data, otp_code, combined=True)
	mv.save(ignore_permissions=True)
	signature_url = _save_signature(mv.doctype, mv.name, data.get("signature"))
	mv.submit()

	if otp_code:
		frappe.cache.delete_value(_otp_lock_key(otp_scope))

	for n in names:
		frappe.db.set_value(MST, n, "work_done", work_done, update_modified=False)
	return {"name": mv.name, "signature": signature_url,
	        "completion_status": status, "task_count": len(names)}


@frappe.whitelist(methods=["POST"])
def submit_installation_note(data) -> dict:
	from tq_crm_support.api.installation_task_api import make_installation_note_from_task

	data = _parse(data)
	task = _get_my_task(IST, data.get("task"))
	draft = _find_draft_note(task.name)
	otp_code = None
	if _installation_otp_required():
		if not draft:
			frappe.throw(_("Please save the installation and generate the OTP first."))
		otp_code = _verify_draft_code(NOTE, draft, task.name, data.get("otp"))

	qty = flt(data.get("installed_qty")) or flt(task.installed_qty) or 1
	task.db_set("installed_qty", qty, update_modified=False)

	note = frappe.get_doc(NOTE, draft or make_installation_note_from_task(task.name)["name"])
	qty, fully = _fill_note(note, task, data, otp_code)
	note.save(ignore_permissions=True)
	signature_url = _save_signature("Installation Note", note.name, data.get("signature"))
	note.submit()  # existing hook updates task + Installation Detail

	if otp_code:
		frappe.cache.delete_value(_otp_lock_key(task.name))

	updates = {"installed_qty": qty}
	if not task.start_date:
		updates["start_date"] = nowdate()
	if fully:
		updates["end_date"] = nowdate()
	task.db_set(updates, update_modified=False)
	return {"name": note.name, "signature": signature_url}

@frappe.whitelist()
def get_my_installations(
    limit=10, search=None, from_date=None, to_date=None, status=None
):
    limit = cint(limit) or 10
    filters = {"docstatus": 1, "owner": frappe.session.user}
    if status == "completed":
        filters["completion_status"] = "Fully Completed"
    elif status == "partial":
        filters["completion_status"] = ["!=", "Fully Completed"]
    if from_date and to_date:
        filters["inst_date"] = ["between", [from_date, to_date]]
    elif from_date:
        filters["inst_date"] = [">=", from_date]
    elif to_date:
        filters["inst_date"] = ["<=", to_date]
 
    or_filters = None
    if search and search.strip():
        like = f"%{search.strip()}%"
        parents = frappe.get_all(
            "Installation Note Item",
            or_filters=[
                ["serial_no", "like", like],
                ["item_code", "like", like],
                ["description", "like", like],
            ],
            pluck="parent",
        )
        or_filters = [
            ["name", "like", like],
            ["customer_name", "like", like],
            ["installation_task", "like", like],
            ["name", "in", parents or ["__none__"]],
        ]
 
    notes = frappe.get_all(
        "Installation Note",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name",
            "customer_name",
            "inst_date",
            "completion_status",
            "installation_task",
        ],
        order_by="inst_date desc, creation desc",
        limit=limit,
    )
    total = len(
        frappe.get_all(
            "Installation Note", filters=filters, or_filters=or_filters, pluck="name"
        )
    )
    if not notes:
        return {"installations": [], "total": 0}
 
    names = [n.name for n in notes]
 
    items = frappe.get_all(
        "Installation Note Item",
        filters={"parent": ["in", names], "parenttype": "Installation Note"},
        fields=["parent", "item_code", "description", "qty", "serial_no"],
        order_by="idx asc",
    )
 
    mat_field = frappe.get_meta("Installation Note").get_field("consumed_materials")
    materials = []
    if mat_field:
        materials = frappe.get_all(
            mat_field.options,
            filters={"parent": ["in", names], "parenttype": "Installation Note"},
            fields=["parent", "item_code", "qty", "uom", "serial_no"],
            order_by="idx asc",
        )
 
    items_by, mats_by = {}, {}
    for i in items:
        i["description"] = frappe.utils.strip_html(i.description or "").strip()
        items_by.setdefault(i.parent, []).append(i)
    for m in materials:
        mats_by.setdefault(m.parent, []).append(m)
 
    # invoice: Installation Note -> Installation Task -> Installation -> Sales Invoice
    task_names = [n.installation_task for n in notes if n.installation_task]
    inst_by_task = (
        {
            t.name: t.installation
            for t in frappe.get_all(
                "Installation Task",
                filters={"name": ["in", task_names]},
                fields=["name", "installation"],
            )
        }
        if task_names
        else {}
    )
    inst_names = [i for i in set(inst_by_task.values()) if i]
    inv_by_inst = (
        {
            i.name: i.sales_invoice
            for i in frappe.get_all(
                "Installation",
                filters={"name": ["in", inst_names]},
                fields=["name", "sales_invoice"],
            )
        }
        if inst_names
        else {}
    )
 
    for n in notes:
        n["items"] = items_by.get(n.name, [])
        n["installed_qty"] = sum(flt(i.qty) for i in n["items"])
        n["materials"] = mats_by.get(n.name, [])
        n["sales_invoice"] = inv_by_inst.get(inst_by_task.get(n.installation_task))
 
    return {"installations": notes, "total": total}
# ------------------------------------------------------------- supervisor

@frappe.whitelist()
def get_supervisor_service_dashboard(date: str = None) -> dict:
    me = _require_team()
    subs = _subordinate_teams(me.name)
    if not (me.is_group or subs):
        frappe.throw(_("Supervisor access required"), frappe.PermissionError)
 
    date = str(getdate(date or nowdate()))
    if not subs:
        return {"date": date, "totals": {"assigned": 0, "completed": 0, "pending": 0}, "engineers": []}
 
    teams = frappe.get_all("CRM Service Team", filters={"name": ["in", subs]}, fields=["name", "employee", "mobile_no"])
    emp_ids = [t.employee for t in teams if t.employee]
    employees = {
        e.name: e
        for e in frappe.get_all(
            "Employee",
            filters={"name": ["in", emp_ids]},
            fields=["name", "employee_name", "designation", "cell_number", "user_id"],
        )
    } if emp_ids else {}
    user_ids = [e.user_id for e in employees.values() if e.user_id]
    user_mobiles = {
        u.name: u.mobile_no
        for u in frappe.get_all("User", filters={"name": ["in", user_ids]}, fields=["name", "mobile_no"])
    } if user_ids else {}
 
    counts = {}
    for doctype in TASK_DOCTYPES:
        rows = frappe.get_all(
            doctype,
            filters={"docstatus": 1, "service_engineer": ["in", subs], "scheduled_date": date},
            fields=["service_engineer", "completion_status", {"COUNT": "*", "as": "cnt"}],
            group_by="service_engineer, completion_status",
        )
        for r in rows:
            c = counts.setdefault(r.service_engineer, {"assigned": 0, "completed": 0, "pending": 0})
            c["assigned"] += r.cnt
            c["completed" if r.completion_status == "Fully Completed" else "pending"] += r.cnt

        # NEW: overdue tasks from earlier dates that are not fully completed
        overdue = frappe.get_all(
            doctype,
            filters={
                "docstatus": 1,
                "service_engineer": ["in", subs],
                "scheduled_date": ["<", date],
                "completion_status": ["!=", "Fully Completed"],
            },
            fields=["service_engineer", {"COUNT": "*", "as": "cnt"}],
            group_by="service_engineer",
        )
        for r in overdue:
            c = counts.setdefault(r.service_engineer, {"assigned": 0, "completed": 0, "pending": 0})
            c["assigned"] += r.cnt
            c["pending"] += r.cnt
 
    last = {}
    if emp_ids:
        for c in frappe.get_all(
            "Employee Checkin",
            filters={"employee": ["in", emp_ids], "time": ["between", [date, date]]},
            fields=["employee", "log_type", "customer", "time"],
            order_by="time desc",
        ):
            last.setdefault(c.employee, c)
 
    engineers, totals = [], {"assigned": 0, "completed": 0, "pending": 0}
    for t in teams:
        emp = employees.get(t.employee) or {}
        c = counts.get(t.name, {"assigned": 0, "completed": 0, "pending": 0})
        ck = last.get(t.employee)
        if not ck or ck.log_type != "IN":
            status = "Off Duty"
        else:
            status = "On Site" if ck.customer else "In Transit"
        for k in totals:
            totals[k] += c[k]
        engineers.append({
            "team": t.name,
            "employee_name": emp.get("employee_name") or t.name,
            "designation": emp.get("designation"),
            "phone": t.mobile_no or emp.get("cell_number") or user_mobiles.get(emp.get("user_id")),
            "status": status,
            **c,
        })
    return {"date": date, "totals": totals, "engineers": engineers}

@frappe.whitelist(methods=["POST"])
def reassign_task(doctype: str, task: str, new_engineer: str) -> dict:
	me = _require_team()
	subs = _subordinate_teams(me.name)
	if not (me.is_group or subs):
		frappe.throw(_("Supervisor access required"), frappe.PermissionError)
	if doctype not in TASK_DOCTYPES or not frappe.db.exists(doctype, task):
		frappe.throw(_("Task not found"))

	scope = set(subs) | {me.name}
	if new_engineer not in scope:
		frappe.throw(_("You can only assign to engineers in your team"), frappe.PermissionError)

	doc = frappe.get_doc(doctype, task)
	if doc.docstatus != 1 or doc.completion_status == "Fully Completed":
		frappe.throw(_("Only open tasks can be re-assigned"))
	if doc.service_engineer and doc.service_engineer not in scope:
		frappe.throw(_("This task belongs to another team"), frappe.PermissionError)

	doc.service_engineer = new_engineer
	doc.save(ignore_permissions=True)
	return {"name": doc.name, "service_engineer": new_engineer}

@frappe.whitelist(methods=["POST"])
def save_visit_draft(data) -> dict:																#Saves a Maintenance Visit as Draft without submitting it.
	data = _parse(data)
	names = list(dict.fromkeys(data.get("tasks") or ([data.get("task")] if data.get("task") else [])))
	if not names:
		frappe.throw(_("Task is required"))
	docs = [_get_my_task(MST, n) for n in names]

	draft = _find_draft_visit(names) or (
		_new_draft_visit(docs[0], data) if len(names) == 1 else _new_draft_combined(names)
	)
	mv = frappe.get_doc(VISIT, draft)
	_fill_visit(mv, data, combined=len(names) > 1)
	mv.save(ignore_permissions=True)
	return {"name": mv.name}


@frappe.whitelist(methods=["POST"])
def save_installation_draft(data) -> dict:													#Saves an Installation Note as Draft
	from tq_crm_support.api.installation_task_api import make_installation_note_from_task

	data = _parse(data)
	task = _get_my_task(IST, data.get("task"))
	qty = flt(data.get("installed_qty")) or flt(task.installed_qty) or 1
	task.db_set("installed_qty", qty, update_modified=False)

	draft = _find_draft_note(task.name) or make_installation_note_from_task(task.name)["name"]
	note = frappe.get_doc(NOTE, draft)
	_fill_note(note, task, data, strict=False)
	note.save(ignore_permissions=True)
	return {"name": note.name}


@frappe.whitelist()
def get_draft_status(task=None, tasks=None, kind="visit") -> dict:						#Checks whether a Draft Visit or Installation Note exists and returns the saved form data.
	names = frappe.parse_json(tasks) if isinstance(tasks, str) else (tasks or [])
	names = list(dict.fromkeys(names or ([task] if task else [])))
	if not names:
		return {"draft": None, "pending": False, "remaining": 0, "form": None}

	installation = kind == "installation"
	for n in names:
		_get_my_task(IST if installation else MST, n)

	draft = _find_draft_note(names[0]) if installation else _find_draft_visit(names)
	form = None
	if draft:
		doc = frappe.get_doc(NOTE if installation else VISIT, draft)
		form = _note_form(doc) if installation else _visit_form(doc)

	remaining = _otp_remaining(_otp_scope(names))
	return {"draft": draft, "pending": remaining > 0, "remaining": remaining, "form": form}
	
def _otp_required():														#Checks whether customer confirmation OTP is enabled for Maintenance Visits.
	return cint(frappe.db.get_single_value(
		"CRM Support Settings", "customer_confirmation_for_visit"
	))

@frappe.whitelist()
def is_visit_otp_required() -> dict:
	_require_team()
	return {"required": bool(_otp_required())}

@frappe.whitelist(methods=["POST"])
def generate_visit_otp(task=None, tasks=None) -> dict:											#Generates the customer confirmation OTP for an individual or combined Maintenance Visit.
	from tq_crm_support.api.maintenance_schedule_api import generate_customer_confirmation_code

	names = frappe.parse_json(tasks) if isinstance(tasks, str) else (tasks or [])
	names = list(dict.fromkeys(names or ([task] if task else [])))
	if not names:
		frappe.throw(_("Task is required"))
	for n in names:
		_get_my_task(MST, n)

	if not _otp_required():
		return {"confirmation_required": False}

	draft = _find_draft_visit(names)
	if not draft:
		frappe.throw(_("Please save the visit first, then generate the OTP."))

	scope = _otp_scope(names)
	_check_resend_lock(scope)
	res = generate_customer_confirmation_code(draft)   # tq_crm_support writes the code on the draft
	_start_otp_window(scope)
	return _otp_response(res)


@frappe.whitelist(methods=["POST"])
def generate_installation_otp(task=None) -> dict:										#Generates the customer confirmation OTP for an Installation Note.	
	from tq_crm_support.api.installation_note_api import generate_installation_confirmation_code # adjust path

	if not task:
		frappe.throw(_("Task is required"))
	_get_my_task(IST, task)

	if not _installation_otp_required():
		return {"confirmation_required": False}

	draft = _find_draft_note(task)
	if not draft:
		frappe.throw(_("Please save the installation first, then generate the OTP."))

	_check_resend_lock(task)
	res = generate_installation_confirmation_code(draft)
	_start_otp_window(task)
	return _otp_response(res)

def _installation_otp_required():						#Checks whether Installation Note OTP verification is enabled.
	return cint(frappe.db.get_single_value(
		"CRM Support Settings", "customer_confirmation_for_installation"
	))

@frappe.whitelist()
def is_installation_otp_required() -> dict:
	_require_team()
	return {"required": bool(_installation_otp_required())}
