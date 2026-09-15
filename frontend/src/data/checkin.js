import { createResource } from "frappe-ui"

export const checkinStatusResource = createResource({
	url: "tq_erphr.pwa_api.get_employee_checkin_status",
	auto: true,
})

export const checkinHistoryResource = createResource({
	url: "tq_erphr.pwa_api.get_employee_checkin_history",
})

export const addCheckinResource = createResource({
	url: "tq_erphr.pwa_api.add_employee_checkin",
})
