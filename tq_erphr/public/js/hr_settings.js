frappe.ui.form.on("HR Settings", {
    refresh: function(frm) {
        // Run on refresh to set field visibility correctly
        frm.toggle_display("map_key", frm.doc.allow_geolocation_tracking ? 1 : 0);
    },
 
    allow_geolocation_tracking: function(frm) {
        // Run whenever allow_geolocation_tracking is toggled
        frm.toggle_display("map_key", frm.doc.allow_geolocation_tracking ? 1 : 0);
    }
});