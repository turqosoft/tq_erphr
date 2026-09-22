import frappe
from frappe import _
from frappe.boot import load_translations
from frappe.query_builder.functions import Coalesce, Count, Sum, Avg, IfNull


@frappe.whitelist()
def get_current_user_info() -> dict:
	current_user = frappe.session.user
	user = frappe.db.get_value(
		"User", current_user, ["name", "first_name", "full_name", "user_image"], as_dict=True
	)
	if user:
		user["roles"] = frappe.get_roles(current_user)
	return user or {}


@frappe.whitelist(methods=["POST"])
def change_user_password(old_password: str, new_password: str) -> dict:
	"""
	Change the password for the current authenticated user.
	Verifies old password, updates to new password, and invalidates all other active sessions.
	"""
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Please log in to change your password."), frappe.PermissionError)

	if not old_password or not new_password:
		frappe.throw(_("Current password and new password are required."))

	if len(new_password) < 6:
		frappe.throw(_("New password must be at least 6 characters long."))

	if old_password == new_password:
		frappe.throw(_("New password cannot be the same as your current password."))

	try:
		from frappe.core.doctype.user.user import check_password, _update_password
		check_password(current_user, old_password)
	except frappe.AuthenticationError:
		frappe.throw(_("Current password is incorrect."))
	except Exception as e:
		frappe.throw(_("Authentication failed: {0}").format(str(e)))

	from frappe.core.doctype.user.user import _update_password
	from frappe.sessions import clear_sessions

	_update_password(current_user, new_password, logout_all_sessions=True)
	clear_sessions(user=current_user, keep_current=True, force=True)

	return {
		"status": "success",
		"message": _("Password changed successfully. All other devices have been logged out.")
	}



@frappe.whitelist()
def get_current_employee_info() -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return None

	employee = frappe.db.get_value(
		"Employee",
		{"user_id": current_user, "status": "Active"},
		[
			"name",
			"first_name",
			"last_name",
			"employee_name",
			"designation",
			"department",
			"company",
			"reports_to",
			"user_id",
			"image",
			"date_of_joining",
			"cell_number",
			"company_email",
			"personal_email",
		],
		as_dict=True,
	)
	if not employee:
		return None

	# User is considered a Sales Person ONLY if their Employee ID or Name is linked to an enabled record in the Sales Person DocType
	sales_person = frappe.db.get_value(
		"Sales Person",
		{"employee": employee["name"], "enabled": 1},
		["name", "sales_person_name"],
		as_dict=True,
	)
	if not sales_person and employee.get("employee_name"):
		sales_person = frappe.db.get_value(
			"Sales Person",
			{"sales_person_name": employee["employee_name"], "enabled": 1},
			["name", "sales_person_name"],
			as_dict=True,
		)

	employee["is_sales_person"] = bool(sales_person)
	employee["sales_person_name"] = sales_person["name"] if sales_person else None

	# Fetch Company Name and Logo
	company_name = employee.get("company") or frappe.defaults.get_global_default("company")
	company_doc = None
	if company_name:
		company_doc = frappe.db.get_value(
			"Company",
			company_name,
			["name", "company_name", "company_logo"],
			as_dict=True,
		)

	employee["company_name"] = (company_doc.get("company_name") if company_doc else company_name) or "Total Quality"
	employee["company_logo"] = company_doc.get("company_logo") if company_doc else None
	if not employee.get("company") and company_name:
		employee["company"] = company_name

	website_app_logo = frappe.db.get_single_value("Website Settings", "app_logo") if frappe.db.exists("DocType", "Website Settings") else None
	employee["app_logo"] = employee["company_logo"] or website_app_logo

	view_all_pref = frappe.defaults.get_user_default("mobibiz_view_all_customers", current_user)
	employee["view_all_customers"] = bool(view_all_pref and str(view_all_pref).lower() in ("1", "true", "yes"))

	# Check Supervisor status & Subordinates count
	subordinates = get_subordinate_sales_persons(current_user)
	employee["is_supervisor"] = bool(subordinates)
	employee["subordinates_count"] = len(subordinates)

	return employee


@frappe.whitelist(methods=["POST"])
def update_user_customer_view_preference(view_all: bool = False) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.PermissionError)

	val = "1" if (view_all is True or str(view_all).lower() in ("1", "true", "yes")) else "0"
	frappe.defaults.set_user_default("mobibiz_view_all_customers", val, current_user)
	return {"status": "success", "view_all_customers": val == "1"}


@frappe.whitelist(methods=["POST"], allow_guest=True)
def get_context_for_dev():
	if not frappe.conf.developer_mode:
		frappe.throw(_("This method is only meant for developer mode"))
	return get_boot()


def get_boot():
	bootinfo = frappe._dict(
		{
			"site_name": frappe.local.site,
			"push_relay_server_url": frappe.conf.get("push_relay_server_url") or "",
			"default_route": "/mobibiz",
		}
	)

	bootinfo.lang = frappe.local.lang
	load_translations(bootinfo)

	return bootinfo


@frappe.whitelist()
def get_employee_checkin_status() -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return {}

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		return {"employee": None}

	today = frappe.utils.today()
	checkins = frappe.get_all(
		"Employee Checkin",
		filters={"employee": employee},
		fields=["name", "employee", "employee_name", "log_type", "time", "latitude", "longitude", "device_id"],
		order_by="time desc",
		limit=20,
	)

	last_checkin = checkins[0] if checkins else None
	next_action = "OUT" if (last_checkin and last_checkin.log_type == "IN") else "IN"

	today_checkins = []
	for c in checkins:
		if not c.time:
			continue
		t_str = str(c.time)
		if t_str.startswith(str(today)):
			today_checkins.append(c)

	return {
		"employee": employee,
		"last_checkin": last_checkin,
		"next_action": next_action,
		"today_checkins": today_checkins,
	}


@frappe.whitelist()
def add_employee_checkin(log_type: str = "IN", latitude=None, longitude=None, device_id: str = None, remarks: str = None) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		frappe.throw(_("No active employee found for current user"))

	if log_type not in ("IN", "OUT"):
		log_type = "IN"

	lat = 0.0
	lon = 0.0
	try:
		if latitude is not None and str(latitude).strip() != "":
			lat = float(latitude)
	except (ValueError, TypeError):
		lat = 0.0

	try:
		if longitude is not None and str(longitude).strip() != "":
			lon = float(longitude)
	except (ValueError, TypeError):
		lon = 0.0

	if not lat or not lon or (lat == 0.0 and lon == 0.0):
		frappe.throw(_("GPS Location is mandatory for attendance check-in / check-out. Please enable location on your device."))

	# If no device_id was passed, infer from HTTP request user agent
	if not device_id:
		user_agent = frappe.request.headers.get("User-Agent", "Unknown Device") if hasattr(frappe, "request") and frappe.request else "Mobile PWA"
		device_id = user_agent[:140]

	checkin_data = {
		"doctype": "Employee Checkin",
		"employee": employee,
		"log_type": log_type,
		"time": frappe.utils.now_datetime(),
		"device_id": (device_id or "Mobile PWA")[:140],
		"latitude": lat,
		"longitude": lon,
	}

	doc = frappe.get_doc(checkin_data)
	if remarks and hasattr(doc, "remarks"):
		doc.remarks = str(remarks)[:250]

	doc.insert(ignore_permissions=True)
	return doc.as_dict()


