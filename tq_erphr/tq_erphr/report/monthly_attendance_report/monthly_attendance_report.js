frappe.query_reports["Monthly Attendance Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end()
        },
        {
            "fieldname": "branch",
            "label": "Branch",
            "fieldtype": "Link",
            "options": "Branch",
            "default": "",
            "reqd": 0
        },
        {
            "fieldname": "employment_type",
            "label": "Employment Type",
            "fieldtype": "Link",
            "options": "Employment Type"
        }
    ]
};
