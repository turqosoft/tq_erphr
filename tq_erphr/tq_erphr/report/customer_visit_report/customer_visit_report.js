frappe.query_reports["Customer Visit Report"] = {
    filters: [
        {
            fieldname: "employee",
            label: "Employee",
            fieldtype: "Link",
            options: "Employee",
            reqd: 1
        },
        {
            fieldname: "month",
            label: "Month",
            fieldtype: "Select",
            options: "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
            reqd: 1,
            default: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][parseInt(frappe.datetime.get_today().split("-")[1]) - 1]
        },
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Int",
            reqd: 1,
            default: parseInt(frappe.datetime.get_today().split("-")[0])
        }
    ]
};
