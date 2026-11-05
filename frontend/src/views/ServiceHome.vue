<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar page-title="Service Dashboard" :is-refreshing="serviceTasksResource.loading" @refresh="load">
				<template #actions><ModeSwitcher /></template>
				<template #profile><ServiceProfileMenu /></template>
			</TopNavBar>

			<div class="p-4 space-y-4">
				<div class="rounded-3xl bg-gradient-to-tr from-teal-700 to-teal-500 text-white p-4 shadow-sm">
					<p class="text-xs opacity-80">{{ employee?.designation || "Service Engineer" }}</p>
					<h2 class="text-lg font-bold leading-tight">{{ employee?.employee_name }}</h2>
					<p class="text-[11px] opacity-80 mt-0.5">Team: {{ employee?.service_team || "-" }}</p>
					<div class="grid grid-cols-3 gap-2 pt-3 mt-3 border-t border-white/20 text-center">
						<div><p class="text-xl font-bold">{{ summary.assigned }}</p><p class="text-[10px] opacity-80">Assigned Today</p></div>
						<div><p class="text-xl font-bold">{{ summary.completed }}</p><p class="text-[10px] opacity-80">Completed</p></div>
						<div><p class="text-xl font-bold">{{ pendingSpares }}</p><p class="text-[10px] opacity-80">Pending Spares</p></div>
					</div>
				</div>

				<CheckinCard @punched="load" />

				<div>
					<div class="grid grid-cols-2 gap-2">
						<button
							v-for="s in quickServices"
							:key="s.label"
							type="button"
							@click="router.push(s.to)"
							class="bg-white rounded-2xl p-3 text-left shadow-sm border border-slate-100 active:scale-95"
						>
							<div class="w-8 h-8 rounded-full bg-teal-50 text-teal-600 flex items-center justify-center mb-2">
								<component :is="s.icon" class="w-4 h-4" />
							</div>
							<p class="text-xs font-bold text-slate-800">{{ s.label }}</p>
							<p class="text-[10px] text-slate-500">{{ s.hint }}</p>
						</button>
					</div>
				</div>

				<div class="flex items-center justify-between">
					<h3 class="text-sm font-bold text-slate-800">Today's Tasks</h3>
					<button
						v-if="canSelect"
						type="button"
						@click="toggleSelectMode"
						class="text-[11px] font-semibold px-3 py-1.5 rounded-xl"
						:class="selectMode ? 'bg-teal-600 text-white' : 'bg-slate-100 text-slate-600'"
					>
						{{ selectMode ? "Cancel" : "Select tasks" }}
					</button>
				</div>
				<p v-if="!tasks.length && !serviceTasksResource.loading" class="text-xs text-slate-500 text-center py-8">No tasks assigned for today.</p>

				<div v-for="t in tasks" :key="t.name" class="relative">
					<ServiceTaskCard :task="t" :class="selectMode ? 'pointer-events-none' : ''" @start="openTask" />
					<div
						v-if="selectMode"
						@click="togglePick(t)"
						class="absolute inset-0 rounded-2xl"
						:class="[
							isPicked(t) ? 'ring-2 ring-teal-600 bg-teal-50/30' : '',
							isBlocked(t) ? 'bg-white/70 cursor-not-allowed' : 'cursor-pointer',
						]"
					>
						<span
							v-if="!isBlocked(t)"
							class="absolute top-2 right-2 w-5 h-5 rounded-md border-2 flex items-center justify-center text-[11px] text-white"
							:class="isPicked(t) ? 'bg-teal-600 border-teal-600' : 'bg-white border-slate-300'"
						>{{ isPicked(t) ? "✓" : "" }}</span>
					</div>
				</div>
			</div>
		</div>

		<ServiceProfileModal v-model="showProfile" />
		<ServiceVisitModal v-model="showVisit" :task="selected" :tasks="combinedTasks" @done="onVisitDone" />
		<InstallationNoteModal v-model="showInstall" :task="selected" @done="load" />

		<div v-if="selectMode" class="fixed bottom-20 inset-x-0 z-40 px-4">
			<div class="sm:max-w-md mx-auto">
				<button
					type="button"
					:disabled="picked.length < 2"
					@click="openCombined"
					class="w-full py-3 rounded-2xl text-sm font-bold text-white bg-teal-600 disabled:opacity-50 shadow-lg active:scale-95"
				>
					Create combined visit ({{ picked.length }})
				</button>
			</div>
		</div>

		<ServiceBottomNav active-tab="home" />
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { Dialog } from "frappe-ui"
import TopNavBar from "@/components/TopNavBar.vue"
import ServiceBottomNav from "@/components/ServiceBottomNav.vue"
import ModeSwitcher from "@/components/ModeSwitcher.vue"
import ServiceTaskCard from "@/components/ServiceTaskCard.vue"
import ServiceVisitModal from "@/components/ServiceVisitModal.vue"
import InstallationNoteModal from "@/components/InstallationNoteModal.vue"
import CheckinCard from "@/components/CheckinCard.vue"
import { employeeResource } from "@/data/employee"
import { session } from "@/data/session"
import { checkinStatusResource } from "@/data/checkin"
import { serviceTasksResource } from "@/data/crm_support"
import ServiceProfileModal from "@/components/ServiceProfileModal.vue"
import ServiceProfileMenu from "@/components/ServiceProfileMenu.vue"
import { Hammer, ClipboardCheck } from "lucide-vue-next"