@frappe.whitelist()
def get_employee_checkin_history(limit: int = 10, limit_start: int = 0) -> list:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return []

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		return []

	try:
		limit = int(limit)
		limit_start = int(limit_start)
	except (ValueError, TypeError):
		limit = 10
		limit_start = 0

	return frappe.get_all(
		"Employee Checkin",
		filters={"employee": employee},
		fields=["name", "employee", "employee_name", "log_type", "time", "latitude", "longitude", "device_id"],
		order_by="time desc",
		limit=limit,
		limit_start=limit_start,
	)


def get_or_create_today_eem_doc(employee: str, date=None):
	if not date:
		date = frappe.utils.today()

	eem_name = frappe.db.get_value(
		"Executive Expense Manager",
		{"employee": employee, "date": date, "docstatus": ["!=", 2]},
		"name",
		order_by="creation desc",
	)
	if eem_name:
		doc = frappe.get_doc("Executive Expense Manager", eem_name)
		if doc.docstatus != 2:
			return doc

	hr_settings = frappe.get_single("TQ ERPHRHR Settings") if frappe.db.exists("DocType", "TQ ERPHRHR Settings") else None
	travel_expense_type = hr_settings.travel_expense_type if hr_settings else "Travel"
	rate_per_km = hr_settings.two_wheeler_rate_per_km if hr_settings else 4.0

	doc = frappe.get_doc(
		{
			"doctype": "Executive Expense Manager",
			"employee": employee,
			"date": date,
			"vehicle_type": "Two Wheeler",
			"rate_per_km": rate_per_km,
			"travel_expense_type": travel_expense_type,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


@frappe.whitelist()
def get_today_eem() -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return {}

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		return {"employee": None}

	checkin_status = get_employee_checkin_status()
	is_checked_in = bool(checkin_status.get("next_action") == "OUT")

	today_date = frappe.utils.today()
	eem_name = frappe.db.get_value(
		"Executive Expense Manager",
		{"employee": employee, "date": today_date, "docstatus": ["!=", 2]},
		"name",
		order_by="creation desc",
	)

	rates = {"Two Wheeler": 4.0, "Four Wheeler": 8.0, "Other": 5.0}
	if frappe.db.exists("DocType", "TQ ERPHRHR Settings"):
		hr_settings = frappe.get_single("TQ ERPHRHR Settings")
		if hr_settings.two_wheeler_rate_per_km:
			rates["Two Wheeler"] = float(hr_settings.two_wheeler_rate_per_km)
		if hr_settings.four_wheeler_rate_per_km:
			rates["Four Wheeler"] = float(hr_settings.four_wheeler_rate_per_km)
		if hr_settings.other_rate_per_km:
			rates["Other"] = float(hr_settings.other_rate_per_km)

	if not eem_name:
		return {
			"employee": employee,
			"trip_status": "NOT_STARTED",
			"eem": None,
			"doc": None,
			"rates": rates,
			"is_checked_in": is_checked_in,
		}

	eem_doc = frappe.get_doc("Executive Expense Manager", eem_name)
	if eem_doc.docstatus == 2:
		return {
			"employee": employee,
			"trip_status": "NOT_STARTED",
			"eem": None,
			"doc": None,
			"rates": rates,
			"is_checked_in": is_checked_in,
		}

	# Ensure rates & totals are refreshed
	if not eem_doc.rate_per_km or eem_doc.rate_per_km <= 0:
		eem_doc.add_travel_expensetype_and_rate()

	has_updated_sites = False
	for row in eem_doc.employee_site_tracking:
		if (not row.site_lat or row.site_lat == 0.0) and row.checkin_lat:
			row.site_lat = row.checkin_lat
			has_updated_sites = True
		if (not row.site_long or row.site_long == 0.0) and row.checkin_long:
			row.site_long = row.checkin_long
			has_updated_sites = True

	eem_doc.calculate_odometer_distance()
	eem_doc.calculate_site_distances()
	eem_doc.calculate_totals()

	if has_updated_sites and eem_doc.docstatus == 0:
		eem_doc.save(ignore_permissions=True)
	
	# Determine status
	if eem_doc.docstatus == 1:
		trip_status = "COMPLETED"
	elif eem_doc.start_time or (eem_doc.start_lat and eem_doc.start_long) or eem_doc.start_odometerkm or (eem_doc.employee_site_tracking and len(eem_doc.employee_site_tracking) > 0):
		if eem_doc.end_time and eem_doc.end_odometerkm and eem_doc.end_odometerkm > 0:
			trip_status = "READY_TO_SUBMIT"
		else:
			trip_status = "IN_PROGRESS"
	else:
		trip_status = "NOT_STARTED"

	eem_dict = eem_doc.as_dict()
	return {
		"employee": employee,
		"trip_status": trip_status,
		"eem": eem_dict,
		"doc": eem_dict,
		"rates": rates,
		"is_checked_in": is_checked_in,
	}


def validate_sales_person(employee_name: str):
	sp = frappe.db.get_value("Sales Person", {"employee": employee_name, "enabled": 1}, "name")
	if not sp:
		emp_name = frappe.db.get_value("Employee", employee_name, "employee_name")
		if emp_name:
			sp = frappe.db.get_value("Sales Person", {"sales_person_name": emp_name, "enabled": 1}, "name")
	if not sp:
		frappe.throw(_("Access Restricted: Only active Sales Persons mapped in the Sales Person Master can access the Executive Expense Manager."), frappe.PermissionError)
	return sp


@frappe.whitelist()
def start_eem_trip(vehicle_type: str = "Two Wheeler", start_odometerkm: float = 0, start_lat=None, start_long=None) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		frappe.throw(_("No active employee found for current user"))

	validate_sales_person(employee)

	lat = 0.0
	lon = 0.0
	try:
		if start_lat is not None and str(start_lat).strip() != "":
			lat = float(start_lat)
	except (ValueError, TypeError):
		lat = 0.0

	try:
		if start_long is not None and str(start_long).strip() != "":
			lon = float(start_long)
	except (ValueError, TypeError):
		lon = 0.0

	if not lat or not lon or (lat == 0.0 and lon == 0.0):
		frappe.throw(_("GPS Location is mandatory to start your travel day. Please enable location on your device."))

	today_date = frappe.utils.today()
	eem_doc = get_or_create_today_eem_doc(employee, today_date)

	odo = 0.0
	try:
		if start_odometerkm is not None and str(start_odometerkm).strip() != "":
			odo = float(start_odometerkm)
	except (ValueError, TypeError):
		odo = 0.0

	eem_doc.vehicle_type = vehicle_type or "Two Wheeler"
	eem_doc.start_odometerkm = odo
	eem_doc.start_time = frappe.utils.now_datetime().time()
	eem_doc.start_lat = lat
	eem_doc.start_long = lon
	eem_doc.add_travel_expensetype_and_rate()
	eem_doc.save(ignore_permissions=True)

	return get_today_eem()


@frappe.whitelist()
def add_eem_site_visit(
	customer: str = None,
	site: str = None,
	remarks: str = None,
	latitude=None,
	longitude=None,
	actual_distance: float = 0,
	address: str = None,
	contact_number: str = None,
	category: str = None,
) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		frappe.throw(_("No active employee found for current user"))

	lat = 0.0
	lon = 0.0
	try:
		if latitude is not None and str(latitude).strip() != "":
			lat = float(latitude)
	except (ValueError, TypeError):
		lat = 0.0

	try:
		if longitude is not None and str(longitude).strip() != "":
			lon = float(longitude)
	except (ValueError, TypeError):
		lon = 0.0

	if not lat or not lon or (lat == 0.0 and lon == 0.0):
		frappe.throw(_("GPS Location is mandatory to record a site visit. Please enable location on your device."))

	today_date = frappe.utils.today()
	eem_doc = get_or_create_today_eem_doc(employee, today_date)

	dist = 0.0
	try:
		if actual_distance is not None and str(actual_distance).strip() != "":
			dist = float(actual_distance)
	except (ValueError, TypeError):
		dist = 0.0

	now_time = frappe.utils.now_datetime().time()

	eem_doc.append(
		"employee_site_tracking",
		{
			"customer": customer or "",
			"site": site or "",
			"location_name": site or (customer or "Site Location"),
			"checkin_time": now_time,
			"checkin_lat": lat,
			"checkin_long": lon,
			"site_lat": lat,
			"site_long": lon,
			"actual_distance": dist,
			"address": address or "",
			"contact_number": contact_number or "",
			"category": category or "",
			"remarks": remarks or "",
		},
	)

	eem_doc.calculate_site_distances()
	eem_doc.calculate_totals()
	eem_doc.build_route_polyline()
	eem_doc.fill_location_names()
	eem_doc.save(ignore_permissions=True)

	return get_today_eem()


@frappe.whitelist()
def add_eem_expense(expense_type: str = "Food", amount: float = 0, description: str = None) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		frappe.throw(_("No active employee found for current user"))

	today_date = frappe.utils.today()
	eem_doc = get_or_create_today_eem_doc(employee, today_date)

	amt = 0.0
	try:
		if amount is not None and str(amount).strip() != "":
			amt = float(amount)
	except (ValueError, TypeError):
		amt = 0.0

	if amt <= 0:
		frappe.throw(_("Please enter a valid expense amount greater than 0."))

	eem_doc.append(
		"employee_expense_tracking",
		{
			"expense_type": expense_type or "Others",
			"amount": amt,
			"description": description or "",
		},
	)

	eem_doc.calculate_totals()
	eem_doc.save(ignore_permissions=True)

	return get_today_eem()


@frappe.whitelist()
def end_eem_trip(end_odometerkm: float = 0, end_lat=None, end_long=None, actual_end_distance: float = 0, end_narration: str = None, submit_doc: bool = False) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		frappe.throw(_("No active employee found for current user"))

	lat = 0.0
	lon = 0.0
	try:
		if end_lat is not None and str(end_lat).strip() != "":
			lat = float(end_lat)
	except (ValueError, TypeError):
		lat = 0.0

	try:
		if end_long is not None and str(end_long).strip() != "":
			lon = float(end_long)
	except (ValueError, TypeError):
		lon = 0.0

	if not lat or not lon or (lat == 0.0 and lon == 0.0):
		frappe.throw(_("GPS Location is mandatory to complete your travel day. Please enable location on your device."))

	today_date = frappe.utils.today()
	eem_doc = get_or_create_today_eem_doc(employee, today_date)

	odo = 0.0
	try:
		if end_odometerkm is not None and str(end_odometerkm).strip() != "":
			odo = float(end_odometerkm)
	except (ValueError, TypeError):
		odo = 0.0

	dist = 0.0
	try:
		if actual_end_distance is not None and str(actual_end_distance).strip() != "":
			dist = float(actual_end_distance)
	except (ValueError, TypeError):
		dist = 0.0

	eem_doc.end_time = frappe.utils.now_datetime().time()
	eem_doc.end_odometerkm = odo
	eem_doc.end_lat = lat
	eem_doc.end_long = lon
	eem_doc.actual_end_distance = dist
	if end_narration:
		eem_doc.end_narration = str(end_narration)[:200]

	eem_doc.calculate_odometer_distance()
	eem_doc.calculate_site_distances()
	eem_doc.calculate_totals()
	eem_doc.build_route_polyline()
	eem_doc.fill_location_names()

	eem_doc.save(ignore_permissions=True)

	if str(submit_doc).lower() in ("true", "1") and eem_doc.docstatus == 0:
		eem_doc.submit()

	return get_today_eem()


@frappe.whitelist()
def get_eem_history(limit: int = 10, limit_start: int = 0, from_date: str = None, to_date: str = None, vehicle_type: str = None) -> list:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return []

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee and current_user == "Administrator":
		sales_person_emp = frappe.db.get_value("Sales Person", {"enabled": 1}, "employee")
		employee = sales_person_emp or frappe.db.get_value("Employee", {"status": "Active"}, "name")

	if not employee:
		return []

	filters = {"employee": employee, "docstatus": ["!=", 2]}
	if from_date and to_date:
		filters["date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["date"] = [">=", from_date]
	elif to_date:
		filters["date"] = ["<=", to_date]

	if vehicle_type and vehicle_type not in ("all", "All", ""):
		filters["vehicle_type"] = vehicle_type

	try:
		limit_num = int(limit) if limit else 10
		limit_start_num = int(limit_start) if limit_start else 0
	except (ValueError, TypeError):
		limit_num = 10
		limit_start_num = 0

	records = frappe.get_all(
		"Executive Expense Manager",
		filters=filters,
		fields=[
			"name",
			"date",
			"vehicle_type",
			"rate_per_km",
			"start_time",
			"end_time",
			"start_odometerkm",
			"end_odometerkm",
			"remarks",
			"end_narration",
			"total_distance",
			"odometer_distance",
			"total_travel_expense",
			"total_other_expenses",
			"total_expense",
			"expense_claim_status",
			"docstatus",
			"creation",
			"modified",
		],
		order_by="date desc, creation desc",
		limit=limit_num,
		limit_start=limit_start_num,
	)

	eem_names = [r.name for r in records]
	if eem_names:
		site_rows = frappe.get_all(
			"Employee Site Tracking",
			filters={"parent": ["in", eem_names]},
			fields=["parent", "customer", "site", "remarks"],
		)
		site_counts = {}
		site_keywords_map = {}
		for row in site_rows:
			parent = row.parent
			site_counts[parent] = site_counts.get(parent, 0) + 1
			kw = f"{row.customer or ''} {row.site or ''} {row.remarks or ''}".strip()
			if kw:
				if parent in site_keywords_map:
					site_keywords_map[parent] += f" {kw}"
				else:
					site_keywords_map[parent] = kw

		expense_rows = frappe.get_all(
			"Employee Expense Tracking",
			filters={"parent": ["in", eem_names]},
			fields=["parent", "name"],
		)
		expense_counts = {}
		for row in expense_rows:
			parent = row.parent
			expense_counts[parent] = expense_counts.get(parent, 0) + 1

		for r in records:
			r["sites_count"] = site_counts.get(r.name, 0)
			r["expenses_count"] = expense_counts.get(r.name, 0)
			r["site_keywords"] = site_keywords_map.get(r.name, "")
	else:
		for r in records:
			r["sites_count"] = 0
			r["expenses_count"] = 0
			r["site_keywords"] = ""

	return records


@frappe.whitelist()
def get_eem_detail(eem_name: str) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee and current_user == "Administrator":
		sales_person_emp = frappe.db.get_value("Sales Person", {"enabled": 1}, "employee")
		employee = sales_person_emp or frappe.db.get_value("Employee", {"status": "Active"}, "name")

	if not employee:
		frappe.throw(_("No active employee profile linked to your account."))

	if not eem_name or not frappe.db.exists("Executive Expense Manager", eem_name):
		frappe.throw(_("Executive Expense Manager record not found."))

	doc = frappe.get_doc("Executive Expense Manager", eem_name)
	if doc.employee != employee and not frappe.has_permission("Executive Expense Manager", "read", doc) and current_user != "Administrator":
		frappe.throw(_("You do not have permission to view this record."), frappe.PermissionError)

	# Check for linked Expense Claim (if any)
	claim_info = None
	linked_claim = frappe.db.get_value(
		"Expense Claim Detail",
		{"executive_expense_manager": doc.name},
		"parent"
	)
	if linked_claim:
		claim_info = frappe.db.get_value(
			"Expense Claim",
			linked_claim,
			["name", "status", "approval_status", "total_claimed_amount", "total_sanctioned_amount", "posting_date"],
			as_dict=True
		)

	return {
		"doc": doc.as_dict(),
		"linked_expense_claim": claim_info,
	}


@frappe.whitelist()
def get_expense_claim_types() -> list:
	return frappe.get_all("Expense Claim Type", fields=["name"], order_by="name asc")


@frappe.whitelist()
def get_customers_list(
	search_term: str = None,
	limit: int = 20,
	limit_start: int = 0,
	latitude: float = None,
	longitude: float = None,
	customer_group: str = None,
	territory: str = None,
) -> list:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return []

	try:
		limit = min(int(limit), 100) if limit else 20
		limit_start = int(limit_start) if limit_start else 0
	except (ValueError, TypeError):
		limit = 20
		limit_start = 0

	user_lat = None
	user_lng = None
	if latitude is not None and longitude is not None:
		try:
			user_lat = float(latitude)
			user_lng = float(longitude)
			if not (-90 <= user_lat <= 90 and -180 <= user_lng <= 180 and not (user_lat == 0 and user_lng == 0)):
				user_lat = None
				user_lng = None
		except (ValueError, TypeError):
			user_lat = None
			user_lng = None

	view_all_pref = frappe.defaults.get_user_default("mobibiz_view_all_customers", current_user)
	can_view_all = bool(view_all_pref and str(view_all_pref).lower() in ("1", "true", "yes"))

	filters = {"disabled": 0}

	if not can_view_all:
		employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, ["name", "employee_name"], as_dict=True)
		sales_person = None
		if employee:
			sales_person = frappe.db.get_value("Sales Person", {"employee": employee["name"], "enabled": 1}, "name")
			if not sales_person and employee.get("employee_name"):
				sales_person = frappe.db.get_value("Sales Person", {"sales_person_name": employee["employee_name"], "enabled": 1}, "name")

		if sales_person:
			sp_row = frappe.db.get_value("Sales Person", sales_person, ["lft", "rgt"], as_dict=True)
			if sp_row and sp_row.lft and sp_row.rgt:
				sales_persons = frappe.get_all(
					"Sales Person",
					filters={"lft": (">=", sp_row.lft), "rgt": ("<=", sp_row.rgt), "enabled": 1},
					pluck="name",
				)
			else:
				sales_persons = [sales_person]

			if sales_persons:
				allowed_customer_names = frappe.get_all(
					"Sales Team",
					filters={
						"parenttype": "Customer",
						"parentfield": "sales_team",
						"sales_person": ["in", sales_persons],
					},
					pluck="parent",
				)
				if allowed_customer_names:
					filters["name"] = ["in", allowed_customer_names]
				else:
					filters["name"] = ["in", ["__NON_EXISTENT__"]]

	if customer_group and customer_group not in ("all", "All", ""):
		filters["customer_group"] = customer_group

	if territory and territory not in ("all", "All", ""):
		filters["territory"] = territory

	or_filters = None
	if search_term and search_term.strip():
		st = f"%{search_term.strip()}%"
		or_filters = [
			["customer_name", "like", st],
			["name", "like", st],
			["territory", "like", st],
			["customer_group", "like", st],
			["mobile_no", "like", st],
		]

	has_lat_col = bool(frappe.db.has_column("Customer", "latitude"))
	has_lng_col = bool(frappe.db.has_column("Customer", "longitude"))

	fields = [
		"name",
		"customer_name",
		"customer_group",
		"territory",
		"mobile_no",
		"email_id",
	]
	if has_lat_col:
		fields.append("latitude")
	if has_lng_col:
		fields.append("longitude")

	import math

	def haversine_km(lat1, lon1, lat2, lon2):
		if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
			return None
		try:
			lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
			if (lat1 == 0 and lon1 == 0) or (lat2 == 0 and lon2 == 0):
				return None
			r = 6371.0
			dlat = math.radians(lat2 - lat1)
			dlon = math.radians(lon2 - lon1)
			a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
			c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
			return round(r * c, 2)
		except Exception:
			return None

	if user_lat is not None and user_lng is not None and has_lat_col and has_lng_col:
		all_customers = frappe.get_all(
			"Customer",
			filters=filters,
			or_filters=or_filters,
			fields=fields,
		)
		for c in all_customers:
			c["distance_km"] = haversine_km(user_lat, user_lng, c.get("latitude"), c.get("longitude"))

		def sort_key(c):
			has_coords = 0 if (c.get("latitude") and c.get("longitude") and float(c.get("latitude") or 0) != 0 and float(c.get("longitude") or 0) != 0) else 1
			dist = c.get("distance_km") if c.get("distance_km") is not None else 999999.0
			return (has_coords, dist, c.get("customer_name") or "")

		all_customers.sort(key=sort_key)
		customers = all_customers[limit_start : limit_start + limit]
	else:
		customers = frappe.get_all(
			"Customer",
			filters=filters,
			or_filters=or_filters,
			fields=fields,
			order_by="customer_name asc",
			limit_start=limit_start,
			limit_page_length=limit,
		)
		for c in customers:
			c["distance_km"] = None

	customer_names = [c["name"] for c in customers]
	if customer_names:
		sales_teams = frappe.get_all(
			"Sales Team",
			filters={"parent": ["in", customer_names], "parenttype": "Customer", "parentfield": "sales_team"},
			fields=["parent", "sales_person"],
		)
		sp_map = {}
		for st_row in sales_teams:
			sp_map.setdefault(st_row.parent, []).append(st_row.sales_person)

		invoice_stats = frappe.get_all(
			"Sales Invoice",
			filters={"docstatus": 1, "customer": ["in", customer_names]},
			fields=["customer", "sum(grand_total) as total_billed", "sum(outstanding_amount) as total_unpaid"],
			group_by="customer",
		)
		stats_map = {row.customer: row for row in invoice_stats}

		for c in customers:
			c["sales_person_names"] = ", ".join(sp_map.get(c["name"], []))
			if "latitude" not in c:
				c["latitude"] = None
			if "longitude" not in c:
				c["longitude"] = None
			st = stats_map.get(c["name"])
			c["total_billed"] = float(st.get("total_billed") or 0.0) if st else 0.0
			c["total_unpaid"] = float(st.get("total_unpaid") or 0.0) if st else 0.0
	else:
		for c in customers:
			c["total_billed"] = 0.0
			c["total_unpaid"] = 0.0
			c["sales_person_names"] = ""

	return customers


@frappe.whitelist()
def get_customer_detail(customer_name: str) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return {}

	if not customer_name:
		return {}

	customer_fields = [
		"name", "customer_name", "customer_group", "territory", "mobile_no", "email_id",
		"customer_primary_contact", "customer_primary_address", "disabled", "creation"
	]
	if frappe.db.has_column("Customer", "latitude"):
		customer_fields.append("latitude")
	if frappe.db.has_column("Customer", "longitude"):
		customer_fields.append("longitude")

	customer = frappe.db.get_value(
		"Customer",
		customer_name,
		customer_fields,
		as_dict=True,
	)
	if not customer:
		return {}

	if "latitude" not in customer:
		customer["latitude"] = None
	if "longitude" not in customer:
		customer["longitude"] = None

	# Sales Team
	sales_team = frappe.get_all(
		"Sales Team",
		filters={"parent": customer_name, "parenttype": "Customer", "parentfield": "sales_team"},
		fields=["sales_person", "allocated_percentage", "contact_no"],
		order_by="idx asc",
	)
	customer["sales_team"] = sales_team

	# Primary Address Text
	customer["address_text"] = ""
	if customer.get("customer_primary_address"):
		try:
			addr = frappe.db.get_value(
				"Address",
				customer["customer_primary_address"],
				["address_line1", "address_line2", "city", "state", "pincode", "address_title"],
				as_dict=True,
			)
			if addr:
				parts = [addr.get(k) for k in ["address_line1", "address_line2", "city", "state", "pincode"] if addr.get(k)]
				customer["address_text"] = ", ".join(parts)
		except Exception:
			customer["address_text"] = ""

	# Billing & Unpaid stats
	inv_stats = frappe.get_all(
		"Sales Invoice",
		filters={"docstatus": 1, "customer": customer_name},
		fields=["sum(grand_total) as total_billed", "sum(outstanding_amount) as total_unpaid"],
	)
	if inv_stats and inv_stats[0].get("total_billed") is not None:
		customer["total_billed"] = float(inv_stats[0].get("total_billed") or 0.0)
		customer["total_unpaid"] = float(inv_stats[0].get("total_unpaid") or 0.0)
	else:
		customer["total_billed"] = 0.0
		customer["total_unpaid"] = 0.0

	try:
		from erpnext.accounts.party import get_dashboard_info
		customer["dashboard_info"] = get_dashboard_info("Customer", customer_name)
	except Exception:
		customer["dashboard_info"] = None

	# Recent Site Visits for this customer from Executive Expense Manager
	st_doctype = frappe.qb.DocType("Employee Site Tracking")
	eem_doctype = frappe.qb.DocType("Executive Expense Manager")
	recent_visits_query = (
		frappe.qb.from_(st_doctype)
		.inner_join(eem_doctype)
		.on(eem_doctype.name == st_doctype.parent)
		.select(
			st_doctype.name,
			st_doctype.parent.as_("eem_name"),
			st_doctype.site,
			st_doctype.checkin_time.as_("visit_time"),
			st_doctype.remarks,
			st_doctype.site_lat.as_("latitude"),
			st_doctype.site_long.as_("longitude"),
			st_doctype.address,
			st_doctype.contact_number,
			st_doctype.category,
			eem_doctype.date.as_("trip_date"),
			eem_doctype.employee_name,
		)
		.where((st_doctype.customer == customer_name) & (eem_doctype.docstatus != 2))
		.orderby(eem_doctype.date, order=frappe.qb.desc)
		.orderby(st_doctype.checkin_time, order=frappe.qb.desc)
		.limit(10)
	)
	customer["recent_visits"] = recent_visits_query.run(as_dict=True)

	return customer


def get_subordinate_sales_persons(current_user: str = None) -> list:
	"""
	Returns all Sales Persons reporting to the current user directly or via Sales Person tree / Employee reports_to.
	If user is Administrator, System Manager, HR Manager or Sales Manager, includes all sales persons in the company.
	"""
	if not current_user:
		current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return []

	# Get linked employee
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": current_user, "status": "Active"},
		["name", "employee_name"],
		as_dict=True,
	)

	sales_person = None
	if employee:
		sales_person = frappe.db.get_value(
			"Sales Person",
			{"employee": employee["name"], "enabled": 1},
			"name",
		)
		if not sales_person:
			sales_person = frappe.db.get_value(
				"Sales Person",
				{"sales_person_name": employee["employee_name"], "enabled": 1},
				"name",
			)

	subordinate_sp_names = set()

	# 1. Check direct & indirect children in Sales Person hierarchy
	if sales_person:
		children = frappe.get_all(
			"Sales Person",
			filters={"parent_sales_person": sales_person, "enabled": 1},
			pluck="name",
		)
		for ch in children:
			subordinate_sp_names.add(ch)
			sub_children = frappe.get_all(
				"Sales Person",
				filters={"parent_sales_person": ch, "enabled": 1},
				pluck="name",
			)
			for sc in sub_children:
				subordinate_sp_names.add(sc)

	# 2. Check Employees reporting to this employee who are Sales Persons
	if employee:
		reporting_employees = frappe.get_all(
			"Employee",
			filters={"reports_to": employee["name"], "status": "Active"},
			pluck="name",
		)
		if reporting_employees:
			rep_sps = frappe.get_all(
				"Sales Person",
				filters={"employee": ["in", reporting_employees], "enabled": 1},
				pluck="name",
			)
			for sp in rep_sps:
				subordinate_sp_names.add(sp)

	# 3. If Administrator, System Manager, HR Manager, or Sales Manager, include all non-group sales persons
	roles = set(frappe.get_roles(current_user))
	is_admin_or_manager = current_user == "Administrator" or bool(roles.intersection({"System Manager", "HR Manager", "Sales Manager", "Sales Master Manager"}))
	if is_admin_or_manager and not subordinate_sp_names:
		all_sps = frappe.get_all("Sales Person", filters={"enabled": 1, "is_group": 0}, pluck="name")
		for sp in all_sps:
			if sp != sales_person:
				subordinate_sp_names.add(sp)

	if not subordinate_sp_names:
		return []

	records = frappe.get_all(
		"Sales Person",
		filters={"name": ["in", list(subordinate_sp_names)], "enabled": 1},
		fields=["name", "sales_person_name", "employee", "parent_sales_person"],
		order_by="sales_person_name asc",
	)

	emp_ids = [r.employee for r in records if r.employee]
	emp_map = {}
	if emp_ids:
		emp_list = frappe.get_all(
			"Employee",
			filters={"name": ["in", emp_ids]},
			fields=["name", "employee_name", "designation", "department", "image", "cell_number", "company_email"],
		)
		emp_map = {e.name: e for e in emp_list}

	res = []
	for r in records:
		emp_data = emp_map.get(r.employee, {})
		res.append({
			"sales_person": r.name,
			"sales_person_name": r.sales_person_name or r.name,
			"employee": r.employee or emp_data.get("name"),
			"employee_name": emp_data.get("employee_name") or r.sales_person_name or r.name,
			"designation": emp_data.get("designation") or "Sales Executive",
			"department": emp_data.get("department") or "Sales",
			"image": emp_data.get("image"),
			"cell_number": emp_data.get("cell_number"),
			"company_email": emp_data.get("company_email"),
			"parent_sales_person": r.parent_sales_person,
		})

	return res


@frappe.whitelist()
def get_supervisor_eem_dashboard(
	date: str = None,
	sales_person: str = None,
	status: str = None,
	limit: int = 20,
	limit_start: int = 0,
) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.PermissionError)

	subordinates = get_subordinate_sales_persons(current_user)
	if not subordinates:
		return {
			"is_supervisor": False,
			"target_date": date or frappe.utils.today(),
			"summary": {
				"total_executives": 0,
				"active_now_count": 0,
				"completed_count": 0,
				"not_started_count": 0,
				"total_distance_km": 0.0,
				"total_claims_amount": 0.0,
				"total_site_visits": 0,
			},
			"team_members": [],
			"trips": [],
		}

	target_date = date or frappe.utils.today()

	emp_to_sub = {s["employee"]: s for s in subordinates if s.get("employee")}
	sp_to_sub = {s["sales_person"]: s for s in subordinates}

	target_employees = list(emp_to_sub.keys())
	if sales_person and sales_person not in ("all", "All", ""):
		if sales_person in sp_to_sub and sp_to_sub[sales_person].get("employee"):
			target_employees = [sp_to_sub[sales_person]["employee"]]
		elif sales_person in emp_to_sub:
			target_employees = [sales_person]

	eem_filters = {
		"employee": ["in", target_employees] if target_employees else [""],
		"date": target_date,
		"docstatus": ["!=", 2],
	}

	eem_records = frappe.get_all(
		"Executive Expense Manager",
		filters=eem_filters,
		fields=[
			"name",
			"employee",
			"employee_name",
			"date",
			"vehicle_type",
			"rate_per_km",
			"start_time",
			"end_time",
			"start_odometerkm",
			"end_odometerkm",
			"start_lat",
			"start_long",
			"end_lat",
			"end_long",
			"remarks",
			"end_narration",
			"total_distance",
			"odometer_distance",
			"total_travel_expense",
			"total_other_expenses",
			"total_expense",
			"expense_claim_status",
			"docstatus",
			"creation",
			"modified",
		],
		order_by="start_time desc, modified desc",
	)

	eem_by_emp = {r.employee: r for r in eem_records}

	eem_names = [r.name for r in eem_records]
	site_visits_by_eem = {}
	if eem_names:
		site_rows = frappe.get_all(
			"Employee Site Tracking",
			filters={"parent": ["in", eem_names]},
			fields=[
				"name",
				"parent as eem_name",
				"customer",
				"site",
				"checkin_time as visit_time",
				"remarks",
				"site_lat",
				"site_long",
				"actual_distance",
				"location_name",
				"address",
				"contact_number",
				"category",
			],
			order_by="checkin_time asc, idx asc",
		)
		for sr in site_rows:
			site_visits_by_eem.setdefault(sr["eem_name"], []).append(sr)

	trips = []
	active_now_count = 0
	completed_count = 0
	not_started_count = 0
	total_dist = 0.0
	total_claims = 0.0
	total_sites = 0

	active_subs = subordinates
	if sales_person and sales_person not in ("all", "All", ""):
		active_subs = [s for s in subordinates if s["sales_person"] == sales_person or s.get("employee") == sales_person]

	for sub in active_subs:
		emp_id = sub.get("employee")
		eem_doc = eem_by_emp.get(emp_id)

		if eem_doc:
			sites = site_visits_by_eem.get(eem_doc.name, [])
			dist_val = float(eem_doc.total_distance or 0.0)
			claim_val = float(eem_doc.total_expense or 0.0)
			total_dist += dist_val
			total_claims += claim_val
			total_sites += len(sites)

			has_started = bool(
				eem_doc.get("start_time")
				or (eem_doc.get("start_lat") and float(eem_doc.get("start_lat") or 0) != 0.0)
				or (eem_doc.get("start_odometerkm") and float(eem_doc.get("start_odometerkm") or 0) > 0)
				or (sites and len(sites) > 0)
			)
			has_ended = bool(
				eem_doc.get("end_odometerkm")
				and float(eem_doc.get("end_odometerkm") or 0) > 0
				and float(eem_doc.get("end_odometerkm") or 0) >= float(eem_doc.get("start_odometerkm") or 0)
			)

			if eem_doc.docstatus == 1:
				trip_status = "COMPLETED"
				completed_count += 1
			elif has_ended:
				trip_status = "READY_TO_SUBMIT"
				completed_count += 1
			elif has_started:
				trip_status = "IN_PROGRESS"
				active_now_count += 1
			else:
				trip_status = "NOT_STARTED"
				not_started_count += 1

			trip_item = {
				"eem_name": eem_doc.name,
				"sales_person": sub["sales_person"],
				"sales_person_name": sub["sales_person_name"],
				"employee": emp_id,
				"employee_name": sub["employee_name"],
				"designation": sub["designation"],
				"image": sub["image"],
				"cell_number": sub["cell_number"],
				"company_email": sub["company_email"],
				"date": str(eem_doc.date),
				"trip_status": trip_status,
				"vehicle_type": eem_doc.vehicle_type,
				"rate_per_km": eem_doc.rate_per_km,
				"start_time": str(eem_doc.start_time) if eem_doc.start_time else None,
				"end_time": str(eem_doc.end_time) if (has_ended or eem_doc.docstatus == 1) and eem_doc.end_time else None,
				"start_odometerkm": eem_doc.start_odometerkm,
				"end_odometerkm": eem_doc.end_odometerkm,
				"start_lat": eem_doc.get("start_lat"),
				"start_long": eem_doc.get("start_long"),
				"end_lat": eem_doc.get("end_lat"),
				"end_long": eem_doc.get("end_long"),
				"remarks": eem_doc.get("remarks"),
				"end_narration": eem_doc.get("end_narration"),
				"total_distance": dist_val,
				"total_travel_expense": float(eem_doc.total_travel_expense or 0.0),
				"total_other_expenses": float(eem_doc.total_other_expenses or 0.0),
				"total_expense": claim_val,
				"docstatus": eem_doc.docstatus,
				"site_visits": sites,
				"site_visits_count": len(sites),
			}
			trips.append(trip_item)
			sub["today_trip_status"] = trip_status
			sub["today_eem_name"] = eem_doc.name
		else:
			not_started_count += 1
			sub["today_trip_status"] = "NOT_STARTED"
			sub["today_eem_name"] = None
			trips.append({
				"eem_name": None,
				"sales_person": sub["sales_person"],
				"sales_person_name": sub["sales_person_name"],
				"employee": emp_id,
				"employee_name": sub["employee_name"],
				"designation": sub["designation"],
				"image": sub["image"],
				"cell_number": sub["cell_number"],
				"company_email": sub["company_email"],
				"date": str(target_date),
				"trip_status": "NOT_STARTED",
				"vehicle_type": "-",
				"rate_per_km": 0,
				"start_time": None,
				"end_time": None,
				"start_odometerkm": 0,
				"end_odometerkm": 0,
				"total_distance": 0,
				"total_expense": 0,
				"docstatus": 0,
				"site_visits": [],
				"site_visits_count": 0,
			})

	if status and status not in ("all", "All", ""):
		if status == "ACTIVE":
			trips = [t for t in trips if t["trip_status"] == "IN_PROGRESS"]
		elif status == "COMPLETED":
			trips = [t for t in trips if t["trip_status"] in ("COMPLETED", "READY_TO_SUBMIT")]
		elif status == "NOT_STARTED":
			trips = [t for t in trips if t["trip_status"] == "NOT_STARTED"]

	return {
		"is_supervisor": True,
		"target_date": str(target_date),
		"summary": {
			"total_executives": len(subordinates),
			"active_now_count": active_now_count,
			"completed_count": completed_count,
			"not_started_count": not_started_count,
			"total_distance_km": round(total_dist, 2),
			"total_claims_amount": round(total_claims, 2),
			"total_site_visits": total_sites,
		},
		"team_members": subordinates,
		"trips": trips,
	}


