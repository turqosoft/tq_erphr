import base64
import json

import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime

from tq_erphr.face_recognition import (
	FaceRecognitionError,
	cosine_similarity,
	decode_image,
	extract_embedding,
	parse_embedding,
)


@frappe.whitelist()
def get_employee_geofencing():
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": frappe.session.user},
		"name",
	)
	if not employee:
		return {
			"employee": None,
			"has_geofencing": False,
			"geofences": [],
			"enabled_geofences": [],
		}

	employee_groups = frappe.get_all(
		"Employee Group Table",
		filters={"employee": employee, "parenttype": "Employee Group"},
		fields=["parent"],
		distinct=True,
	)
	group_names = [row.parent for row in employee_groups if row.parent]

	geofences = []
	if group_names:
		for group in frappe.get_all(
			"Employee Group",
			filters={"name": ["in", group_names]},
			fields=[
				"name",
				"enable_geofencing",
				"geofencing_latitude",
				"geofencing_longitude",
				"geofencing_radius",
			],
		):
			radius = cint(group.geofencing_radius)
			geofences.append(
				{
					"employee_group": group.name,
					"enabled": bool(cint(group.enable_geofencing)),
					"latitude": flt(group.geofencing_latitude),
					"longitude": flt(group.geofencing_longitude),
					"radius": radius,
					"radius_meters": radius,
				}
			)

	enabled_geofences = [item for item in geofences if item["enabled"]]
	return {
		"employee": employee,
		"has_geofencing": bool(enabled_geofences),
		"geofences": geofences,
		"enabled_geofences": enabled_geofences,
	}


def _get_logged_in_employee():
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": frappe.session.user},
		"name",
	)
	if not employee:
		frappe.throw(_("No Employee record is linked to the logged-in user"))
	return employee


def _get_enrollment_employee(employee=None):
	if not employee:
		return _get_logged_in_employee()

	if "System Manager" not in frappe.get_roles():
		frappe.throw(_("Only a System Manager can enroll a face for another employee"))
	if not frappe.db.exists("Employee", employee):
		frappe.throw(_("Invalid employee"))
	return employee


def _get_selfie_image(file_url=None, image_base64=None):
	image_base64 = image_base64 or frappe.form_dict.get("image_base64")
	image_base64 = image_base64 or frappe.form_dict.get("image")
	image_base64 = image_base64 or frappe.form_dict.get("selfie_base64")
	file_url = file_url or frappe.form_dict.get("file_url")
	image_bytes = None

	if frappe.request and getattr(frappe.request, "files", None):
		uploaded_file = frappe.request.files.get("selfie") or frappe.request.files.get("file")
		if uploaded_file:
			image_bytes = uploaded_file.read()
			if len(image_bytes) > 10 * 1024 * 1024:
				frappe.throw(_("The selfie must be smaller than 10 MB"))
			image_base64 = base64.b64encode(image_bytes).decode("ascii")

	if file_url:
		file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
		if not file_name:
			frappe.throw(_("The uploaded selfie file was not found"))

		file_doc = frappe.get_doc("File", file_name)
		if (
			file_doc.owner != frappe.session.user
			and "System Manager" not in frappe.get_roles()
		):
			frappe.throw(_("You cannot use this selfie file"))

		with open(file_doc.get_full_path(), "rb") as selfie:
			image_bytes = selfie.read(10 * 1024 * 1024 + 1)
		if len(image_bytes) > 10 * 1024 * 1024:
			frappe.throw(_("The selfie must be smaller than 10 MB"))
		image_base64 = base64.b64encode(image_bytes).decode("ascii")

	if not image_base64:
		frappe.throw(_("No selfie image was provided"))
	if len(image_base64) > 14 * 1024 * 1024:
		frappe.throw(_("The selfie must be smaller than 10 MB"))
	if image_bytes is None:
		try:
			encoded_image = image_base64.split(",", 1)[-1]
			image_bytes = base64.b64decode(encoded_image, validate=True)
		except (ValueError, base64.binascii.Error):
			frappe.throw(_("The selfie image is not valid base64"))
	if len(image_bytes) > 10 * 1024 * 1024:
		frappe.throw(_("The selfie must be smaller than 10 MB"))

	try:
		return decode_image(image_base64), file_url, image_bytes
	except FaceRecognitionError as exc:
		frappe.throw(str(exc))


