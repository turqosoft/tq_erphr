import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class MonthlyFoodExpense(Document):
    @frappe.whitelist()
    def get_employees(self):
        self.set("employee_food_details", [])
        
        filters = {"status": "Active"}
        if self.company:
            filters["company"] = self.company
        if self.branch:
            filters["branch"] = self.branch
        if self.employment_type:
            filters["employment_type"] = self.employment_type
            
        employees = frappe.get_all("Employee", filters=filters, fields=["name", "employee_name"])
        
        if not self.start_date or not self.end_date:
            frappe.throw("Please select Start Date and End Date")
            
        for emp in employees:
            # Count Present attendance
            working_days = frappe.db.count("Attendance", {
                "employee": emp.name,
                "attendance_date": ["between", [self.start_date, self.end_date]],
                "status": "Present",
                "docstatus": 1
            })
            
            # Count Half Day as 0.5
            half_days = frappe.db.count("Attendance", {
                "employee": emp.name,
                "attendance_date": ["between", [self.start_date, self.end_date]],
                "status": "Half Day",
                "docstatus": 1
            })
            
            total_working_days = working_days + (half_days * 0.5)
            
            food_expense = (self.default_per_day_amount or 0) * total_working_days

            # Fetch extra food expenses from Daily Extra Food Expense
            extra_food_amount = frappe.db.get_value(
                "Daily Extra Food Expense Detail",
                filters={
                    "employee": emp.name,
                    "parent": ["in", frappe.get_all("Daily Extra Food Expense", filters={
                        "date": ["between", [self.start_date, self.end_date]],
                        "docstatus": 1
                    }, pluck="name")]
                },
                fieldname="sum(amount)"
            ) or 0
            
            total_amount = food_expense + extra_food_amount

            self.append("employee_food_details", {
                "employee": emp.name,
                "employee_name": emp.employee_name,
                "working_days": total_working_days,
                "food_expense_per_working_days": food_expense,
                "extra_food_amount": extra_food_amount,
                "total": total_amount
            })
        
        self.calculate_totals()

    def calculate_totals(self):
        total = 0
        for row in self.employee_food_details:
            row.total = (row.food_expense_per_working_days or 0) + (row.extra_food_amount or 0)
            total += row.total
        self.total = total

    def validate(self):
        self.calculate_totals()

    def on_submit(self):
        self.create_additional_salary()

    def on_cancel(self):
        self.delete_additional_salary()

    def create_additional_salary(self):
        if not self.food_expense_salary_component:
            frappe.throw("Please select Food Expense Salary Component")
        
        if not self.salary_posting_date:
            frappe.throw("Please select Salary Posting Date")

        for row in self.employee_food_details:
            if row.total > 0:
                additional_salary = frappe.new_doc("Additional Salary")
                additional_salary.employee = row.employee
                additional_salary.salary_component = self.food_expense_salary_component
                additional_salary.payroll_date = self.salary_posting_date
                additional_salary.amount = row.total
                additional_salary.company = self.company
                additional_salary.ref_doctype = self.doctype
                additional_salary.ref_dn = self.name
                additional_salary.insert()
                additional_salary.submit()

    def delete_additional_salary(self):
        additional_salaries = frappe.get_all("Additional Salary", filters={
            "ref_doctype": self.doctype,
            "ref_dn": self.name
        })

        for ads in additional_salaries:
            ads_doc = frappe.get_doc("Additional Salary", ads.name)
            if ads_doc.docstatus == 1:
                ads_doc.cancel()
            frappe.delete_doc("Additional Salary", ads.name)
