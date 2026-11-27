import frappe
from frappe.model.document import Document


class EmployeeFaceProfile(Document):
	def validate(self):
		if not frappe.db.exists("Employee", self.employee):
			frappe.throw("Invalid employee")

		if self.is_active and self.enrollment_status == "Enrolled" and not self.embedding:
			frappe.throw("Face Embedding is required before enrollment can be enabled")
