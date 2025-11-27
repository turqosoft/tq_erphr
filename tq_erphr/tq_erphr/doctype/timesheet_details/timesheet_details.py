
# import frappe
# from frappe.model.document import Document
# from frappe.utils import get_datetime, flt
# from datetime import timedelta

# class TimesheetDetailsTest(Document):

#     def on_submit(self):
#         """Create Timesheet(s) automatically when this document is submitted"""

#         if not self.employee_detail:
#             frappe.throw("No employees found in Employee Detail table.")

#         for row in self.employee_detail:
#             # Always calculate to_dt using total_working_hours
#             from_dt = get_datetime(f"{self.timesheet_date} {self.from_time or '09:00:00'}")
#             hours = flt(self.total_working_hours or 1)
#             to_dt = from_dt + timedelta(hours=hours)

#             billing_rate = flt(self.rate) or frappe.db.get_value(
#                 "Activity Type", self.activity_type, "billing_rate"
#             ) or 0
#             billing_amount = flt(hours * billing_rate)

#             ts_doc = frappe.get_doc({
#                 "doctype": "Timesheet",
#                 "employee": row.employee_id,
#                 "company": self.company,
#                 "project": self.project,
#                 "note": self.note or "",
#                 "start_date": self.timesheet_date,
#                 "custom_timesheet_details_test": self.name,
#                 "time_logs": [
#                     {
#                         "activity_type": self.activity_type,
#                         "project": self.project,
#                         "from_time": from_dt,
#                         "to_time": to_dt,
#                         "hours": hours,
#                         "billing_hours": hours,  # same as hours
#                         "billing_rate": billing_rate,
#                         "billing_amount": billing_amount,
#                         "is_billable": 1,
#                         "base_billing_rate": flt(billing_rate),        
#                         "base_billing_amount": flt(billing_amount), 
#                         "description": self.note or "",
#                     }
#                 ]
#             })

#             ts_doc.insert(ignore_permissions=True)
#             frappe.msgprint(f"✅ Draft Timesheet {ts_doc.name} created for {row.employee_id}")




#with billing rate is distributed based on the number of employees
import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, flt
from datetime import timedelta

class TimesheetDetails(Document):

    def on_submit(self):
        """Create Timesheet(s) automatically when this document is submitted"""

        if not self.employee_detail:
            frappe.throw("No employees found in Employee Detail table.")

        num_employees = len(self.employee_detail)
        # Avoid division by zero
        if num_employees == 0:
            num_employees = 1

        # Divide the total rate among employees
        distributed_rate = flt(self.rate or 0) / num_employees

        for row in self.employee_detail:
            # Always calculate to_dt using total_working_hours
            from_dt = get_datetime(f"{self.timesheet_date} {self.from_time or '09:00:00'}")
            hours = flt(self.total_working_hours or 1)
            to_dt = from_dt + timedelta(hours=hours)

            billing_rate = distributed_rate or frappe.db.get_value(
                "Activity Type", self.activity_type, "billing_rate"
            ) or 0
            billing_amount = flt(hours * billing_rate)

            ts_doc = frappe.get_doc({
                "doctype": "Timesheet",
                "employee": row.employee_id,
                "company": self.company,
                "project": self.project,
                "note": self.note or "",
                "start_date": self.timesheet_date,
                "custom_timesheet_details_test": self.name,
                "time_logs": [
                    {
                        "activity_type": self.activity_type,
                        "project": self.project,
                        "from_time": from_dt,
                        "to_time": to_dt,
                        "hours": hours,
                        "billing_hours": hours,
                        "billing_rate": billing_rate,
                        "billing_amount": billing_amount,
                        "is_billable": 1,
                        "base_billing_rate": flt(billing_rate),
                        "base_billing_amount": flt(billing_amount),
                        "description": self.note or "",
                    }
                ]
            })

            ts_doc.insert(ignore_permissions=True)
            frappe.msgprint(f"✅ Draft Timesheet {ts_doc.name} created for {row.employee_id}")