def _create_face_verification_log(
	employee,
	matched=False,
	similarity=None,
	threshold=None,
	status="Error",
	failure_reason=None,
):
	frappe.get_doc(
		{
			"doctype": "Face Verification Log",
			"employee": employee,
			"scanner_user": frappe.session.user,
			"matched": 1 if matched else 0,
			"verification_time": now_datetime(),
			"similarity": similarity,
			"threshold": threshold,
			"status": status,
			"failure_reason": (failure_reason or "")[:140],
		}
	).insert(ignore_permissions=True)


@frappe.whitelist()
def enroll_employee_face(image_base64=None, file_url=None, employee=None):
	employee = _get_enrollment_employee(employee)
	image, resolved_file_url, _image_bytes = _get_selfie_image(file_url, image_base64)

	try:
		embedding = extract_embedding(image)
	except FaceRecognitionError as exc:
		frappe.throw(str(exc))

	profile_name = frappe.db.exists("Employee Face Profile", {"employee": employee})
	if profile_name:
		profile = frappe.get_doc("Employee Face Profile", profile_name)
	else:
		profile = frappe.get_doc(
			{"doctype": "Employee Face Profile", "employee": employee}
		)

	profile.embedding = json.dumps(embedding)
	profile.embedding_provider = "InsightFace"
	profile.embedding_version = "buffalo_l"
	profile.enrollment_status = "Enrolled"
	profile.is_active = 1
	profile.failure_count = 0
	if resolved_file_url:
		profile.enrollment_photo = resolved_file_url

	if profile.is_new():
		profile.insert(ignore_permissions=True)
	else:
		profile.save(ignore_permissions=True)

	return {
		"enrolled": True,
		"employee": employee,
		"embedding_provider": "InsightFace",
		"embedding_version": "buffalo_l",
		"message": "Employee face profile enrolled successfully",
	}


def verify_face_for_employee(employee, image):
	profile_name = frappe.db.exists(
		"Employee Face Profile",
		{
			"employee": employee,
			"is_active": 1,
			"enrollment_status": "Enrolled",
		},
	)
	if not profile_name:
		_create_face_verification_log(
			employee,
			status="No Profile",
			failure_reason="No active employee face profile",
		)
		return {
			"matched": False,
			"status": "No Profile",
			"message": "No active face profile is enrolled",
		}

	profile = frappe.get_doc("Employee Face Profile", profile_name)
	threshold = flt(profile.threshold) or 0.4

	try:
		captured_embedding = extract_embedding(image)
		stored_embedding = parse_embedding(profile.embedding)
		similarity = cosine_similarity(stored_embedding, captured_embedding)
	except FaceRecognitionError as exc:
		message = str(exc)
		status = "Multiple Faces" if "exactly one face" in message else "Face Not Detected"
		_create_face_verification_log(
			employee,
			threshold=threshold,
			status=status,
			failure_reason=message,
		)
		return {"matched": False, "status": status, "message": message}

	matched = similarity >= threshold
	status = "Matched" if matched else "No Match"
	if matched:
		profile.last_verified = now_datetime()
		profile.failure_count = 0
	else:
		profile.failure_count = cint(profile.failure_count) + 1
	profile.save(ignore_permissions=True)

	_create_face_verification_log(
		employee,
		matched=matched,
		similarity=round(similarity, 6),
		threshold=threshold,
		status=status,
		failure_reason=(
			None if matched else "Captured face did not meet the similarity threshold"
		),
	)

	return {
		"matched": matched,
		"status": status,
		"similarity": round(similarity, 6),
		"threshold": threshold,
		"message": "Face matched" if matched else "Face did not match",
	}


@frappe.whitelist()
def verify_employee_face(image_base64=None, file_url=None):
	employee = _get_logged_in_employee()
	image, _resolved_file_url, _image_bytes = _get_selfie_image(file_url, image_base64)
	return verify_face_for_employee(employee, image)


