
frappe.ui.form.on("TQ ERPHRHR Settings", {
    refresh: function(frm) {
        check_and_render_all_status(frm);
    },
    routing_provider: function(frm) {
        check_and_render_all_status(frm);
    },
    ors_api_key: function(frm) {
        check_and_render_all_status(frm);
    },
    map_key: function(frm) {
        check_and_render_all_status(frm);
    }
});

function check_and_render_all_status(frm) {
    if (!frm.fields_dict.routing_status_html) return;

    const wrapper = frm.fields_dict.routing_status_html.$wrapper;
    wrapper.empty();

    const selectedProvider = frm.doc.routing_provider || "OpenRouteService";

    const container = document.createElement("div");
    container.className = "routing-status-dashboard";
    container.style.marginTop = "8px";
    container.style.marginBottom = "15px";

    // Loading card
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "alert alert-info";
    loadingDiv.style.display = "flex";
    loadingDiv.style.alignItems = "center";
    loadingDiv.style.justifyContent = "space-between";
    loadingDiv.style.padding = "10px 15px";
    loadingDiv.style.borderRadius = "8px";

    const loadingText = document.createElement("span");
    loadingText.textContent = `⏳ Checking ${selectedProvider} connection...`;
    loadingDiv.appendChild(loadingText);
    container.appendChild(loadingDiv);
    wrapper.append(container);

    frappe.call({
        method: "tq_erphr.tq_erphr.doctype.tq_erphrhr_settings.tq_erphrhr_settings.check_all_routing_status",
        args: {
            ors_key: frm.doc.ors_api_key || "",
            google_key: frm.doc.map_key || ""
        },
        callback: function(r) {
            wrapper.empty();
            const data = r.message || {};
            render_selected_provider_status(frm, wrapper, data, selectedProvider);
        },
        error: function() {
            wrapper.empty();
            render_error_card(wrapper);
        }
    });
}

function render_selected_provider_status(frm, wrapper, data, selectedProvider) {
    const dashboard = document.createElement("div");
    dashboard.style.display = "flex";
    dashboard.style.flexDirection = "column";
    dashboard.style.gap = "8px";
    dashboard.style.marginTop = "8px";
    dashboard.style.marginBottom = "15px";

    let serviceName = "OpenRouteService (ORS)";
    let serviceInfo = data.ors || { status: "missing_key", message: "Not configured" };

    if (selectedProvider === "Google Maps") {
        serviceName = "Google Maps Distance Matrix";
        serviceInfo = data.google || { status: "missing_key", message: "Not configured" };
    } else if (selectedProvider === "OSRM (OpenStreetMap)") {
        serviceName = "OSRM (Public OpenStreetMap)";
        serviceInfo = data.osrm || { status: "active", message: "Online & Reachable" };
    }

    const card = create_service_status_row(serviceName, serviceInfo, frm);
    dashboard.appendChild(card);
    wrapper.append(dashboard);
}

function create_service_status_row(name, info, frm) {
    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.alignItems = "center";
    row.style.justifyContent = "space-between";
    row.style.padding = "12px 16px";
    row.style.borderRadius = "8px";
    row.style.fontSize = "13px";

    let bg = "#f8f9fa";
    let border = "#dee2e6";
    let badgeBg = "#6c757d";
    let badgeText = "Not Configured";
    let icon = "ℹ️";

    if (info.status === "active") {
        bg = "#d1e7dd";
        border = "#a3cfbb";
        badgeBg = "#16a34a";
        badgeText = "Active / Online";
        icon = "✅";
    } else if (info.status === "quota_exceeded") {
        bg = "#fff3cd";
        border = "#ffe69c";
        badgeBg = "#d97706";
        badgeText = "Quota Exceeded";
        icon = "⚠️";
    } else if (info.status === "timeout") {
        bg = "#fff3cd";
        border = "#ffe69c";
        badgeBg = "#d97706";
        badgeText = "Latency / Timeout";
        icon = "⏳";
    } else if (info.status === "invalid_key" || info.status === "error") {
        bg = "#f8d7da";
        border = "#f1aeb5";
        badgeBg = "#dc2626";
        badgeText = "Error / Invalid";
        icon = "❌";
    } else if (info.status === "missing_key") {
        bg = "#e2e3e5";
        border = "#c6c8ca";
        badgeBg = "#6c757d";
        badgeText = "Key Missing";
        icon = "⚪";
    }

    row.style.border = `1px solid ${border}`;
    row.style.backgroundColor = bg;

    // Left info
    const leftDiv = document.createElement("div");
    leftDiv.style.display = "flex";
    leftDiv.style.flexDirection = "column";
    leftDiv.style.gap = "3px";

    const nameSpan = document.createElement("span");
    nameSpan.style.fontWeight = "600";
    nameSpan.style.color = "#1f2937";
    nameSpan.textContent = `${icon} ${name}`;
    leftDiv.appendChild(nameSpan);

    const msgSpan = document.createElement("span");
    msgSpan.style.color = "#4b5563";
    msgSpan.style.fontSize = "12px";
    msgSpan.textContent = info.message || "";
    leftDiv.appendChild(msgSpan);

    row.appendChild(leftDiv);

    // Right actions container (Badge + Test Button)
    const rightDiv = document.createElement("div");
    rightDiv.style.display = "flex";
    rightDiv.style.alignItems = "center";
    rightDiv.style.gap = "10px";

    const badge = document.createElement("span");
    badge.style.backgroundColor = badgeBg;
    badge.style.color = "#ffffff";
    badge.style.fontSize = "11px";
    badge.style.fontWeight = "600";
    badge.style.padding = "4px 10px";
    badge.style.borderRadius = "12px";
    badge.style.whiteSpace = "nowrap";
    badge.textContent = badgeText;
    rightDiv.appendChild(badge);

    const testBtn = document.createElement("button");
    testBtn.className = "btn btn-xs btn-default";
    testBtn.style.whiteSpace = "nowrap";
    testBtn.textContent = "Test Connection";
    testBtn.onclick = function(e) {
        e.preventDefault();
        check_and_render_all_status(frm);
    };
    rightDiv.appendChild(testBtn);

    row.appendChild(rightDiv);

    return row;
}

function render_error_card(wrapper) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "alert alert-danger";
    errorDiv.style.padding = "10px 15px";
    errorDiv.style.borderRadius = "8px";
    errorDiv.style.fontSize = "12px";
    errorDiv.textContent = "❌ Failed to connect to server to verify routing status.";
    wrapper.append(errorDiv);
}