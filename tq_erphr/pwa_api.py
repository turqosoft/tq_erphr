import frappe
from frappe import _
from frappe.boot import load_translations


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

	return employee


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
def get_employee_checkin_history(limit: int = 20) -> list:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return []

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		return []

	return frappe.get_all(
		"Employee Checkin",
		filters={"employee": employee},
		fields=["name", "employee", "employee_name", "log_type", "time", "latitude", "longitude", "device_id"],
		order_by="time desc",
		limit=limit,
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
def add_eem_site_visit(customer: str = None, site: str = None, remarks: str = None, latitude=None, longitude=None, actual_distance: float = 0) -> dict:
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
def get_eem_history(limit: int = 20) -> list:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return []

	employee = frappe.db.get_value("Employee", {"user_id": current_user, "status": "Active"}, "name")
	if not employee:
		return []

	records = frappe.get_all(
		"Executive Expense Manager",
		filters={"employee": employee},
		fields=[
			"name",
			"date",
			"vehicle_type",
			"total_distance",
			"odometer_distance",
			"total_travel_expense",
			"total_other_expenses",
			"total_expense",
			"expense_claim_status",
			"docstatus",
		],
		order_by="date desc, creation desc",
		limit=limit,
	)
	return records


@frappe.whitelist()
def get_expense_claim_types() -> list:
	return frappe.get_all("Expense Claim Type", fields=["name"], order_by="name asc")


@frappe.whitelist()
def get_customers_list(search_term: str = None, limit: int = 50) -> list:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return []

	filters = {}
	if search_term and search_term.strip():
		filters["customer_name"] = ["like", f"%{search_term.strip()}%"]

	return frappe.get_all(
		"Customer",
		filters=filters,
		fields=["name", "customer_name", "customer_group", "territory", "mobile_no", "email_id"],
		order_by="customer_name asc",
		limit=limit,
	)
