import { createResource } from "frappe-ui"

const API = "tq_erphr.pwa_crm_api"

// `cache` keeps the last result so the task list still opens with no signal
export const serviceTasksResource = createResource({
	url: `${API}.get_engineer_tasks`,
	cache: "tq_erphr:service_tasks",
})

export const serviceVisitsResources = Object.fromEntries(
	["pending", "completed", "spares"].map((s) => [
		s,
		createResource({ url: `${API}.get_service_visits`, cache: `tq_erphr:service_visits_${s}` }),
	])
)

export const supervisorDashboardResource = createResource({
	url: `${API}.get_supervisor_service_dashboard`,
	cache: "tq_erphr:service_supervisor",
})

export const submitVisitResource = createResource({ url: `${API}.submit_maintenance_visit` })
export const submitInstallationNoteResource = createResource({ url: `${API}.submit_installation_note` })
export const reassignTaskResource = createResource({ url: `${API}.reassign_task` })

export const SPARES_API = `${API}.search_spare_items`
export const SERIALS_API = `${API}.get_available_serial_nos`
export const ENGINEER_TASKS_API = `${API}.get_engineer_tasks`

export function mapsUrl(address) {
	return address ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}` : null
}

export function formatInr(n) {
	return "₹" + Number(n || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function errorText(err) {
	const raw = err?.messages?.[0] || err?.message || "Something went wrong"
	return String(raw).replace(/<[^>]+>/g, "")
}

export const VISIT_TABS = [
	{ key: "upcoming", label: "Upcoming", source: "pending", filter: (t) => !t.is_overdue },
	{ key: "overdue", label: "Pending", source: "pending", filter: (t) => t.is_overdue },
	{ key: "completed", label: "Completed", source: "completed", filter: () => true },
	{ key: "spares", label: "Requires Spares", source: "spares", filter: () => true },
]

export function visitsForTab(tab, tasks) {
	return (tasks || []).filter(tab.filter)
}