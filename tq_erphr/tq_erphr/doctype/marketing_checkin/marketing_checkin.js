// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Marketing Checkin", {
	refresh: async (frm) => {
		// if (!frm.doc.__islocal) frm.trigger("add_fetch_shift_button");
        // First check if geolocation tracking is allowed in HR Settings
		const allow_geolocation_tracking = await frappe.db.get_single_value(
			"HR Settings",
			"allow_geolocation_tracking",
		);

		if (!allow_geolocation_tracking) {
			hide_field(["fetch_geolocation", "latitude", "longitude", "geolocation", "cogeolocation"]);
			return;
		}

        // Hide the Checkout button initially
        if (!frm.doc.__islocal) {
            if (!frm.doc.checkin_time) {
                frm.set_df_property("check_out_button", "hidden", 1);
            } else if (!frm.doc.checkout_time) {
                frm.set_df_property("check_out_button", "hidden", 0);
            }
        }
        
        // Add Check-in button if not already checked in
        if (!frm.doc.checkin_time) {
            frm.add_custom_button(__('Check-In Now'), function() {
                get_current_location(frm, "checkin");
            }, "Actions");
        }

        // Add Check-out button if checked-in and not yet checked out
        if (frm.doc.checkin_time && !frm.doc.checkout_time) {
            frm.add_custom_button(__('Check-Out Now'), function() {
                get_current_location(frm, "checkout");
            }, "Actions").addClass("btn-danger");
        }
	},

	fetch_geolocation: (frm) => {
		// hrms.fetch_geolocation(frm);
	},
});

function get_current_location(frm, action) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            let lat = position.coords.latitude;
            let long = position.coords.longitude;
            let now = frappe.datetime.now_datetime();
            
            // Ensure Salesman is set before saving
            if (!frm.doc.employee) {
                frappe.msgprint("Error: Salesman field is required.");
                return;
            }

            if (action === "checkin") {
                frm.set_value("latitude", lat);
                frm.set_value("longitude", long);
                frm.set_value("checkin_time", now);
                frm.save();
                // frappe.msgprint("Checked in successfully!");
            } else if (action === "checkout") {
                frm.set_value("colatitude", lat);
                frm.set_value("colongitude", long);
                frm.set_value("checkout_time", now);
                frm.set_value("checked_out", 1);
                frm.save();
                // frappe.msgprint("Checked out successfully!");
                frm.reload_doc();  // Refresh to disable Check-Out button
            }

            
        }, function(error) {
            frappe.msgprint("Error fetching location. Please allow location access.");
        });
    } else {
        frappe.msgprint("Geolocation is not supported in your browser.");
    }
}
