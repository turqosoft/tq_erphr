function apply_route_map_styles(frm) {
    const route_field = frm.fields_dict.employee_route;

    if (!route_field) {
        return;
    }

    const marker_offsets = {};
    const offset_step = 0.00005;

    function make_route_icon(label, color, shape) {
        const is_diamond = shape === "diamond";
        const wrapper_style = [
            "width: 28px",
            "height: 28px",
            "display: flex",
            "align-items: center",
            "justify-content: center",
            `background: ${color}`,
            "border: 2px solid #ffffff",
            "box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35)",
            "color: #ffffff",
            "font-size: 12px",
            "font-weight: 700",
            "line-height: 1",
            is_diamond ? "border-radius: 4px" : "border-radius: 50%",
            is_diamond ? "transform: rotate(45deg)" : ""
        ].filter(Boolean).join("; ");

        const label_style = is_diamond ? "transform: rotate(-45deg)" : "";

        return L.divIcon({
            className: "eem-route-marker",
            html: `<div style="${wrapper_style}"><span style="${label_style}">${label}</span></div>`,
            iconSize: [28, 28],
            iconAnchor: [14, 14]
        });
    }

    route_field.point_to_layer = function(feature, latlng) {
        const properties = feature.properties || {};
        const name = properties.name || "";
        const coord_key = [
            Number(latlng.lat).toFixed(6),
            Number(latlng.lng).toFixed(6)
        ].join(",");
        const offset_count = marker_offsets[coord_key] || 0;

        marker_offsets[coord_key] = offset_count + 1;

        if (offset_count) {
            latlng = L.latLng(
                latlng.lat + offset_step * offset_count,
                latlng.lng + offset_step * offset_count
            );
        }

        if (name === "Start Location") {
            return L.marker(latlng, {
                icon: make_route_icon("S", "#00a83b", "circle")
            });
        }

        if (name.startsWith("Site ")) {
            const site_index = (name.match(/^Site (\d+)/) || [])[1] || "";

            return L.marker(latlng, {
                icon: make_route_icon(site_index, "#0066ff", "circle")
            });
        }

        if (name === "End Location") {
            return L.marker(latlng, {
                icon: make_route_icon("E", "#d93025", "diamond")
            });
        }

        return L.marker(latlng);
    };

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
