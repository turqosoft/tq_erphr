import base64

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
		frappe.throw(_("You can only view tasks of your own team"), frappe.PermissionError)

	tasks = _fetch_tasks([target], date, bool(cint(include_overdue)))
	completed = sum(1 for t in tasks if t.completion_status == "Fully Completed")
	return {
		"date": date,
		"team": target,
		"summary": {"assigned": len(tasks), "completed": completed, "pending": len(tasks) - completed},
		"tasks": tasks,
	}


@frappe.whitelist()
def get_service_visits(status: str = "pending", days: int = 30, limit: int = 20) -> dict:
	"""status: pending | completed | spares  (last N days plus the next 7)."""
	me = _require_team()
	today = getdate(nowdate())
	start, end = add_days(today, -cint(days)), add_days(today, 7)
	rows = []
	for doctype, fields in TASK_FIELDS.items():
		found = frappe.get_all(
			doctype,
			# filters={"docstatus": 1, "service_engineer": me.name, "scheduled_date": ["between", [start, end]]},
					
		filters={
			"docstatus": 1,"service_engineer": me.name,},
			fields=fields + ["creation"],
			order_by="creation asc",
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
		rows = rows[: cint(limit) or 20]
	elif status == "spares":
		rows = [r for r in rows if r.completion_status != "Fully Completed" and needs_spares(r)]
	else:
		rows = [r for r in rows if r.completion_status != "Fully Completed"]
	if status != "completed":
		rows.sort(key=lambda r: (str(r.creation), str(r.scheduled_date or "")), reverse=True)
	return {"status": status, "tasks": _decorate(rows)}

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
	for i in items:
		i["rate"] = rates.get(i.item_code, 0)
	return {
		"items": items,
		"default_warehouse": frappe.db.get_single_value("Stock Settings", "default_warehouse"),
		"warehouses": frappe.get_all("Warehouse", filters={"disabled": 0, "is_group": 0}, pluck="name"),
	}


# ------------------------------------------------------ maintenance visit

@frappe.whitelist(methods=["POST"])
def submit_maintenance_visit(data) -> dict:
	from tq_crm_support.api.maintenance_schedule_api import make_maintenance_visit_from_task

	data = _parse(data)
	task = _get_my_task(MST, data.get("task"))

	resolution = data.get("resolution_status") or "Fully Resolved"
	fully = resolution == "Fully Resolved"
	note = (data.get("work_done") or "").strip()
	work_done = f"{resolution}: {note}" if note else resolution
	lat, lon = _coords(data)

	mv = _as_admin(make_maintenance_visit_from_task, task.name)
	mv.company = (
		mv.company
		or frappe.db.get_value("CRM Maintenance Schedule", task.maintenance_schedule, "company")
		or frappe.defaults.get_global_default("company")
	)
	mv.mntc_date = nowdate()
	mv.mntc_time = nowtime()
	mv.completion_status = "Fully Completed" if fully else "Partially Completed"
	mv.customer_feedback = data.get("feedback")
	_set_if_field(mv, "checkin_lat", lat)
	_set_if_field(mv, "checkin_long", lon)
	_set_if_field(mv, "resolution_status", resolution)
	if mv.purposes:
		mv.purposes[0].work_done = work_done

	default_wh = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	for m in data.get("materials") or []:
		qty = flt(m.get("qty"))
		if qty <= 0:
			continue
		rate = flt(m.get("rate"))
		mv.append("consumed_materials", {
			"item_code": m.get("item_code"),
			"warehouse": m.get("warehouse") or default_wh,
			"qty": qty,
			"uom": m.get("uom"),
			"rate": rate,
			"amount": qty * rate,
			"billing_type": m.get("billing_type") or "Free",
			"serial_no": m.get("serial_no"),
			"batch_no": m.get("batch_no"),
		})

	mv.insert(ignore_permissions=True)
	signature_url = _save_signature(mv.doctype, mv.name, data.get("signature"))
	mv.submit()  # existing hooks: stock checks, task status, optional invoice

	task.db_set("work_done", work_done, update_modified=False)
	return {"name": mv.name, "signature": signature_url, "completion_status": mv.completion_status}


# -------------------------------------------------------- installation note

@frappe.whitelist(methods=["POST"])
def submit_installation_note(data) -> dict:
	from tq_crm_support.api.installation_task_api import make_installation_note_from_task

	data = _parse(data)
	task = _get_my_task(IST, data.get("task"))
	fully = (data.get("completion_status") or "Fully Completed") == "Fully Completed"
	qty = flt(data.get("installed_qty")) or flt(task.installed_qty) or 1
	task.db_set("installed_qty", qty, update_modified=False)
	lat, lon = _coords(data)

	lines = [f"{'[x]' if c.get('checked') else '[ ]'} {c.get('label')}" for c in (data.get("checklist") or [])]
	if data.get("handover_notes"):
		lines += ["", data["handover_notes"]]

	note = frappe.get_doc("Installation Note", make_installation_note_from_task(task.name)["name"])
	note.inst_date = nowdate()
	note.inst_time = nowtime()
	note.completion_status = "Fully Completed" if fully else "Partially Completed"
	note.remarks = "\n".join(lines)
	_set_if_field(note, "checkin_lat", lat)
	_set_if_field(note, "checkin_long", lon)
	if note.items:
		note.items[0].qty = qty
		has_serial = frappe.db.get_value("Item", task.item_code, "has_serial_no")
		if has_serial:
			if data.get("serial_no"):
				note.items[0].serial_no = data["serial_no"]
		else:
			note.items[0].serial_no = None

	note.save(ignore_permissions=True)
	signature_url = _save_signature("Installation Note", note.name, data.get("signature"))
	note.submit()  # existing hook updates task + Installation Detail

	updates = {"installed_qty": qty}
	if not task.start_date:
		updates["start_date"] = nowdate()
	if fully:
		updates["end_date"] = nowdate()
	task.db_set(updates, update_modified=False)
	return {"name": note.name, "signature": signature_url}


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
			fields=["service_engineer", "completion_status", "count(name) as cnt"],
			group_by="service_engineer, completion_status",
		)
		for r in rows:
			c = counts.setdefault(r.service_engineer, {"assigned": 0, "completed": 0, "pending": 0})
			c["assigned"] += r.cnt
			c["completed" if r.completion_status == "Fully Completed" else "pending"] += r.cnt

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