<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar page-title="Team Visits" :is-refreshing="supervisorDashboardResource.loading" @refresh="load">
				<template #actions><ModeSwitcher /></template>
			</TopNavBar>

			<div class="p-4 space-y-3">
				<div class="grid grid-cols-3 gap-2 text-center">
					<div v-for="s in stats" :key="s.label" class="rounded-2xl bg-white border border-slate-100 p-3">
						<p class="text-xl font-bold text-teal-700">{{ s.value }}</p>
						<p class="text-[10px] text-slate-500">{{ s.label }}</p>
					</div>
				</div>

				<p v-if="!engineers.length && !supervisorDashboardResource.loading" class="text-xs text-slate-500 text-center py-10">No engineers in your team.</p>

				<div v-for="e in engineers" :key="e.team" class="rounded-2xl bg-white border border-slate-100 p-3.5 space-y-2 shadow-sm">
					<div class="flex items-start justify-between gap-2">
						<div class="min-w-0">
							<p class="text-sm font-bold truncate">{{ e.employee_name }}</p>
							<p class="text-[11px] text-slate-500 truncate">{{ e.designation || e.team }}</p>
						</div>
						<span class="text-[10px] font-bold px-2 py-0.5 rounded-full flex-shrink-0" :class="statusClass(e.status)">{{ e.status }}</span>
					</div>
					<p class="text-[11px] text-slate-600">
						Assigned {{ e.assigned }} · Done {{ e.completed }} · Pending {{ e.pending }}
					</p>
					<div class="flex gap-2">
						<a v-if="e.phone" :href="`tel:${e.phone}`" class="flex-1 text-center text-xs font-semibold py-2 rounded-xl bg-emerald-50 text-emerald-700">📞 Call {{ e.employee_name }}</a>
						<button type="button" @click="toggle(e)" class="flex-1 text-xs font-semibold py-2 rounded-xl bg-slate-100 text-slate-700">
							{{ open === e.team ? "Hide tasks" : "View tasks" }}
						</button>
					</div>

					<div v-if="open === e.team" class="space-y-2 pt-1">
						<p v-if="loadingTasks" class="text-[11px] text-slate-400">Loading...</p>
						<p v-else-if="!openTasks.length" class="text-[11px] text-slate-400">No tasks.</p>
						<div v-for="t in openTasks" :key="t.name" class="rounded-xl border border-slate-100 p-2.5 flex items-center justify-between gap-2">
							<div class="min-w-0">
								<p class="text-xs font-semibold truncate">{{ t.customer_name }}</p>
								<p class="text-[10px] text-slate-500 truncate">{{ t.item_name }} · {{ t.name }}</p>
								<div class="flex flex-wrap gap-1 mt-1">
									<span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full" :class="t.kind === 'installation' ? 'bg-indigo-50 text-indigo-700' : 'bg-sky-50 text-sky-700'">
										{{ t.kind === "installation" ? "Installation" : "Maintenance" }}
									</span>
									<span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full" :class="taskStatusClass(t)">
										{{ t.is_overdue ? "Overdue" : t.completion_status }}
									</span>
								</div>
							</div>
								<div class="flex items-center gap-1.5 flex-shrink-0">
								<div class="relative group">
									<button type="button" @click="viewing = t" class="w-8 h-8 flex items-center justify-center rounded-lg bg-teal-50 text-teal-700 active:bg-teal-100" aria-label="View details">
										<svg xmlns="http://www.w3.org/2000/svg" class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
											<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" />
											<circle cx="12" cy="12" r="3" />
										</svg>
									</button>
									<span class="pointer-events-none absolute bottom-full right-0 mb-1 hidden group-hover:block whitespace-nowrap rounded-md bg-slate-800 px-2 py-1 text-[10px] font-medium text-white shadow">
										View details
									</span>
								</div>
								<button v-if="t.completion_status !== 'Fully Completed'" type="button" @click="startReassign(t)" class="text-[11px] font-bold px-2.5 py-1.5 rounded-lg bg-amber-50 text-amber-700">Re-assign</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Re-assign sheet -->
		<div v-if="reassigning" class="fixed inset-0 z-50 bg-slate-900/50 flex items-end sm:items-center justify-center">
			<div class="bg-white w-full sm:max-w-md rounded-t-3xl sm:rounded-3xl p-4 space-y-3">
				<h3 class="text-sm font-bold">Re-assign task</h3>
				<p class="text-xs text-slate-500">{{ reassigning.customer_name }} · {{ reassigning.item_name }}</p>
				<select v-model="target" class="w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white">
					<option value="" disabled>Select engineer</option>
					<option v-for="e in otherEngineers" :key="e.team" :value="e.team">{{ e.employee_name }} ({{ e.status }})</option>
				</select>
				<div class="flex gap-2">
					<button type="button" @click="reassigning = null" class="flex-1 py-2.5 rounded-xl bg-slate-100 text-sm font-semibold">Cancel</button>
					<button type="button" :disabled="!target || reassignTaskResource.loading" @click="confirmReassign" class="flex-1 py-2.5 rounded-xl bg-teal-600 text-white text-sm font-bold disabled:opacity-50">Assign</button>
				</div>
			</div>
		</div>
		<!-- Task details popup -->
		<div v-if="viewing" class="fixed inset-0 z-50 bg-slate-900/50 flex items-end sm:items-center justify-center" @click.self="viewing = null">
			<div class="bg-white w-full sm:max-w-md rounded-t-3xl sm:rounded-3xl p-4 space-y-3 max-h-[85vh] overflow-y-auto">
				<div class="flex items-start justify-between gap-2">
					<div class="min-w-0">
						<h3 class="text-sm font-bold truncate">{{ viewing.customer_name }}</h3>
						<div class="flex flex-wrap gap-1 mt-1">
							<span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full" :class="viewing.kind === 'installation' ? 'bg-indigo-50 text-indigo-700' : 'bg-sky-50 text-sky-700'">
								{{ viewing.kind === "installation" ? "Installation" : "Maintenance" }}
							</span>
							<span class="text-[9px] font-bold px-1.5 py-0.5 rounded-full" :class="taskStatusClass(viewing)">
								{{ viewing.is_overdue ? "Overdue" : viewing.completion_status }}
							</span>
						</div>
					</div>
				<button type="button" @click="viewing = null" class="text-slate-400 text-lg leading-none" aria-label="Close">✕</button>
				</div>

				<div class="divide-y divide-slate-100">
					<div v-for="r in detailRows" :key="r[0]" class="flex justify-between gap-3 py-1.5 text-xs">
						<span class="text-slate-500 flex-shrink-0">{{ r[0] }}</span>
						<span class="font-medium text-right break-words min-w-0">{{ r[1] }}</span>
					</div>
				</div>

				<button type="button" @click="viewing = null" class="w-full py-2.5 rounded-xl bg-slate-100 text-sm font-semibold">Close</button>
			</div>
		</div>
		<ServiceBottomNav active-tab="team" />
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { call } from "frappe-ui"
import TopNavBar from "@/components/TopNavBar.vue"
import ServiceBottomNav from "@/components/ServiceBottomNav.vue"
import ModeSwitcher from "@/components/ModeSwitcher.vue"
import { supervisorDashboardResource, reassignTaskResource, ENGINEER_TASKS_API, errorText } from "@/data/crm_support"
import { toast } from "@/utils/toast"

