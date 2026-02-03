import frappe
from frappe.model.document import Document

class DailyExtraFoodExpense(Document):
    def validate(self):
        self.calculate_total()

    def calculate_total(self):
        total = 0
        for row in self.extra_expenses:
            total += (row.amount or 0)
        self.total_amount = total

    @frappe.whitelist()
    def get_employees(self):
        self.set("extra_expenses", [])
        
        filters = {"status": "Active"}
        if self.company:
            filters["company"] = self.company
        if self.branch:
            filters["branch"] = self.branch
        if self.employment_type:
            filters["employment_type"] = self.employment_type
            
        employees = frappe.get_all("Employee", filters=filters, fields=["name", "employee_name"])
        
        for emp in employees:
            self.append("extra_expenses", {
                "employee": emp.name,
                "employee_name": emp.employee_name,
                "amount": self.default_extra_food_amount or 0
            })
        
        self.calculate_total()