@frappe.whitelist(methods=["POST"])
def add_employee_checkin(
	log_type="IN",
	latitude=None,
	longitude=None,
	device_id=None,
	remarks=None,
	selfie_base64=None,
	selfie_file_url=None,
):
	"""Create an employee check-in/out after verifying and attaching a selfie."""
	current_user = frappe.session.user
	if not current_user or current_user == "Guest":
		frappe.throw(_("Not logged in"), frappe.AuthenticationError)

	employee = frappe.db.get_value(
		"Employee",
		{"user_id": current_user, "status": "Active"},
		"name",
	)
	if not employee:
		frappe.throw(_("No active employee found for current user"))

	if log_type not in ("IN", "OUT"):
		log_type = "IN"

	try:
		latitude = float(latitude)
		longitude = float(longitude)
	except (TypeError, ValueError):
		frappe.throw(
			_("GPS Location is mandatory for attendance check-in / check-out. Please enable location on your device.")
		)

	if not latitude or not longitude or (latitude == 0.0 and longitude == 0.0):
		frappe.throw(
			_("GPS Location is mandatory for attendance check-in / check-out. Please enable location on your device.")
		)

	image, _resolved_file_url, _image_bytes = _get_selfie_image(
		file_url=selfie_file_url,
		image_base64=selfie_base64,
	)
	face_result = verify_face_for_employee(employee, image)
	if not face_result.get("matched"):
		frappe.throw(
			_("Face verification failed: {0}").format(
				face_result.get("message") or face_result.get("status")
			)
		)

	if not device_id:
		user_agent = (
			frappe.request.headers.get("User-Agent", "Unknown Device")
			if frappe.request
			else "Mobile PWA"
		)
		device_id = user_agent[:140]

	checkin = frappe.get_doc(
		{
			"doctype": "Employee Checkin",
			"employee": employee,
			"log_type": log_type,
			"time": now_datetime(),
			"device_id": (device_id or "Mobile PWA")[:140],
			"latitude": latitude,
			"longitude": longitude,
		}
	)
	if remarks and checkin.meta.has_field("remarks"):
		checkin.remarks = str(remarks)[:250]
	checkin.insert(ignore_permissions=True)

	import cv2
	from frappe.utils.file_manager import save_file

	success, encoded_selfie = cv2.imencode(
		".jpg",
		image,
		[cv2.IMWRITE_JPEG_QUALITY, 90],
	)
	if not success:
		frappe.throw(_("Could not prepare the selfie attachment"))

	selfie_file = save_file(
		fname=f"checkin-selfie-{checkin.name}.jpg",
		content=encoded_selfie.tobytes(),
		dt="Employee Checkin",
		dn=checkin.name,
		is_private=1,
		df="face_selfie",
	)
	checkin.db_set("face_selfie", selfie_file.file_url)
	checkin.face_selfie = selfie_file.file_url

	return checkin.as_dict()


def _require_face_checkin_role():
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required"), frappe.AuthenticationError)
	if "Face Checkin User" not in frappe.get_roles():
		frappe.throw(_("This account is not authorized to use the face check-in scanner"), frappe.PermissionError)


def _match_enrolled_employee(image):
	try:
		captured_embedding = extract_embedding(image)
	except FaceRecognitionError as exc:
		return None, {
			"matched": False,
			"status": "Face Not Detected",
			"message": str(exc),
		}

	active_employees = set(
		frappe.get_all(
			"Employee",
			filters={"status": "Active"},
			pluck="name",
		)
	)
	if not active_employees:
		return None, {
			"matched": False,
			"status": "No Match",
			"message": "No active employee face profiles are available",
		}

	profiles = frappe.get_all(
		"Employee Face Profile",
		filters={
			"is_active": 1,
			"enrollment_status": "Enrolled",
			"employee": ["in", list(active_employees)],
		},
		fields=["employee", "embedding", "threshold"],
	)

	matches = []
	for profile in profiles:
		threshold = flt(profile.threshold) or 0.4
		stored_embedding = parse_embedding(profile.embedding)
		similarity = cosine_similarity(stored_embedding, captured_embedding)
		if similarity >= threshold:
			matches.append(
				{
					"employee": profile.employee,
					"similarity": similarity,
					"threshold": threshold,
				}
			)

	if not matches:
		return None, {
			"matched": False,
			"status": "No Match",
			"message": "No active employee face profile matched",
		}

	matches.sort(key=lambda result: result["similarity"], reverse=True)
	best_match = matches[0]
	if len(matches) > 1 and best_match["similarity"] - matches[1]["similarity"] < 0.02:
		return None, {
			"matched": False,
			"status": "Ambiguous Match",
			"similarity": round(best_match["similarity"], 6),
			"threshold": best_match["threshold"],
			"message": "More than one employee face profile matched; ask an administrator to review enrollment",
		}

	return best_match, {
		"matched": True,
		"status": "Matched",
		"similarity": round(best_match["similarity"], 6),
		"threshold": best_match["threshold"],
	}


