frappe.ui.form.on('Daily Extra Food Expense', {
    refresh: function (frm) {
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Fetch Employees'), function () {
                frm.call({
                    doc: frm.doc,
                    method: 'get_employees',
                    callback: function (r) {
                        if (!r.exc) {
                            frm.refresh_field('extra_expenses');
                        }
                    }
                });
            });
        }
    },
    default_extra_food_amount: function (frm) {
        frm.doc.extra_expenses.forEach(row => {
            row.amount = frm.doc.default_extra_food_amount || 0;
        });
        frm.refresh_field('extra_expenses');
        calculate_grand_total(frm);
    }
});

frappe.ui.form.on('Daily Extra Food Expense Detail', {
    amount: function (frm, cdt, cdn) {
        calculate_grand_total(frm);
    },
    extra_expenses_remove: function (frm) {
        calculate_grand_total(frm);
    }
});

var calculate_grand_total = function (frm) {
    let total = 0;
    frm.doc.extra_expenses.forEach(row => {
        total += (row.amount || 0);
    });
    frm.set_value('total_amount', total);
};
