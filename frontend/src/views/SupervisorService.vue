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
						<p v-else-if="!openTasks.length" class="text-[11px] text-slate-400">No open tasks.</p>
						<div v-for="t in openTasks" :key="t.name" class="rounded-xl border border-slate-100 p-2.5 flex items-center justify-between gap-2">
							<div class="min-w-0">
								<p class="text-xs font-semibold truncate">{{ t.customer_name }}</p>
								<p class="text-[10px] text-slate-500 truncate">{{ t.item_name }} · {{ t.completion_status }}</p>
							</div>
							<button type="button" @click="startReassign(t)" class="text-[11px] font-bold px-2.5 py-1.5 rounded-lg bg-amber-50 text-amber-700 flex-shrink-0">Re-assign</button>
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
const otherEngineers = computed(() => engineers.value.filter((e) => e.team !== reassigning.value?.service_engineer))

const statusClass = (s) =>
	s === "On Site" ? "bg-emerald-50 text-emerald-700" : s === "In Transit" ? "bg-amber-50 text-amber-700" : "bg-slate-100 text-slate-500"

function load() {
	supervisorDashboardResource.fetch()
	if (open.value) loadTasks(open.value)
}

async function loadTasks(team) {
	loadingTasks.value = true
	try {
		const res = await call(ENGINEER_TASKS_API, { engineer: team })
		openTasks.value = (res.tasks || []).filter((t) => t.completion_status !== "Fully Completed")
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