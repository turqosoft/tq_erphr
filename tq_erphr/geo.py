import math
import requests
import frappe


def get_routing_settings():
    """Retrieve routing configuration from TQ ERPHRHR Settings."""
    provider = "OpenRouteService"
    ors_key = ""
    google_key = ""

    try:
        provider = frappe.db.get_single_value("TQ ERPHRHR Settings", "routing_provider") or "OpenRouteService"
        ors_key = frappe.db.get_single_value("TQ ERPHRHR Settings", "ors_api_key") or ""
        google_key = frappe.db.get_single_value("TQ ERPHRHR Settings", "map_key") or ""
    except Exception:
        pass

    if not ors_key:
        ors_key = frappe.conf.get("ors_api_key") or ""
    if not google_key:
        google_key = frappe.conf.get("google_map_key") or ""

    return {
        "provider": str(provider).strip(),
        "ors_key": str(ors_key).strip(),
        "google_key": str(google_key).strip()
    }


def get_google_maps_distance(lat1, lon1, lat2, lon2, api_key):
    """Calculate driving distance via Google Maps Distance Matrix API."""
    if not api_key:
        return None

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{lat1},{lon1}",
        "destinations": f"{lat2},{lon2}",
        "mode": "driving",
        "key": api_key
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json() if res.content else {}

        if res.status_code == 200 and data.get("status") == "OK":
            rows = data.get("rows", [])
            if rows and len(rows) > 0:
                elements = rows[0].get("elements", [])
                if elements and len(elements) > 0:
                    elem = elements[0]
                    if elem.get("status") == "OK" and "distance" in elem:
                        distance_meters = elem["distance"]["value"]
                        return distance_meters / 1000  # convert to KM

        error_msg = data.get("error_message") or data.get("status")
        frappe.log_error(
            title="Google Maps Distance Error (Falling back)",
            message=f"Status: {res.status_code}\nResponse: {error_msg or data}"
        )
        return None
    except Exception as e:
        frappe.log_error(
            title="Google Maps Distance Exception (Falling back)",
            message=str(e)
        )
        return None


def get_ors_distance(lat1, lon1, lat2, lon2, api_key):
    """Calculate driving distance via OpenRouteService API."""
    if not api_key:
        return None

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
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        data = res.json() if res.content else {}

        if res.status_code == 200 and "routes" in data and len(data["routes"]) > 0:
            distance_meters = data["routes"][0]["summary"]["distance"]
            return distance_meters / 1000  # convert to KM

        # If quota exceeded or error, log and return None for fallback
        error_info = data.get("error", "") if isinstance(data, dict) else str(data)
        frappe.log_error(
            title="ORS Routing Warning (Falling back)",
            message=f"Status: {res.status_code}\nInput: {payload}\nResponse: {error_info}"
        )
        return None
    except Exception as e:
        frappe.log_error(
            title="ORS Distance Exception (Falling back)",
            message=str(e)
        )
        return None


def get_osrm_distance(lat1, lon1, lat2, lon2):
    """Calculate driving distance via public OSRM routing service (Fallback 1)."""
    url = f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    headers = {
        "User-Agent": "Frappe-Expense-Tracker/1.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=8)
        data = res.json() if res.content else {}

        if res.status_code == 200 and data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
            distance_meters = data["routes"][0]["distance"]
            return distance_meters / 1000  # convert to KM

        return None
    except Exception as e:
        frappe.log_error(
            title="OSRM Distance Exception",
            message=str(e)
        )
        return None


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate straight-line distance in KM using Haversine formula (Fallback 2)."""
    try:
        r = 6371.0  # Earth radius in kilometers
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        straight_line = r * c
        # Apply 1.25x road circuity factor to approximate real-world driving distance
        return straight_line * 1.25
    except Exception:
        return 0.0


def street_distance(lat1, lon1, lat2, lon2):
    """
    Calculate road distance between two points in KM based on the selected provider in settings:
    - Google Maps
    - OpenRouteService
    - OSRM (OpenStreetMap)
    With automatic multi-tier fallback so distance calculation is always resilient.
    """
    if not (lat1 and lon1 and lat2 and lon2):
        return 0

    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (ValueError, TypeError):
        return 0

    if lat1 == lat2 and lon1 == lon2:
        return 0

    settings = get_routing_settings()
    provider = settings["provider"]
    ors_key = settings["ors_key"]
    google_key = settings["google_key"]

    # 1. Primary: Google Maps
    if provider == "Google Maps":
        if google_key:
            distance = get_google_maps_distance(lat1, lon1, lat2, lon2, google_key)
            if distance is not None:
                return round(distance, 3)
        # Fallback to ORS if available
        if ors_key:
            distance = get_ors_distance(lat1, lon1, lat2, lon2, ors_key)
            if distance is not None:
                return round(distance, 3)

    # 2. Primary: OpenRouteService (Default)
    elif provider == "OpenRouteService":
        if ors_key:
            distance = get_ors_distance(lat1, lon1, lat2, lon2, ors_key)
            if distance is not None:
                return round(distance, 3)
        # Fallback to Google Maps if available
        if google_key:
            distance = get_google_maps_distance(lat1, lon1, lat2, lon2, google_key)
            if distance is not None:
                return round(distance, 3)

    # 3. Primary: OSRM (or fallback when primary/secondary services fail)
    distance = get_osrm_distance(lat1, lon1, lat2, lon2)
    if distance is not None:
        return round(distance, 3)

    # 4. Final Mathematical Fallback: Haversine
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return round(distance, 3)






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