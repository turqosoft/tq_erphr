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

        if (doc.expense_claim_status === "Paid") {
            return ["Paid", "darkgreen", "expense_claim_status,=,Paid"];
        }

        if (doc.expense_claim_status === "Rejected") {
            return ["Rejected", "red", "expense_claim_status,=,Rejected"];
        }

        if (doc.expense_claim_status === "Cancelled") {
            return ["Not Created", "red", "expense_claim_status,=,Cancelled"];
        }
    },

    onload(listview) {

        listview.page.add_actions_menu_item(
            __("Create Expense Claim"),
            function () {

                const selected = listview.get_checked_items();

                if (!selected.length) {
                    frappe.msgprint("Please select at least one record.");
                    return;
                }

                const names = selected.map(d => d.name);

                frappe.confirm(
                    `Create Expense Claim for ${names.length} record(s)?`,
                    () => {
                        frappe.call({
                            method: "tq_erphr.tq_erphr.doctype.executive_expense_manager.executive_expense_manager.bulk_create_expense_claim",
                            args: {
                                executive_expense_managers: names
                            },
                            freeze: true,
                            callback(r) {
                                if (!r.exc) {
                                    frappe.msgprint(r.message || "Expense Claims created successfully.");
                                    listview.refresh();
                                }
                            }
                        });
                    }, false, __("Create")
                );
            }
        );
    }
};