@frappe.whitelist(methods=["POST"])
def scan_face_and_checkin(
	image_base64=None,
	file_url=None,
	latitude=None,
	longitude=None,
	device_id=None,
	remarks=None,
):
	"""Identify an employee from their face and create their next IN/OUT check-in."""
	_require_face_checkin_role()

	try:
		latitude = float(latitude)
		longitude = float(longitude)
	except (TypeError, ValueError):
		frappe.throw(_("GPS latitude and longitude are required for face check-in"))

	if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
		frappe.throw(_("GPS latitude or longitude is out of range"))

	image, _resolved_file_url, _image_bytes = _get_selfie_image(file_url, image_base64)
	match, result = _match_enrolled_employee(image)
	if not match:
		_create_face_verification_log(
			employee=None,
			similarity=result.get("similarity"),
			threshold=result.get("threshold"),
			status=result["status"],
			failure_reason=result["message"],
		)
		return result

	employee = match["employee"]
	employee_lock = frappe.db.sql(
		"select name from `tabEmployee` where name = %s for update",
		employee,
		as_dict=True,
	)
	if not employee_lock:
		frappe.throw(_("The matched employee record no longer exists"))

	last_checkin = frappe.get_all(
		"Employee Checkin",
		filters={"employee": employee},
		fields=["name", "log_type", "time"],
		order_by="time desc, creation desc",
		limit=1,
	)
	if last_checkin and last_checkin[0].time:
		seconds_since_last = (
			now_datetime() - frappe.utils.get_datetime(last_checkin[0].time)
		).total_seconds()
		if 0 <= seconds_since_last < 30:
			return {
				"matched": True,
				"status": "Already Recorded",
				"employee": employee,
				"employee_name": frappe.db.get_value(
					"Employee", employee, "employee_name"
				),
				"log_type": last_checkin[0].log_type,
				"checkin": last_checkin[0].name,
				"message": _("A check-in was just recorded. Please wait before scanning again."),
			}
	log_type = "OUT" if last_checkin and last_checkin[0].log_type == "IN" else "IN"

	checkin = frappe.get_doc(
		{
			"doctype": "Employee Checkin",
			"employee": employee,
			"log_type": log_type,
			"time": now_datetime(),
			"device_id": (device_id or "Face Checkin Device")[:140],
			"latitude": latitude,
			"longitude": longitude,
		}
	)
	if remarks and checkin.meta.has_field("remarks"):
		checkin.remarks = str(remarks)[:250]
	checkin.insert(ignore_permissions=True)

	import cv2
	from frappe.utils.file_manager import save_file

	success, encoded_selfie = cv2.imencode(
		".jpg",
		image,
		[cv2.IMWRITE_JPEG_QUALITY, 90],
	)
	if not success:
		frappe.throw(_("Could not prepare the selfie attachment"))

	selfie_file = save_file(
		fname=f"face-checkin-{checkin.name}.jpg",
		content=encoded_selfie.tobytes(),
		dt="Employee Checkin",
		dn=checkin.name,
		is_private=1,
		df="face_selfie",
	)
	checkin.db_set("face_selfie", selfie_file.file_url)

	profile_name = frappe.db.get_value(
		"Employee Face Profile",
		{"employee": employee},
		"name",
	)
	profile = frappe.get_doc("Employee Face Profile", profile_name)
	profile.last_verified = now_datetime()
	profile.failure_count = 0
	profile.save(ignore_permissions=True)

	_create_face_verification_log(
		employee=employee,
		matched=True,
		similarity=match["similarity"],
		threshold=match["threshold"],
		status="Matched",
	)

	employee_name = frappe.db.get_value("Employee", employee, "employee_name")
	return {
		"matched": True,
		"status": "Checkin Recorded",
		"employee": employee,
		"employee_name": employee_name,
		"log_type": log_type,
		"checkin": checkin.name,
		"similarity": round(match["similarity"], 6),
		"threshold": match["threshold"],
		"message": _("Face verified. {0} recorded for {1}.").format(log_type, employee_name),
	}
