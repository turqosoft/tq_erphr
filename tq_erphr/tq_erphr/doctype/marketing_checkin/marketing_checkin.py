# Copyright (c) 2024, Turqosoft Solutions Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, get_datetime

from hrms.hr.utils import (
	get_distance_between_coordinates,
	set_geolocation_from_coordinates,
	validate_active_employee,
)

class MarketingCheckin(Document):
	def validate(self):
		self.set_geolocation()
		self.set_cogeolocation()
		
	@frappe.whitelist()
	def set_geolocation(self):
		set_geolocation_from_coordinates(self)

	@frappe.whitelist()
	def set_cogeolocation(self):
		self.set_cogeolocation_from_coordinates(self)      

	@frappe.whitelist()
	def set_cogeolocation_from_coordinates(doc):
		if not frappe.db.get_single_value("HR Settings", "allow_geolocation_tracking"):
			return

		if not (doc.colatitude and doc.colongitude):
			return

		doc.cogeolocation = frappe.json.dumps(
			{
				"type": "FeatureCollection",
				"features": [
					{
						"type": "Feature",
						"properties": {},
						# geojson needs coordinates in reverse order: long, lat instead of lat, long
						"geometry": {"type": "Point", "coordinates": [doc.colongitude, doc.colatitude]},
					}
				],
			}
		)