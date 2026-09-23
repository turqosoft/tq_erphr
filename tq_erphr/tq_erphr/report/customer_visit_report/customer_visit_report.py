import frappe
from frappe import _
import calendar


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "sr_no",
            "label": _("Sr No"),
            "fieldtype": "Int",
            "width": 60
        },
        {
            "fieldname": "date",
            "label": _("Dated"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "customer_name",
            "label": _("Customer Name"),
            "fieldtype": "Data",
            "width": 160
        },
        {
            "fieldname": "address",
            "label": _("Address"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "contact_number",
            "label": _("Contact Number"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "sales_agent",
            "label": _("Sales Agent"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "category",
            "label": _("Category"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "remarks",
            "label": _("Remarks"),
            "fieldtype": "Data",
            "width": 300
        }
    ]


MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}


def get_data(filters):
    employee = filters.get("employee")
    raw_month = filters.get("month")
    if isinstance(raw_month, str) and raw_month in MONTH_MAP:
        month = MONTH_MAP[raw_month]
    else:
        month = cint(raw_month)
    year = cint(filters.get("year"))

    if not employee or not month or not year:
        frappe.throw(_("Employee, Month, and Year are required."))

    # Compute date range for the selected month
    _, last_day = calendar.monthrange(year, month)
    from_date = f"{year}-{month:02d}-01"
    to_date   = f"{year}-{month:02d}-{last_day}"

    # Fetch parent EEM records for the employee in the month
    eems = frappe.get_all(
        "Executive Expense Manager",
        filters={
            "employee": employee,
            "date": ["between", [from_date, to_date]],
            "docstatus": ["!=", 2],   # exclude cancelled
        },
        fields=["name", "date", "employee", "employee_name"],
        order_by="date asc"
    )

    if not eems:
        return []

    # Get employee name for Sales Agent column
    emp_doc = frappe.get_doc("Employee", employee)
    sales_agent = emp_doc.employee_name or employee

    rows = []
    sr = 1

    for eem in eems:
        # Fetch all site tracking rows for this EEM
        site_rows = frappe.get_all(
            "Employee Site Tracking",
            filters={"parent": eem.name},
            fields=[
                "customer", "site", "location_name", "address",
                "contact_number", "category", "remarks"
            ],
            order_by="idx asc"
        )

        for site in site_rows:
            # Resolve customer name in order of preference:
            # 1. Customer link
            # 2. Site field
            # 3. Location Name (last preference)
            customer_name = ""
            if site.customer:
                customer_doc = frappe.db.get_value("Customer", site.customer, "customer_name")
                customer_name = customer_doc or site.customer
            elif site.site:
                customer_name = site.site
            elif site.location_name:
                customer_name = site.location_name

            if not customer_name:
                continue  # skip rows with no customer/location

            rows.append({
                "sr_no": sr,
                "date": eem.date,
                "customer_name": customer_name,
                "address": site.address or "",
                "contact_number": site.contact_number or "",
                "sales_agent": sales_agent,
                "category": site.category or "",
                "remarks": site.remarks or ""
            })
            sr += 1

    return rows


def cint(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0
