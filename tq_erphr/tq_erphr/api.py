import frappe
from frappe import _
import json
from frappe.desk.query_report import run
from frappe.utils import getdate, today,rounded,money_in_words,nowdate,cint,flt,get_first_day,get_last_day
import requests
import re
from frappe.utils import strip_html
from frappe.utils import flt
 
@frappe.whitelist()
def get_customer_sales_order_report(from_date=None, to_date=None, salesperson=None):
 
    filters = {
        "docstatus": 1
    }
 
    # Step 1: If salesperson → get customers mapped to that salesperson
    customer_list = None
 
    if salesperson:
        customer_sales_team = frappe.get_all(
            "Sales Team",
            filters={
                "parenttype": "Customer",
                "sales_person": salesperson
            },
            fields=["parent"]
        )
 
        customer_list = [d.parent for d in customer_sales_team]
 
        #  If no customers found → return empty
        if not customer_list:
            return []
 
        filters["customer"] = ["in", customer_list]
 
    # Step 2: Date filter
    if from_date and to_date:
        filters["transaction_date"] = ["between", [from_date, to_date]]
 
    # Step 3: Fetch Sales Orders
    sales_orders = frappe.get_all(
        "Sales Order",
        filters=filters,
        fields=["customer", "grand_total"]
    )
 
    #  Step 4: Aggregate
    customer_data = {}
 
    for so in sales_orders:
        if so.customer not in customer_data:
            customer_data[so.customer] = {
                "customer": so.customer,
                "total_count": 0,
                "total_amount": 0
            }
 
        customer_data[so.customer]["total_count"] += 1
        customer_data[so.customer]["total_amount"] += flt(so.grand_total)
 
    return list(customer_data.values())
 
 
 
 
 
 
@frappe.whitelist()
def get_customer_quotation_report(from_date=None, to_date=None, salesperson=None):
 
    filters = {
        "docstatus": 1
    }
 
    if salesperson:
        customer_sales_team = frappe.get_all(
            "Sales Team",
            filters={
                "parenttype": "Customer",
                "sales_person": salesperson
            },
            fields=["parent"]
        )
 
        customer_list = [d.parent for d in customer_sales_team]
 
        if not customer_list:
            return []
 
        filters["party_name"] = ["in", customer_list]
 
    if from_date and to_date:
        filters["transaction_date"] = ["between", [from_date, to_date]]
 
    quotations = frappe.get_all(
        "Quotation",
        filters=filters,
        fields=["party_name", "grand_total"]
    )
 
    customer_data = {}
 
    for qt in quotations:
        if qt.party_name not in customer_data:
            customer_data[qt.party_name] = {
                "customer": qt.party_name,
                "total_count": 0,
                "total_amount": 0
            }
 
        customer_data[qt.party_name]["total_count"] += 1
        customer_data[qt.party_name]["total_amount"] += flt(qt.grand_total)
 
    return list(customer_data.values())
 
 
 
 
@frappe.whitelist()
def get_payment_collection_report(from_date=None, to_date=None, salesperson=None):
 
    filters = {
        "docstatus": 1
    }
 
    #  Step 1: Filter by Sales Person via Customer Sales Team
    if salesperson:
        customer_sales_team = frappe.get_all(
            "Sales Team",
            filters={
                "parenttype": "Customer",
                "sales_person": salesperson
            },
            fields=["parent"]
        )
 
        customer_list = [d.parent for d in customer_sales_team]
 
        if not customer_list:
            return []
 
        filters["customer"] = ["in", customer_list]
 
    #  Step 2: Date filter
    if from_date and to_date:
        filters["date"] = ["between", [from_date, to_date]]
 
    #  Step 3: Fetch Payment Collection entries
    payments = frappe.get_all(
        "Payment Collection",
        filters=filters,
        fields=["customer", "amount"]
    )
 
    #  Step 4: Aggregate customer-wise
    customer_data = {}
 
    for p in payments:
        if p.customer not in customer_data:
            customer_data[p.customer] = {
                "customer": p.customer,
                "total_count": 0,
                "total_amount": 0
            }
 
        customer_data[p.customer]["total_count"] += 1
        customer_data[p.customer]["total_amount"] += flt(p.amount)
 
    return list(customer_data.values())
 
 
 
 
@frappe.whitelist()
def get_customer_estimate_report(from_date=None, to_date=None, salesperson=None):
 
    filters = {
        "docstatus": 1
    }
 
    # Step 1: Sales Person → get Customers
    if salesperson:
        customer_sales_team = frappe.get_all(
            "Sales Team",
            filters={
                "parenttype": "Customer",
                "sales_person": salesperson
            },
            fields=["parent"]
        )
 
        customer_list = [d.parent for d in customer_sales_team]
 
        if not customer_list:
            return []
 
        filters["customer"] = ["in", customer_list]
 
    # Step 2: Date filter
    if from_date and to_date:
        filters["Date"] = ["between", [from_date, to_date]]
 
    # Step 3: Fetch Estimates (Tq Estimate)
    estimates = frappe.get_all(
        "Tq Estimate",
        filters=filters,
        fields=["customer", "total_amount"]
    )
 
    # Step 4: Aggregate Customer-wise
    customer_data = {}
 
    for e in estimates:
        if e.customer not in customer_data:
            customer_data[e.customer] = {
                "customer": e.customer,
                "total_count": 0,
                "total_amount": 0
            }
 
        customer_data[e.customer]["total_count"] += 1
        customer_data[e.customer]["total_amount"] += flt(e.total_amount)
 
    return list(customer_data.values())
 
 
 
 
 
@frappe.whitelist()
def get_site_visit_report(from_date=None, to_date=None, salesperson=None):
 
    filters = {}
 
    # Sales Person → Customer filter
    if salesperson:
        customer_sales_team = frappe.get_all(
            "Sales Team",
            filters={
                "parenttype": "Customer",
                "sales_person": salesperson
            },
            fields=["parent"]
        )
 
        customer_list = [d.parent for d in customer_sales_team]
 
        if not customer_list:
            return []
 
        filters["customer"] = ["in", customer_list]
 
    # Date filter
    if from_date and to_date:
        filters["time"] = ["between", [from_date, to_date]]
 
    #  Fetch individual visit records
    visits = frappe.get_all(
        "Site Visit",
        filters=filters,
        fields=[
            "customer",
            "site",        
            "remarks"    
        ],
        order_by="time desc"
    )
 
    return visits
 
 
 
# Returns Sales Person activity dashboard (Quotation, SO, Payment, Estimate, Visit)
@frappe.whitelist()
def get_sales_person_dashboard(from_date=None, to_date=None, salesperson=None):
 
    try:
        quotation = get_customer_quotation_report(from_date, to_date, salesperson)
        sales_order = get_customer_sales_order_report(from_date, to_date, salesperson)
        payment = get_payment_collection_report(from_date, to_date, salesperson)
        estimate = get_customer_estimate_report(from_date, to_date, salesperson)
 
        visit = get_site_visit_report(from_date, to_date, salesperson)
 
        return {
            "status": "success",
            "data": {
                "quotation": quotation,
                "sales_order": sales_order,
                "payment_collection": payment,
                "estimate": estimate,
                "visit": visit  
            }
        }
 
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Dashboard API Error")
        return {
            "status": "error",
            "message": str(e)
        }