function apply_route_map_styles(frm) {
    const route_field = frm.fields_dict.employee_route;

    if (!route_field) {
        return;
    }

    route_field.set_style = function(feature) {
        const properties = feature.properties || {};

        if (properties.name === "Direction") {
            return {
                color: properties.stroke || "#333333",
                weight: properties["stroke-width"] || 2,
                fillColor: properties.fill || "#333333",
                fillOpacity: properties["fill-opacity"] || 1
            };
        }

        if (properties.name === "Travel Route") {
            return {
                color: properties.stroke || "#333333",
                weight: properties["stroke-width"] || 3,
                opacity: 0.9
            };
        }

        return {};
    };

    route_field.on_each_feature = function(feature, layer) {
        if (feature.properties && feature.properties.name) {
            layer.bindTooltip(feature.properties.name);
        }
    };

    if (route_field.map && frm.doc.employee_route) {
        route_field.bind_leaflet_data(frm.doc.employee_route);
    }
}

frappe.ui.form.on("Executive Expense Manager", {
    refresh(frm) {
        apply_route_map_styles(frm);
    },

    refresh_map(frm) {
        apply_route_map_styles(frm);

        frm.call("build_route_polyline")
            .then(() => {
                frm.reload_doc();

            });
    }
});
