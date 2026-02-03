frappe.ui.form.on('Monthly Food Expense', {
    refresh: function (frm) {
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Get Employees'), function () {
                frm.call({
                    doc: frm.doc,
                    method: 'get_employees',
                    callback: function (r) {
                        if (!r.exc) {
                            frm.refresh_field('employee_food_details');
                        }
                    }
                });
            });
        }
    },
    default_per_day_amount: function (frm) {
        frm.doc.employee_food_details.forEach(row => {
            row.food_expense_per_working_days = (frm.doc.default_per_day_amount || 0) * (row.working_days || 0);
            row.total = row.food_expense_per_working_days + (row.extra_food_amount || 0);
        });
        frm.refresh_field('employee_food_details');
        calculate_grand_total(frm);
    }
});

frappe.ui.form.on('Employee Food Details', {
    extra_food_amount: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.total = (row.food_expense_per_working_days || 0) + (row.extra_food_amount || 0);
        frm.refresh_field('employee_food_details');
        calculate_grand_total(frm);
    },
    food_expense_per_working_days: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.total = (row.food_expense_per_working_days || 0) + (row.extra_food_amount || 0);
        frm.refresh_field('employee_food_details');
        calculate_grand_total(frm);
    },
    employee_food_details_remove: function (frm) {
        calculate_grand_total(frm);
    }
});

var calculate_grand_total = function (frm) {
    let total = 0;
    frm.doc.employee_food_details.forEach(row => {
        total += (row.total || 0);
    });
    frm.set_value('total', total);
};
