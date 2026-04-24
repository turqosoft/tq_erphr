import frappe
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ✅ Import existing APIs
from tqerp_bd.api import (
    get_customer_quotation_report,
    get_customer_sales_order_report,
    get_payment_collection_report,
    get_customer_estimate_report,
    get_site_visit_report
)


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


# ✅ Columns 
def get_columns():
    return [
        {"label": "Section", "fieldname": "section", "fieldtype": "Data", "width": 220},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": "Count", "fieldname": "count", "fieldtype": "Data", "width": 100},  
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Data", "width": 120}, 
        {"label": "Site", "fieldname": "site", "fieldtype": "Data", "width": 150},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 250}
    ]


def get_data(filters):

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    salesperson = filters.get("salesperson")

     # ✅ VALIDATION: Max 2 months range
    if from_date and to_date:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")

        max_to_date = from_dt + relativedelta(months=2)

        if to_dt > max_to_date:
            frappe.throw("Date range should not exceed 2 months")

    data = []
   

    # Helper: spacing
    def add_space():
        data.append({})

    # Helper: section header
    def add_header(title):
        data.append({
            # "section": f"<b>{title}</b>"
            "section": f"<b>{title.upper()}</b>"
        })

    # Helper: total row (FULL BOLD)
    def add_total(total_count, total_amount):
        data.append({
            "section": "<b>Total</b>",
            "customer": "",
            "count": f"<b>{total_count}</b>",
            "amount": f"<b>{total_amount}</b>"
        })

    # =======================
    # QUOTATION
    # =======================
    add_header("Quotation")

    quotation = get_customer_quotation_report(from_date, to_date, salesperson)

    total_count = 0
    total_amount = 0

    for row in quotation:
        total_count += row.get("total_count", 0)
        total_amount += row.get("total_amount", 0)

        data.append({
            "customer": row.get("customer"),
            "count": row.get("total_count"),
            "amount": row.get("total_amount")
        })

    add_total(total_count, total_amount)
    add_space()

    # =======================
    # SALES ORDER
    # =======================
    add_header("Sales Order")

    sales_order = get_customer_sales_order_report(from_date, to_date, salesperson)

    total_count = 0
    total_amount = 0

    for row in sales_order:
        total_count += row.get("total_count", 0)
        total_amount += row.get("total_amount", 0)

        data.append({
            "customer": row.get("customer"),
            "count": row.get("total_count"),
            "amount": row.get("total_amount")
        })

    add_total(total_count, total_amount)
    add_space()

    # =======================
    # PAYMENT COLLECTION
    # =======================
    add_header("Payment Collection")

    payment = get_payment_collection_report(from_date, to_date, salesperson)

    total_count = 0
    total_amount = 0

    for row in payment:
        total_count += row.get("total_count", 0)
        total_amount += row.get("total_amount", 0)

        data.append({
            "customer": row.get("customer"),
            "count": row.get("total_count"),
            "amount": row.get("total_amount")
        })

    add_total(total_count, total_amount)
    add_space()

    # =======================
    # ESTIMATE
    # =======================
    add_header("Estimate")

    estimate = get_customer_estimate_report(from_date, to_date, salesperson)

    total_count = 0
    total_amount = 0

    for row in estimate:
        total_count += row.get("total_count", 0)
        total_amount += row.get("total_amount", 0)

        data.append({
            "customer": row.get("customer"),
            "count": row.get("total_count"),
            "amount": row.get("total_amount")
        })

    add_total(total_count, total_amount)
    add_space()

    # =======================
    # SITE VISIT
    # =======================
    add_header("Site Visit")

    visits = get_site_visit_report(from_date, to_date, salesperson)

    if visits:
        for row in visits:
            data.append({
                "customer": row.get("customer"),
                "site": row.get("site"),
                "remarks": row.get("remarks")
            })
    else:
        data.append({
            "section": "<b>No Visit Data Found</b>"
        })

    return data