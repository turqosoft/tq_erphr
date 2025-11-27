frappe.ui.form.on('Timesheet Details', {
    // Auto calculate working hours
    from_time: function(frm) {
        calculate_total_hours(frm);
    },
    to_time: function(frm) {
        calculate_total_hours(frm);
    },

    // Filter items based on Item Group
    refresh: function(frm) {
        frm.set_query("item", function() {
            return {
                filters: {
                    item_group: frm.doc.item_group
                }
            };
        });

        // frm.add_custom_button(__('Create Timesheets'), function() {
        //     frappe.call({
        //         method: 'project_demo.project_demo.doctype.timesheet_details_test.timesheet_details_test.create_timesheets',
        //         args: {
        //             docname: frm.doc.name
        //         },
        //         callback: function(r) {
        //             frappe.msgprint(__('Timesheets created successfully'));
        //             frm.reload_doc();
        //         }
        //     });
        // });
    },

    // Clear item when item_group changes
    item_group: function(frm) {
        frm.set_value("item", "");
    }
});

// Function to calculate total working hours
function calculate_total_hours(frm) {
    // ✅ If user already gave total_working_hours, keep it
    if (frm.doc.total_working_hours && frm.doc.total_working_hours > 0) {
        return;
    }

    // Otherwise calculate from from_time & to_time
    if (frm.doc.from_time && frm.doc.to_time) {
        let from = moment(frm.doc.from_time, "HH:mm:ss");
        let to = moment(frm.doc.to_time, "HH:mm:ss");

        // Handle overnight case (to_time is next day)
        if (to.isBefore(from)) {
            to.add(1, "day");
        }

        let duration = moment.duration(to.diff(from));
        let hours = duration.asHours();

        frm.set_value("total_working_hours", hours);
    }
}
