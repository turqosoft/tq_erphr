frappe.query_reports["Sales Man Summary"] = {
    filters: [
        {
            fieldname: "salesperson",
            label: "Sales Person",
            fieldtype: "Link",
            options: "Sales Person",
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1
        }
    ]
};