const route = useRoute()
const router = useRouter()
const employee = computed(() => employeeResource.data)
const tasks = computed(() => serviceTasksResource.data?.tasks || [])
const summary = computed(() => serviceTasksResource.data?.summary || { assigned: 0, completed: 0, pending: 0 })
const pendingSpares = computed(
	() => tasks.value.filter((t) => t.completion_status !== "Fully Completed" && (t.work_done || "").startsWith("Pending Spare Parts")).length
)

const quickServices = [
	{ label: "Installations", hint: "Status & history", to: "/service/my-installations", icon: Hammer },
	{ label: "Visits", hint: "Status & history", to: "/service/my-visits", icon: ClipboardCheck },
]

const showProfile = ref(false)
const showVisit = ref(false)
const showInstall = ref(false)
const selected = ref(null)

// ---- combined visit selection ----
const selectMode = ref(false)
const picked = ref([])
const combinedTasks = ref([])

const canSelect = computed(() =>
	tasks.value.some((t) => t.kind === "maintenance" && t.completion_status !== "Fully Completed")
)
const pickedTasks = computed(() => tasks.value.filter((t) => picked.value.includes(t.name)))

function isPicked(t) {
	return picked.value.includes(t.name)
}
function isBlocked(t) {
	if (t.kind !== "maintenance" || t.completion_status === "Fully Completed") return true
	const f = pickedTasks.value[0]
	return !!f && !isPicked(t) && (t.customer !== f.customer || (t.address || "") !== (f.address || ""))
}
function togglePick(t) {
	if (isBlocked(t)) return
	picked.value = isPicked(t) ? picked.value.filter((n) => n !== t.name) : [...picked.value, t.name]
}
function toggleSelectMode() {
	selectMode.value = !selectMode.value
	picked.value = []
}
function openCombined() {
	if (picked.value.length < 2) return
	combinedTasks.value = pickedTasks.value
	selected.value = pickedTasks.value[0]
	showVisit.value = true
}
function onVisitDone() {
	selectMode.value = false
	picked.value = []
	combinedTasks.value = []
	load()
}

// ---- loading ----
function load() {
	serviceTasksResource.fetch({ include_overdue: 0 })
	checkinStatusResource.fetch()
}

function openTask(t) {
	selected.value = t
	combinedTasks.value = []
	if (t.kind === "installation") showInstall.value = true
	else showVisit.value = true
}

watch(
	() => route.query.openProfile,
	(v) => {
		if (v) {
			showProfile.value = true
			router.replace({ path: "/service" })
		}
	},
	{ immediate: true }
)

onMounted(load)
</script>