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
		site_counts = dict(
			frappe.db.sql(
				"""
				SELECT parent, COUNT(*)
				FROM `tabEmployee Site Tracking`
				WHERE parent IN %(parents)s
				GROUP BY parent
				""",
				{"parents": eem_names},
			)
		)
		expense_counts = dict(
			frappe.db.sql(
				"""
				SELECT parent, COUNT(*)
				FROM `tabEmployee Expense Tracking`
				WHERE parent IN %(parents)s
				GROUP BY parent
				""",
				{"parents": eem_names},
			)
		)
		# Also get list of customer/site names for search matching
		site_names_raw = frappe.db.sql(
			"""
			SELECT parent, GROUP_CONCAT(CONCAT_WS(' ', customer, site, remarks) SEPARATOR ' ') as site_keywords
			FROM `tabEmployee Site Tracking`
			WHERE parent IN %(parents)s
			GROUP BY parent
			""",
			{"parents": eem_names},
			as_dict=True,
		)
		site_keywords_map = {row.parent: (row.site_keywords or "") for row in site_names_raw}

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

	search_clause = ""
	sales_person_clause = ""
	group_clause = ""
	territory_clause = ""
	params = {"limit": limit, "limit_start": limit_start}

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
				sales_person_clause = """
				  AND name IN (
					SELECT parent 
					FROM `tabSales Team` 
					WHERE parenttype = 'Customer' 
					  AND parentfield = 'sales_team' 
					  AND sales_person IN %(sales_persons)s
				  )
				"""
				params["sales_persons"] = tuple(sales_persons)

	if search_term and search_term.strip():
		params["term"] = f"%{search_term.strip()}%"
		search_clause = """
		  AND (
			customer_name LIKE %(term)s
			OR name LIKE %(term)s
			OR territory LIKE %(term)s
			OR customer_group LIKE %(term)s
			OR mobile_no LIKE %(term)s
		  )
		"""

	if customer_group and customer_group not in ("all", "All", ""):
		params["customer_group"] = customer_group
		group_clause = " AND customer_group = %(customer_group)s"

	if territory and territory not in ("all", "All", ""):
		params["territory"] = territory
		territory_clause = " AND territory = %(territory)s"

	if user_lat is not None and user_lng is not None:
		params["user_lat"] = user_lat
		params["user_lng"] = user_lng
		query = f"""
			SELECT 
				name, customer_name, customer_group, territory, mobile_no, email_id, latitude, longitude,
				(SELECT GROUP_CONCAT(sales_person SEPARATOR ', ') FROM `tabSales Team` WHERE parent = `tabCustomer`.name AND parenttype = 'Customer' AND parentfield = 'sales_team') AS sales_person_names,
				ROUND(
					6371 * 2 * ASIN(
						SQRT(
							POWER(SIN(RADIANS(latitude - %(user_lat)s) / 2), 2) +
							COS(RADIANS(%(user_lat)s)) * COS(RADIANS(latitude)) *
							POWER(SIN(RADIANS(longitude - %(user_lng)s) / 2), 2)
						)
					),
					2
				) AS distance_km
			FROM `tabCustomer`
			WHERE disabled = 0
			  {sales_person_clause}
			  {group_clause}
			  {territory_clause}
			  {search_clause}
			ORDER BY 
				CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL AND latitude != 0 AND longitude != 0 THEN 0 ELSE 1 END,
				distance_km ASC,
				customer_name ASC
			LIMIT %(limit_start)s, %(limit)s
		"""
		return frappe.db.sql(query, params, as_dict=True)

	return frappe.db.sql(
		f"""
		SELECT 
			name, customer_name, customer_group, territory, mobile_no, email_id, latitude, longitude,
			(SELECT GROUP_CONCAT(sales_person SEPARATOR ', ') FROM `tabSales Team` WHERE parent = `tabCustomer`.name AND parenttype = 'Customer' AND parentfield = 'sales_team') AS sales_person_names,
			NULL AS distance_km
		FROM `tabCustomer`
		WHERE disabled = 0
		  {sales_person_clause}
		  {group_clause}
		  {territory_clause}
		  {search_clause}
		ORDER BY customer_name ASC
		LIMIT %(limit_start)s, %(limit)s
		""",
		params,
		as_dict=True,
	)


@frappe.whitelist()
def get_customer_detail(customer_name: str) -> dict:
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		return {}

	if not customer_name:
		return {}

	customer = frappe.db.get_value(
		"Customer",
		customer_name,
		["name", "customer_name", "customer_group", "territory", "mobile_no", "email_id", "latitude", "longitude", "customer_primary_contact", "customer_primary_address", "disabled", "creation"],
		as_dict=True,
	)
	if not customer:
		return {}

	# Sales Team
	sales_team = frappe.get_all(
		"Sales Team",
		filters={"parent": customer_name, "parenttype": "Customer", "parentfield": "sales_team"},
		fields=["sales_person", "allocated_percentage", "contact_no"],
		order_by="idx asc",
	)
	customer["sales_team"] = sales_team

	# Recent Site Visits for this customer from Executive Expense Manager
	recent_visits = frappe.db.sql(
		"""
		SELECT 
			st.name, st.parent as eem_name, st.site, st.checkin_time as visit_time, st.remarks, st.site_lat as latitude, st.site_long as longitude,
			eem.date as trip_date, eem.employee_name
		FROM `tabEmployee Site Tracking` st
		INNER JOIN `tabExecutive Expense Manager` eem ON eem.name = st.parent
		WHERE st.customer = %(customer)s
		  AND eem.docstatus != 2
		ORDER BY eem.date DESC, st.checkin_time DESC
		LIMIT 10
		""",
		{"customer": customer_name},
		as_dict=True,
	)
	customer["recent_visits"] = recent_visits

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
		site_rows = frappe.db.sql(
			"""
			SELECT 
				st.name, st.parent as eem_name, st.customer, st.site, st.checkin_time as visit_time, 
				st.remarks, st.site_lat, st.site_long, st.actual_distance, st.location_name
			FROM `tabEmployee Site Tracking` st
			WHERE st.parent IN %(parents)s
			ORDER BY st.checkin_time ASC, st.idx ASC
			""",
			{"parents": eem_names},
			as_dict=True,
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






