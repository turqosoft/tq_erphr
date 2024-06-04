// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.query_reports["Checkin Report"] = {
    "filters": [
      
        {
            label: __("From Posting Date"),
            fieldname:"from_date",
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -10),
            reqd: 1
        },
        {
            label: __("To Posting Date"),
            fieldname:"to_date",
            fieldtype: "Date",

            default: frappe.datetime.get_today(),
            reqd: 1,
        },
        {
            label: __("Employee"),
            fieldname:"emp_name",
            fieldtype: "Link",
            options: "Employee"


        }
    ]
}