@frappe.whitelist()
def get_supervisor_team_eem_detail(eem_name: str) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.PermissionError)

	if not eem_name:
		return {}

	doc = frappe.get_doc("Executive Expense Manager", eem_name)
	doc_dict = doc.as_dict()

	if doc.employee:
		emp = frappe.db.get_value(
			"Employee",
			doc.employee,
			["name", "employee_name", "designation", "image", "cell_number", "company_email"],
			as_dict=True,
		)
		doc_dict["employee_details"] = emp

	has_started = bool(
		doc.start_time
		or (doc.start_lat and float(doc.start_lat or 0) != 0.0)
		or (doc.start_odometerkm and float(doc.start_odometerkm or 0) > 0)
		or (doc.employee_site_tracking and len(doc.employee_site_tracking) > 0)
	)
	has_ended = bool(
		doc.end_odometerkm
		and float(doc.end_odometerkm or 0) > 0
		and float(doc.end_odometerkm or 0) >= float(doc.start_odometerkm or 0)
	)

	if doc.docstatus == 1:
		doc_dict["trip_status"] = "COMPLETED"
	elif has_ended:
		doc_dict["trip_status"] = "READY_TO_SUBMIT"
	elif has_started:
		doc_dict["trip_status"] = "IN_PROGRESS"
	else:
		doc_dict["trip_status"] = "NOT_STARTED"

	return doc_dict


