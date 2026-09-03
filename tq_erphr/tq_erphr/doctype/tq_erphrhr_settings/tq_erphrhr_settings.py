

import frappe
import requests
from frappe.model.document import Document


class TQERPHRHRSettings(Document):
	pass


@frappe.whitelist()
def check_ors_status(api_key=None):
	"""
	Check whether the OpenRouteService API key is active, exhausted, or invalid.
	"""
	if not api_key:
		api_key = frappe.db.get_single_value("TQ ERPHRHR Settings", "ors_api_key")

	if not api_key:
		return {
			"status": "missing_key",
			"message": "No OpenRouteService API key configured.",
		}

	api_key = str(api_key).strip()

	url = "https://api.openrouteservice.org/v2/directions/driving-car"
	payload = {
		"coordinates": [
			[77.5946, 12.9716],
			[77.6245, 12.9352],
		]
	}
	headers = {
		"Authorization": api_key,
		"Content-Type": "application/json",
	}

	try:
		res = requests.post(url, json=payload, headers=headers, timeout=12)
		data = res.json() if res.content else {}

		if res.status_code == 200 and "routes" in data:
			return {
				"status": "active",
				"message": "OpenRouteService API key is active and working properly.",
			}

		error_msg = data.get("error", "") if isinstance(data, dict) else str(data)
		if res.status_code == 403 or "quota" in str(error_msg).lower():
			return {
				"status": "quota_exceeded",
				"message": "API Quota Exceeded / Exhausted.",
			}
		elif res.status_code == 401 or "unauthorized" in str(error_msg).lower():
			return {
				"status": "invalid_key",
				"message": "Invalid API key or unauthorized.",
			}
		else:
			return {
				"status": "error",
				"message": f"ORS returned status {res.status_code}: {error_msg or res.text}",
			}
	except requests.exceptions.Timeout:
		return {
			"status": "timeout",
			"message": "Connection to OpenRouteService timed out (server latency).",
		}
	except Exception as e:
		return {
			"status": "error",
			"message": f"Failed to reach OpenRouteService: {str(e)}",
		}


@frappe.whitelist()
def check_google_maps_status(api_key=None):
	"""
	Check whether the Google Maps Distance Matrix API key is active and valid.
	"""
	if not api_key:
		api_key = frappe.db.get_single_value("TQ ERPHRHR Settings", "map_key")

	if not api_key:
		return {
			"status": "missing_key",
			"message": "No Google Map Key configured.",
		}

	api_key = str(api_key).strip()

	url = "https://maps.googleapis.com/maps/api/distancematrix/json"
	params = {
		"origins": "12.9716,77.5946",
		"destinations": "12.9352,77.6245",
		"mode": "driving",
		"key": api_key,
	}

	try:
		res = requests.get(url, params=params, timeout=10)
		data = res.json() if res.content else {}

		if res.status_code == 200 and data.get("status") == "OK":
			rows = data.get("rows", [])
			if rows and rows[0].get("elements", []) and rows[0]["elements"][0].get("status") == "OK":
				return {
					"status": "active",
					"message": "Google Maps Distance Matrix API is active and operational.",
				}

		status = data.get("status", "ERROR")
		error_msg = data.get("error_message") or status
		if status in ["REQUEST_DENIED", "INVALID_REQUEST"]:
			return {
				"status": "invalid_key",
				"message": f"Google Maps API error: {error_msg}",
			}
		elif status == "OVER_QUERY_LIMIT":
			return {
				"status": "quota_exceeded",
				"message": "Google Maps daily query limit exceeded.",
			}
		else:
			return {
				"status": "error",
				"message": f"Google Maps returned status: {error_msg}",
			}
	except requests.exceptions.Timeout:
		return {
			"status": "timeout",
			"message": "Connection to Google Maps timed out.",
		}
	except Exception as e:
		return {
			"status": "error",
			"message": f"Failed to reach Google Maps: {str(e)}",
		}


@frappe.whitelist()
def check_osrm_status():
	"""
	Check whether the public OSRM fallback server is reachable.
	"""
	url = "https://router.project-osrm.org/route/v1/driving/77.5946,12.9716;77.6245,12.9352?overview=false"
	headers = {"User-Agent": "Frappe-Expense-Tracker/1.0"}

	try:
		res = requests.get(url, headers=headers, timeout=8)
		data = res.json() if res.content else {}

		if res.status_code == 200 and data.get("code") == "Ok":
			return {
				"status": "active",
				"message": "Public OSRM server is online and responding normally.",
			}
		return {
			"status": "error",
			"message": f"OSRM server returned code: {data.get('code') or res.status_code}",
		}
	except requests.exceptions.Timeout:
		return {
			"status": "timeout",
			"message": "OSRM public server is currently experiencing latency.",
		}
	except Exception as e:
		return {
			"status": "error",
			"message": f"Failed to reach OSRM server: {str(e)}",
		}


@frappe.whitelist()
def check_all_routing_status(ors_key=None, google_key=None):
	"""
	Check status for all 3 routing services simultaneously.
	"""
	return {
		"ors": check_ors_status(ors_key),
		"google": check_google_maps_status(google_key),
		"osrm": check_osrm_status(),
	}