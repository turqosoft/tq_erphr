import frappe
from frappe import _


# On create of Biometric Data, create Employee Checkin records for IN and OUT based on in_time and out_time
def biometric_data_after_insert(doc, method):
    # frappe.msgprint("Biometric ID::: " + doc.attendance_device_id)
    emp_doc_name = frappe.db.get_value('Employee', {'attendance_device_id': doc.employee_code})
    values = {'id': doc.name}

    # data = frappe.db.sql("""
    #     SELECT
    #         name, employee_name,
    #         concat(date, ' ', in_time) as inDateTime,
    #         concat(date, ' ', out_time) as outDateTime
    #     FROM `tabBiometric Data`
    #     WHERE name = %(id)s
    # """, values=values, as_dict=0)

    data = frappe.get_all(
        "Biometric Data",
        filters={"name": values.get("id")},
        fields=["name", "employee_name", "date", "in_time", "out_time"]
    )

    result = []

    for row in data:
        in_dt = f"{row.date} {row.in_time}" if row.in_time else None
        out_dt = f"{row.date} {row.out_time}" if row.out_time else None

    result.append([
        row.name,
        row.employee_name,
        in_dt,
        out_dt
    ])

    for info in result:
        frappe.get_doc(dict(
            doctype = 'Employee Checkin',
            log_type = 'IN',
            time = info[2],
            employee = emp_doc_name
        )).insert()

        frappe.get_doc(dict(
            doctype = 'Employee Checkin',
            log_type = 'OUT',
            time = info[3],
            employee = emp_doc_name
        )).insert()

