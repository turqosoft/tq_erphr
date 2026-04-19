frappe.ui.form.on("Executive Expense Manager", {
    refresh_map(frm) {
        frm.call("build_route_polyline")
            .then(() => {
                frm.reload_doc();

            });
    }
});