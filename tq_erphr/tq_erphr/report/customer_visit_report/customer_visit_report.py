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
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # Fallback to month/year if from_date/to_date not directly provided
    if not from_date or not to_date:
        raw_month = filters.get("month")
        if isinstance(raw_month, str) and raw_month in MONTH_MAP:
            month = MONTH_MAP[raw_month]
        else:
            month = cint(raw_month)
        year = cint(filters.get("year"))

        if month and year:
            _, last_day = calendar.monthrange(year, month)
            from_date = f"{year}-{month:02d}-01"
            to_date   = f"{year}-{month:02d}-{last_day}"

    if not employee or not from_date or not to_date:
        frappe.throw(_("Employee, From Date, and To Date are required."))

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

    # Fetch company details and logo
    company_name = ""
    company_logo = ""
    company = emp_doc.company or frappe.db.get_default("company") or frappe.db.get_value("Company", {"is_group": 0}, "name")
    if company:
        comp_info = frappe.db.get_value("Company", company, ["company_name", "company_logo"], as_dict=True)
        if comp_info:
            company_name = comp_info.company_name or company
            company_logo = comp_info.company_logo or ""

    if not company_logo:
        company_logo = frappe.db.get_value("Letter Head", {"is_default": 1}, "image") or ""
    if not company_logo:
        try:
            company_logo = frappe.db.get_single_value("Website Settings", "banner_image") or frappe.db.get_single_value("Navbar Settings", "app_logo") or ""
        except Exception:
            pass

    group_by_date = cint(filters.get("group_by_date", 1))

    raw_visits = []
    for eem in eems:
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
            customer_name = ""
            if site.customer:
                customer_doc = frappe.db.get_value("Customer", site.customer, "customer_name")
                customer_name = customer_doc or site.customer
            elif site.site:
                customer_name = site.site
            elif site.location_name:
                customer_name = site.location_name

            if not customer_name:
                continue

            raw_visits.append({
                "date": eem.date,
                "customer_name": customer_name,
                "address": site.address or "",
                "contact_number": site.contact_number or "",
                "sales_agent": sales_agent,
                "category": site.category or "",
                "remarks": site.remarks or ""
            })

    if not raw_visits:
        return []

    # Count visits per date for rowspan when group_by_date is active
    date_counts = {}
    if group_by_date:
        for v in raw_visits:
            d = str(v["date"])
            date_counts[d] = date_counts.get(d, 0) + 1

    rows = []
    seen_dates = set()
    sr = 1

    for v in raw_visits:
        d = str(v["date"])
        if group_by_date:
            if d not in seen_dates:
                seen_dates.add(d)
                rowspan = date_counts[d]
                is_new_date = True
            else:
                rowspan = 0
                is_new_date = False
        else:
            rowspan = 1
            is_new_date = True

        rows.append({
            "sr_no": sr,
            "date": v["date"],
            "raw_date": v["date"],
            "rowspan": rowspan,
            "is_new_date": 1 if is_new_date else 0,
            "customer_name": v["customer_name"],
            "address": v["address"],
            "contact_number": v["contact_number"],
            "sales_agent": v["sales_agent"],
            "category": v["category"],
            "remarks": v["remarks"],
            "company_name": company_name,
            "company_logo": company_logo
        })
        sr += 1

    return rows


def cint(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0