@frappe.whitelist()
def get_stock_items(
	search_term: str = None,
	warehouse: str = None,
	item_group: str = None,
	limit: int = 20,
	limit_start: int = 0,
	sort_by: str = "actual_qty",
	sort_order: str = "desc",
) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return {"items": [], "total_count": 0}

	try:
		limit = min(int(limit), 100) if limit else 20
		limit_start = int(limit_start) if limit_start else 0
	except (ValueError, TypeError):
		limit = 20
		limit_start = 0

	item_tbl = frappe.qb.DocType("Item")
	bin_tbl = frappe.qb.DocType("Bin")

	query = (
		frappe.qb.from_(item_tbl)
		.left_join(bin_tbl)
		.on(bin_tbl.item_code == item_tbl.name)
		.select(
			item_tbl.name.as_("item_code"),
			item_tbl.item_name,
			item_tbl.item_group,
			item_tbl.stock_uom,
			item_tbl.brand,
			item_tbl.image,
			item_tbl.has_batch_no,
			item_tbl.has_serial_no,
			Coalesce(Sum(bin_tbl.actual_qty), 0).as_("actual_qty"),
			Coalesce(Sum(bin_tbl.projected_qty), 0).as_("projected_qty"),
			Coalesce(Sum(bin_tbl.reserved_qty), 0).as_("reserved_qty"),
			Coalesce(Sum(bin_tbl.reserved_stock), 0).as_("reserved_stock"),
			Coalesce(Avg(bin_tbl.valuation_rate), 0).as_("valuation_rate"),
			Count(bin_tbl.warehouse).distinct().as_("warehouse_count"),
		)
		.where(item_tbl.disabled == 0)
		.groupby(item_tbl.name)
	)

	if search_term and search_term.strip():
		st = f"%{search_term.strip()}%"
		query = query.where(
			(item_tbl.name.like(st))
			| (item_tbl.item_name.like(st))
			| (item_tbl.description.like(st))
			| (item_tbl.brand.like(st))
		)

	if item_group and item_group not in ("all", "All", ""):
		query = query.where(item_tbl.item_group == item_group)

	if warehouse and warehouse not in ("all", "All", ""):
		query = query.where(bin_tbl.warehouse == warehouse)

	# Execute items query
	items = (
		query.orderby(Coalesce(Sum(bin_tbl.actual_qty), 0), order=frappe.qb.desc)
		.orderby(item_tbl.item_name, order=frappe.qb.asc)
		.offset(limit_start)
		.limit(limit)
		.run(as_dict=True)
	)

	item_codes = [it["item_code"] for it in items]
	bin_map = {}
	in_transit_map = {}
	if item_codes:
		bin_rows = frappe.get_all(
			"Bin",
			filters={"item_code": ["in", item_codes]},
			fields=[
				"name as bin_name",
				"item_code",
				"warehouse",
				"actual_qty",
				"projected_qty",
				"reserved_qty",
				"reserved_stock",
				"valuation_rate",
			],
			order_by="actual_qty desc, warehouse asc",
		)
		for br in bin_rows:
			br["actual_qty"] = float(br.get("actual_qty") or 0.0)
			br["projected_qty"] = float(br.get("projected_qty") or 0.0)
			br["reserved_qty"] = float(br.get("reserved_qty") or 0.0)
			br["reserved_stock"] = float(br.get("reserved_stock") or 0.0)
			br["valuation_rate"] = float(br.get("valuation_rate") or 0.0)
			bin_map.setdefault(br["item_code"], []).append(br)

		# Fetch In-Transit details from mobibiz serv or fallback query
		try:
			from tqerp_mobibiz_serv.api import get_in_transit_item_details
			transit_resp = get_in_transit_item_details()
			if transit_resp and isinstance(transit_resp, dict) and transit_resp.get("data"):
				for tr in transit_resp["data"]:
					it_code = tr.get("item")
					if it_code in item_codes:
						in_transit_map.setdefault(it_code, []).append(tr)
		except Exception:
			pii = frappe.qb.DocType("Purchase Invoice Item")
			pi = frappe.qb.DocType("Purchase Invoice")
			pending_qty = pii.qty - Coalesce(pii.received_qty, 0)
			transit_q = (
				frappe.qb.from_(pii)
				.inner_join(pi).on(pii.parent == pi.name)
				.select(
					pii.item_code.as_("item"),
					pii.item_name,
					pending_qty.as_("qty"),
					pi.name.as_("purchase_invoice_number"),
					pi.posting_date.as_("date_of_purchase"),
					pi.supplier,
					pi.supplier_name,
				)
				.where(pi.docstatus == 1)
				.where(pi.is_return == 0)
				.where(Coalesce(pi.update_stock, 0) == 0)
				.where(pending_qty > 0)
				.where(pii.item_code.isin(item_codes))
				.orderby(pi.posting_date, order=frappe.qb.desc)
			)
			for tr in transit_q.run(as_dict=True):
				in_transit_map.setdefault(tr.get("item"), []).append(tr)

	for item in items:
		item["actual_qty"] = float(item.get("actual_qty") or 0.0)
		item["projected_qty"] = float(item.get("projected_qty") or 0.0)
		item["reserved_qty"] = float(item.get("reserved_qty") or 0.0)
		item["reserved_stock"] = float(item.get("reserved_stock") or 0.0)
		item["valuation_rate"] = float(item.get("valuation_rate") or 0.0)
		item["stock_value"] = round(item["actual_qty"] * item["valuation_rate"], 2)
		item["warehouses"] = bin_map.get(item["item_code"], [])
		item["warehouse_count"] = len(item["warehouses"])
		
		item_transits = in_transit_map.get(item["item_code"], [])
		item["in_transit_records"] = item_transits
		item["in_transit_qty"] = float(sum(float(t.get("qty") or 0.0) for t in item_transits))

	# Count query
	count_q = (
		frappe.qb.from_(item_tbl)
		.left_join(bin_tbl)
		.on(bin_tbl.item_code == item_tbl.name)
		.select(Count(item_tbl.name).distinct().as_("cnt"))
		.where(item_tbl.disabled == 0)
	)
	if search_term and search_term.strip():
		st = f"%{search_term.strip()}%"
		count_q = count_q.where(
			(item_tbl.name.like(st))
			| (item_tbl.item_name.like(st))
			| (item_tbl.description.like(st))
			| (item_tbl.brand.like(st))
		)
	if item_group and item_group not in ("all", "All", ""):
		count_q = count_q.where(item_tbl.item_group == item_group)
	if warehouse and warehouse not in ("all", "All", ""):
		count_q = count_q.where(bin_tbl.warehouse == warehouse)

	cnt_res = count_q.run(as_dict=True)
	total_count = int(cnt_res[0].cnt or 0) if cnt_res else len(items)

	return {
		"items": items,
		"total_count": total_count,
	}


