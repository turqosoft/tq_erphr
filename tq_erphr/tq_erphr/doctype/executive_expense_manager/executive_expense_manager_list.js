frappe.listview_settings["Executive Expense Manager"] = {
    add_fields: ["expense_claim_status"],

    get_indicator(doc) {
        if (doc.expense_claim_status === "Not Created") {
            return ["Not Created", "gray", "expense_claim_status,=,Not Created"];
        }

        if (doc.expense_claim_status === "Processing") {
            return ["Processing", "blue", "expense_claim_status,=,Processing"];
        }

        if (doc.expense_claim_status === "Submitted") {
            return ["Submitted", "orange", "expense_claim_status,=,Submitted"];
        }

        if (doc.expense_claim_status === "Approved") {
            return ["Approved", "green", "expense_claim_status,=,Approved"];
        }

        if (doc.expense_claim_status === "Unpaid") {
            return ["Unpaid", "orange", "expense_claim_status,=,Unpaid"];
        }

        if (doc.expense_claim_status === "Paid") {
            return ["Paid", "green", "expense_claim_status,=,Paid"];
        }

        if (doc.expense_claim_status === "Rejected") {
            return ["Rejected", "red", "expense_claim_status,=,Rejected"];
        }

        if (doc.expense_claim_status === "Cancelled") {
            return ["Not Created", "red", "expense_claim_status,=,Cancelled"];
        }
    },

    onload(listview) {
        listview.page.add_inner_button(__("Employee Expense Claim"), () => {
            const dialog = new frappe.ui.Dialog({
                title: __("Employee Expense Claim"),
                fields: [
                    {
                        fieldname: "employee",
                        fieldtype: "Link",
                        label: __("Employee"),
                        options: "Employee",
                        reqd: 1,
                        get_query: () => {
                            return {
                                query: "tq_erphr.tq_erphr.doctype.executive_expense_manager.executive_expense_manager.get_eem_employees"
                            };
                        }
                    },
                    {
                        fieldname: "start_date",
                        fieldtype: "Date",
                        label: __("Start Date"),
                        reqd: 1,
                    },
                    {
                        fieldname: "end_date",
                        fieldtype: "Date",
                        label: __("End Date"),
                        reqd: 1,
                    },
                ],
                primary_action_label: __("Create"),
                primary_action(values) {
                    if (values.start_date > values.end_date) {
                        frappe.msgprint(__("Start Date cannot be after End Date."));
                        return;
                    }

                    frappe.call({
                        method: "tq_erphr.tq_erphr.doctype.executive_expense_manager.executive_expense_manager.create_employee_expense_claim",
                        args: values,
                        freeze: true,
                        freeze_message: __("Creating Expense Claim..."),
                        callback(r) {
                            if (!r.exc) {
                                dialog.hide();
                                frappe.msgprint(r.message || __("Expense Claim created successfully."));
                                listview.refresh();
                            }
                        },
                    });
                },
            });

            dialog.show();
        });
    },
};
