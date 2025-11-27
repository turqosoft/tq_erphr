# import frappe
# from frappe.utils import flt

# def get_timesheet_based_basic(employee, start_date, end_date):
#     """
#     Calculate the current basic for an employee based on Timesheets
#     between start_date and end_date, dividing rate among employees in the timesheet.
#     """
#     total_basic = 0

#     # Get all submitted timesheets in the period
#     timesheets = frappe.get_all(
#         "Timesheet",
#         filters={
#             "docstatus": 1,
#             "start_date": ["between", [start_date, end_date]]
#         },
#         fields=["name"]
#     )

#     for ts in timesheets:
#         ts_doc = frappe.get_doc("Timesheet", ts.name)
#         num_employees = len(ts_doc.time_logs) or 1  # avoid division by zero

#         for log in ts_doc.time_logs:
#             if log.employee == employee:
#                 # Calculate per-employee rate
#                 per_employee_amount = flt(log.quantity) * flt(log.rate) / num_employees
#                 total_basic += per_employee_amount

#     return total_basic


# def set_timesheet_basic_in_employee(doc, method=None):
#     """
#     Update Employee's current_basic based on timesheets in the salary slip period
#     """
#     if not doc.start_date or not doc.end_date or not doc.employee:
#         return

#     timesheet_basic = get_timesheet_based_basic(doc.employee, doc.start_date, doc.end_date)

#     if timesheet_basic:
#         emp_doc = frappe.get_doc("Employee", doc.employee)
#         emp_doc.current_basic = timesheet_basic
#         emp_doc.save(ignore_permissions=True)
#         frappe.msgprint(f"✅ Current Basic updated for {doc.employee}: {timesheet_basic}")


from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip


import frappe
from frappe.utils import flt

def set_timesheet_basic_in_salary_slip(doc, method=None):
    """
    On Salary Slip creation, calculate current basic for this employee
    based on Timesheet Details Test between start_date and end_date.
    Update Employee.current_basic and also assign to Salary Slip.basic,
    then re-run validation to refresh salary calculations.
    """

    if not doc.employee or not doc.start_date or not doc.end_date:
        return

    employee = doc.employee
    start_date = doc.start_date
    end_date = doc.end_date

    # Get submitted Timesheet Details Test within the period
    timesheets = frappe.get_all(
        "Timesheet Details Test",
        filters={
            "timesheet_date": ["between", [start_date, end_date]],
            "docstatus": 1
        },
        fields=["name", "quantity", "rate"]
    )

    total_basic = 0
    for ts_name in timesheets:
        ts_doc = frappe.get_doc("Timesheet Details Test", ts_name.name)
        num_employees = len(ts_doc.employee_detail) or 1  # avoid divide by zero

        for row in ts_doc.employee_detail:
            if row.employee_id == employee:
                per_employee_amount = flt(ts_doc.quantity) * flt(ts_doc.rate) / num_employees
                total_basic += per_employee_amount

    # If found, update Salary Slip.basic and Employee.current_basic
    if total_basic > 0:
        # update salary slip field
        doc.basic = total_basic

        # update employee record
        emp_doc = frappe.get_doc("Employee", employee)
        emp_doc.current_basic = total_basic
        emp_doc.save(ignore_permissions=True)

        frappe.msgprint(f"✅ Current Basic for {employee} set to {total_basic} based on Timesheets.")

        # Re-run salary slip validation so salary calculations update
        doc.validate()


def clear_employee_current_basic(doc, method=None):
    """
    On Salary Slip submission, clear current_basic in Employee.
    """
    if doc.employee:
        emp_doc = frappe.get_doc("Employee", doc.employee)
        emp_doc.current_basic = None  
        emp_doc.save(ignore_permissions=True)

        frappe.msgprint(f"Cleared Current Basic for {doc.employee} after Salary Slip submission.")