@frappe.whitelist()
def get_stock_meta_filters() -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return {"warehouses": [], "item_groups": [], "stats": {}}

	warehouses = frappe.get_all(
		"Bin",
		filters={"warehouse": ["is", "set"]},
		fields=["distinct warehouse as name"],
		order_by="warehouse asc",
	)

	item_groups = frappe.get_all(
		"Item",
		filters={"disabled": 0, "item_group": ["is", "set"]},
		fields=["distinct item_group as name"],
		order_by="item_group asc",
	)

	bin_stats = frappe.get_all(
		"Bin",
		fields=[
			"count(distinct item_code) as total_items",
			"count(distinct warehouse) as total_warehouses",
			"sum(actual_qty) as total_actual_qty",
			"sum(projected_qty) as total_available_qty",
		],
	)
	in_stock_bins = frappe.get_all(
		"Bin",
		filters={"actual_qty": [">", 0]},
		fields=["count(distinct item_code) as in_stock_items"],
	)

	total_in_transit = 0.0
	try:
		from tqerp_mobibiz_serv.api import get_in_transit_item_details
		transit_resp = get_in_transit_item_details()
		if transit_resp and isinstance(transit_resp, dict) and transit_resp.get("data"):
			total_in_transit = float(sum(float(r.get("qty") or 0.0) for r in transit_resp["data"]))
	except Exception:
		pass

	bs = bin_stats[0] if bin_stats else {}
	is_cnt = in_stock_bins[0].get("in_stock_items") if in_stock_bins else 0

	stats = {
		"total_items": int(bs.get("total_items") or 0),
		"total_warehouses": int(bs.get("total_warehouses") or 0),
		"total_actual_qty": float(bs.get("total_actual_qty") or 0.0),
		"total_available_qty": float(bs.get("total_available_qty") or 0.0),
		"total_in_transit_qty": float(total_in_transit),
		"in_stock_items": int(is_cnt or 0),
	}

	return {
		"warehouses": [w.name for w in warehouses if w.name],
		"item_groups": [g.name for g in item_groups if g.name],
		"stats": stats,
	}