const data = computed(() => supervisorDashboardResource.data || {})
const engineers = computed(() => data.value.engineers || [])
const stats = computed(() => [
	{ label: "Assigned", value: data.value.totals?.assigned ?? 0 },
	{ label: "Completed", value: data.value.totals?.completed ?? 0 },
	{ label: "Pending", value: data.value.totals?.pending ?? 0 },
])

const open = ref(null)
const openTasks = ref([])
const loadingTasks = ref(false)
const reassigning = ref(null)
const target = ref("")
const viewing = ref(null)
const otherEngineers = computed(() => engineers.value.filter((e) => e.team !== reassigning.value?.service_engineer))

const statusClass = (s) =>
	s === "On Site" ? "bg-emerald-50 text-emerald-700" : s === "In Transit" ? "bg-amber-50 text-amber-700" : "bg-slate-100 text-slate-500"

const taskStatusClass = (t) =>
	t.is_overdue ? "bg-red-50 text-red-700"
	: t.completion_status === "Fully Completed" ? "bg-emerald-50 text-emerald-700"
	: "bg-amber-50 text-amber-700"
const detailRows = computed(() => {
	const t = viewing.value
	if (!t) return []
	return [
		["Task", t.name],
		["Item", t.item_name],
		["Serial no", (t.serial_no || "").split(/[\s,]+/).filter(Boolean).join(", ")],
		["Scheduled", t.scheduled_date],
		["Started", t.start_date],
		["Ended", t.end_date],
		["Visit", t.visit_no ? `${t.visit_no} of ${t.visit_total}` : null],
		["Installed qty", t.installed_qty],
		["Phone", t.phone],
		["Email", t.email],
		["Address", t.address],
		["Territory", t.territory],
		["Sales invoice", t.sales_invoice],
		["Work done", t.work_done],
	].filter((r) => r[1])
})
function load() {
	supervisorDashboardResource.fetch()
	if (open.value) loadTasks(open.value)
}

async function loadTasks(team) {
	loadingTasks.value = true
	try {
		const res = await call(ENGINEER_TASKS_API, { engineer: team })
		openTasks.value = res.tasks || []
	} catch (err) {
		toast.error(errorText(err), "Could not load tasks")
	} finally {
		loadingTasks.value = false
	}
}

function toggle(e) {
	if (open.value === e.team) {
		open.value = null
		return
	}
	open.value = e.team
	loadTasks(e.team)
}

function startReassign(t) {
	reassigning.value = t
	target.value = ""
}

async function confirmReassign() {
	try {
		await reassignTaskResource.submit({
			doctype: reassigning.value.doctype,
			task: reassigning.value.name,
			new_engineer: target.value,
		})
		toast.success("Task re-assigned", "Done")
		reassigning.value = null
		load()
	} catch (err) {
		toast.error(errorText(err), "Could not re-assign")
	}
}

onMounted(load)
</script>