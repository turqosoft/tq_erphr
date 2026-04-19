import requests
import frappe


ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjgxNTU0YTdkZGFkNDQ5MzQ4MmMwNWUyYjAwMGFmZjE1IiwiaCI6Im11cm11cjY0In0=" 


def street_distance(lat1, lon1, lat2, lon2):
    if not (lat1 and lon1 and lat2 and lon2):
        return 0

    api_key = ORS_API_KEY
    if not api_key:
        frappe.throw("ORS API key missing")

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    payload = {
        "coordinates": [
            [lon1, lat1],
            [lon2, lat2]
        ]
    }

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        data = res.json()

       

        # Check for error structure
        if "error" in data:
            frappe.log_error(
                title="ORS Routing Error",
                message=f"Input: {payload}\nResponse: {data}"
            )
            return 0

        # Correct ORS v2 path
        distance_meters = data["routes"][0]["summary"]["distance"]
        return distance_meters / 1000     # convert to KM

    except Exception as e:
        frappe.log_error(
            title="ORS Distance Exception",
            message=str(e)
        )
        return 0




def reverse_geocode(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "jsonv2",
            "lat": lat,
            "lon": lon,
            "zoom": 18,
            "addressdetails": 1
        }

        headers = {
            "User-Agent": "Frappe-Expense-Tracker"
        }

        res = requests.get(url, params=params, headers=headers, timeout=8)
        data = res.json()

        return data.get("display_name", "")
    except Exception as e:
        frappe.log_error("Reverse Geocode Error", str(e))
        return ""