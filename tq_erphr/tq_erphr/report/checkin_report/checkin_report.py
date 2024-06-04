# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import getdate
from datetime import date, timedelta
import json


def execute(filters=None):
    columns, data = [], []
    # conditions = get_conditions(filters)
    columns = get_columns(filters)
    data = get_data_new( filters)

    return columns, data, None

def daterange(start_date, end_date):
    for n in range(int((getdate(end_date) - getdate(start_date)).days+1)):
        yield getdate(start_date) + timedelta(n)

def get_conditions(filters):
    from_date, to_date = filters.get("from_date"), filters.get("to_date")
    conditions = ""
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " and `tabSales Planning`.from_date between %(from_date)s and %(to_date)s"

def get_emp_conditions(filters):
    emp_name = filters.get("emp_name")
    emp_conditions = ""
    
    if emp_name:
        emp_conditions = " and emp.name ='"+ emp_name+"'"
    return emp_conditions

def get_data_new( filters):
    data = []
    from_date, to_date = filters.get("from_date"), filters.get("to_date")
    emp_name = filters.get("emp_name")
    emp_conditions = get_emp_conditions(filters)
    values = {
            
            'from_date': from_date,
            'to_date': to_date,
            'emp_name': emp_name

           }

    map_results = frappe.db.sql(
            """
            SELECT
                emp.name,emp.employee_name
            FROM
                `tabEmployee` emp WHERE 1=1 {conditions}
            
            """.format(conditions=emp_conditions),
            as_dict=1,debug=1,
        )
    
    for empi in map_results:
        row = {
            'employee':empi.name,
            'employee_name':empi.employee_name
            
    
        }

        from_date, to_date = filters.get("from_date"), filters.get("to_date")
        for single_date in daterange(from_date, to_date):
            day = single_date.day
            month = single_date.month
            
            # db_checkin = frappe.get_all("Employee Checkin",filters = dict(employee=empi.name, time= single_date), fields = ["log_type","time","employee"])
            log_details = frappe.db.sql(
            """
            SELECT
                log_type,time,employee
            FROM
                `tabEmployee Checkin` WHERE DATE(time)=%s AND employee=%s 
            
            """,(single_date, empi.name),
            as_dict=1,debug=1,
            )
        
            field_name = "col_" + str(day) + str(month)
            log=""
            for emp_details in log_details:
                frappe.errprint(emp_details)
                checkin_time = emp_details.time.strftime("%H:%M:%S")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                log_type = emp_details.log_type  
                log+=emp_details.log_type + "-" + checkin_time + "\n"

            message = f"""
            <span style=border-left: 2px solid blue; padding-right: 12px; font-weight: bold; padding-left: 5px; margin-right: 3px;'>
            {log}
            </span>
            """

            row.update({field_name: f"{message}"})

                
                
        data.append(row)
    return data


def get_columns(filters):
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 100,
        },
        {
            "label": _("Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",

            "width": 100,
        }
    ]

    
    from_date, to_date = filters.get("from_date"), filters.get("to_date")
    for single_date in daterange(from_date, to_date):
        day = single_date.day
        month = single_date.month
        field_name = "col_" + str(day) + str(month)
        field_label = str(day) + "/" + str(month)
        columns.extend(
            [
                
                {
                    "label": field_label,
                    "fieldname": field_name,
                    "fieldtype": "Data",
                    "width": 100,
                }
            ]
        )


    return columns