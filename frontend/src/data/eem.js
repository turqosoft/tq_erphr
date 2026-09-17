import { createResource } from "frappe-ui"

export const todayEemResource = createResource({
	url: "tq_erphr.pwa_api.get_today_eem",
	auto: true,
})

export const startTripResource = createResource({
	url: "tq_erphr.pwa_api.start_eem_trip",
})

export const addEemSiteVisitResource = createResource({
	url: "tq_erphr.pwa_api.add_eem_site_visit",
})

export const addEemExpenseResource = createResource({
	url: "tq_erphr.pwa_api.add_eem_expense",
})

export const endTripResource = createResource({
	url: "tq_erphr.pwa_api.end_eem_trip",
})

export const eemHistoryResource = createResource({
	url: "tq_erphr.pwa_api.get_eem_history",
	auto: true,
})

export const eemDetailResource = createResource({
	url: "tq_erphr.pwa_api.get_eem_detail",
})

export const expenseTypesResource = createResource({
	url: "tq_erphr.pwa_api.get_expense_claim_types",
	auto: true,
})

export const customersResource = createResource({
	url: "tq_erphr.pwa_api.get_customers_list",
	auto: true,
})

