import { createResource } from "frappe-ui"

export const customersResource = createResource({
	url: "tq_erphr.pwa_api.get_customers_list",
	auto: true,
})

export const todaySiteVisitsResource = createResource({
	url: "tq_erphr.pwa_api.get_today_site_visits",
	auto: true,
})

export const addSiteVisitResource = createResource({
	url: "tq_erphr.pwa_api.add_site_visit",
})

export const siteVisitHistoryResource = createResource({
	url: "tq_erphr.pwa_api.get_site_visit_history",
})
