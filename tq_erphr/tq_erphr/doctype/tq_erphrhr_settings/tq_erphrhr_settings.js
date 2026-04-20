// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.ui.form.on("TQ ERPHRHR Settings", {
    refresh: function(frm) {
       
    }
});

// Tooggle the key based on the allow_geolocation_tracking in HR Settings
function toggle_map_key(frm) {
    frappe.db.get_value("HR Settings", null, "allow_geolocation_tracking")
        .then(r => {
            let allow = r.message.allow_geolocation_tracking || 0;
            frm.toggle_display("map_key", allow ? 1 : 0);
        });
}