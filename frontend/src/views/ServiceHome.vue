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

				<h3 class="text-sm font-bold text-slate-800">Today's Tasks</h3>
				<p v-if="!tasks.length && !serviceTasksResource.loading" class="text-xs text-slate-500 text-center py-8">No tasks assigned for today.</p>
				<ServiceTaskCard v-for="t in tasks" :key="t.name" :task="t" @start="openTask" />
			</div>
		</div>

		<ServiceProfileModal v-model="showProfile" />
		<ServiceVisitModal v-model="showVisit" :task="selected" @done="load" />
		<InstallationNoteModal v-model="showInstall" :task="selected" @done="load" />
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

const route = useRoute()
const router = useRouter()
const employee = computed(() => employeeResource.data)
const tasks = computed(() => serviceTasksResource.data?.tasks || [])
const summary = computed(() => serviceTasksResource.data?.summary || { assigned: 0, completed: 0, pending: 0 })
const pendingSpares = computed(
	() => tasks.value.filter((t) => t.completion_status !== "Fully Completed" && (t.work_done || "").startsWith("Pending Spare Parts")).length
)

const showProfile = ref(false)
const showVisit = ref(false)
const showInstall = ref(false)
const selected = ref(null)

function load() {
	serviceTasksResource.fetch({ include_overdue: 0 })
	checkinStatusResource.fetch()
}

function openTask(t) {
	selected.value = t
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