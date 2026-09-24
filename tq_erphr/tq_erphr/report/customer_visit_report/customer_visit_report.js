frappe.query_reports["Customer Visit Report"] = {
    filters: [
        {
            fieldname: "employee",
            label: "Employee",
            fieldtype: "Link",
            options: "Employee",
            reqd: 1,
            on_change: function() {
                var employee = frappe.query_report.get_filter_value("employee");
                if (employee) {
                    frappe.db.get_value("Employee", employee, "employee_name", function(r) {
                        if (r && r.employee_name) {
                            frappe.query_report.set_filter_value("employee_name", r.employee_name);
                        }
                    });
                } else {
                    frappe.query_report.set_filter_value("employee_name", "");
                }
            }
        },
        {
            fieldname: "employee_name",
            label: "Employee Name",
            fieldtype: "Data",
            read_only: 1
        },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            reqd: 1
        },
        {
            fieldname: "group_by_date",
            label: "Group By Date",
            fieldtype: "Check",
            default: 1
        }
    ],
    onload: function(report) {
        var employee = report.get_filter_value("employee");
        if (employee) {
            frappe.db.get_value("Employee", employee, "employee_name", function(r) {
                if (r && r.employee_name) {
                    report.set_filter_value("employee_name", r.employee_name);
                }
            });
        }
    }
};
