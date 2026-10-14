<template>
	<div class="relative" ref="rootRef">
		<!-- Avatar button -->
		<button
			type="button"
			@click="isOpen = !isOpen"
			class="flex items-center p-0.5 rounded-full hover:ring-2 hover:ring-teal-400/50 active:scale-95 transition focus:outline-none cursor-pointer"
			title="Account & Profile"
			aria-label="User profile menu"
		>
			<div class="w-8 h-8 rounded-full bg-gradient-to-tr from-teal-600 to-teal-400 text-white font-bold text-xs flex items-center justify-center shadow-sm overflow-hidden ring-2 ring-white">
				<img v-if="employee?.image" :src="employee.image" :alt="employee.employee_name" class="w-full h-full object-cover" />
				<span v-else>{{ getInitials(employee?.employee_name || session.user) }}</span>
			</div>
		</button>

		<!-- Dropdown card -->
		<transition
			enter-active-class="transition duration-150 ease-out"
			enter-from-class="transform scale-95 opacity-0"
			enter-to-class="transform scale-100 opacity-100"
			leave-active-class="transition duration-100 ease-in"
			leave-from-class="transform scale-100 opacity-100"
			leave-to-class="transform scale-95 opacity-0"
		>
			<div v-if="isOpen" class="absolute right-0 mt-2 w-64 bg-white rounded-3xl shadow-2xl border border-slate-200/90 py-1.5 z-50 overflow-hidden">
				<!-- Summary -->
				<div class="px-4 py-3.5 border-b border-slate-100 bg-slate-50/50">
					<div class="flex items-center space-x-2.5">
						<div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-teal-400 text-white font-bold text-xs flex items-center justify-center flex-shrink-0 shadow-sm overflow-hidden">
							<img v-if="employee?.image" :src="employee.image" :alt="employee.employee_name" class="w-full h-full object-cover" />
							<span v-else>{{ getInitials(employee?.employee_name || session.user) }}</span>
						</div>
						<div class="min-w-0 flex-1">
							<p class="text-xs font-bold text-slate-900 truncate">{{ employee?.employee_name || session.user }}</p>
							<p class="text-[10px] text-slate-500 truncate">{{ employee?.company_email || employee?.user_id || session.user }}</p>
							<span class="inline-flex items-center px-1.5 py-0.2 mt-1 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
								{{ employee?.designation || "Service Engineer" }}
							</span>
						</div>
					</div>
				</div>

				<!-- Items -->
				<div class="px-1.5 py-1.5 space-y-0.5">
					<button
						v-for="item in items"
						:key="item.key"
						type="button"
						@click="item.action()"
						class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium transition text-left active:scale-98"
						:class="item.danger ? 'text-rose-600 hover:bg-rose-50 hover:text-rose-700' : 'text-slate-700 hover:bg-teal-50 hover:text-teal-800'"
					>
						<svg class="w-4 h-4" :class="item.danger ? 'text-rose-500' : item.accent ? 'text-teal-600' : 'text-slate-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
						</svg>
						<span>{{ item.label }}</span>
					</button>
				</div>
			</div>
		</transition>

		<!-- Profile details / change password -->
		<ServiceProfileModal v-model="showProfile" />
		<ServiceProfileModal v-model="showPassword" start-view="password" />

		<!-- Check-in logs -->
		<Dialog v-model="showLogs">
			<template #body-title>
				<h2 class="text-base font-bold text-slate-900">Attendance Check-in History</h2>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2 max-h-80 overflow-y-auto pr-1">
					<p v-if="loadingLogs && !logs.length" class="py-6 text-center text-xs text-slate-500">Loading records...</p>
					<p v-else-if="!logs.length" class="py-6 text-center text-xs text-slate-400">No check-in logs found.</p>
					<div
						v-for="log in logs"
						:key="log.name"
						class="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-100 text-xs"
					>
						<div class="flex items-center space-x-3">
							<span class="px-2 py-1 rounded-lg text-[10px] font-bold" :class="log.log_type === 'IN' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'">{{ log.log_type }}</span>
							<p class="font-bold text-slate-900">{{ formatDateTime(log.time) }}</p>
						</div>
						<span class="text-[10px] text-slate-400 font-mono">{{ log.name }}</span>
					</div>
					<button
						v-if="hasMore"
						type="button"
						:disabled="loadingMore"
						@click="loadMoreLogs"
						class="w-full py-2.5 text-xs font-semibold text-teal-700 bg-teal-50 border border-teal-200/80 rounded-2xl"
					>
						{{ loadingMore ? "Loading older logs..." : `View More Logs (Showing ${logs.length})` }}
					</button>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end w-full pt-1">
					<Button variant="solid" @click="showLogs = false" class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl">Close</Button>
				</div>
			</template>
		</Dialog>

		<!-- Logout confirm -->
		<Dialog v-model="showLogout">
			<template #body-title><h2 class="text-base font-bold text-slate-900">Log out</h2></template>
			<template #body-content>
				<p class="mt-2 text-xs text-slate-600">Are you sure you want to log out of MobiBiz?</p>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button variant="subtle" @click="showLogout = false">Cancel</Button>
					<Button variant="solid" class="bg-rose-600 text-white hover:bg-rose-500" @click="session.logout.submit()">Yes, Log out</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { Dialog, Button, call } from "frappe-ui"
import { employeeResource } from "@/data/employee"
import { session } from "@/data/session"
import { toast } from "@/utils/toast"
import ServiceProfileModal from "@/components/ServiceProfileModal.vue"

const router = useRouter()
const employee = computed(() => employeeResource.data)

const rootRef = ref(null)
const isOpen = ref(false)
const showProfile = ref(false)
const showPassword = ref(false)
const showLogs = ref(false)
const showLogout = ref(false)

const logs = ref([])
const loadingLogs = ref(false)
const loadingMore = ref(false)
const hasMore = ref(false)

const ICONS = {
	profile: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
	clock: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
	box: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
	lock: "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z",
	logout: "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1",
}

const items = [
	{ key: "profile", label: "Profile Details", icon: ICONS.profile, action: () => pick(() => (showProfile.value = true)) },
	{ key: "logs", label: "Check-in Logs", icon: ICONS.clock, action: () => pick(openLogs) },
	{ key: "stock", label: "Stock & Inventory", icon: ICONS.box, accent: true, action: () => pick(() => router.push("/stock")) },
	{ key: "password", label: "Change Password", icon: ICONS.lock, action: () => pick(() => (showPassword.value = true)) },
	{ key: "logout", label: "Log out", icon: ICONS.logout, danger: true, action: () => pick(() => (showLogout.value = true)) },
]

function pick(fn) {
	isOpen.value = false
	fn()
}

function getInitials(name) {
	if (!name) return "SE"
	const parts = name.trim().split(" ")
	return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase()
}

function formatDateTime(t) {
	if (!t) return "-"
	const d = new Date(t)
	if (isNaN(d.getTime())) return t
	return d.toLocaleDateString([], { day: "2-digit", month: "short" }) + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

async function openLogs() {
	showLogs.value = true
	loadingLogs.value = true
	try {
		const res = await call("tq_erphr.pwa_api.get_employee_checkin_history", { limit: 10, limit_start: 0 })
		logs.value = res || []
		hasMore.value = logs.value.length === 10
	} catch {
		toast.error("Failed to load check-in history")
	} finally {
		loadingLogs.value = false
	}
}

async function loadMoreLogs() {
	if (loadingMore.value) return
	loadingMore.value = true
	try {
		const res = (await call("tq_erphr.pwa_api.get_employee_checkin_history", { limit: 10, limit_start: logs.value.length })) || []
		logs.value = [...logs.value, ...res]
		if (res.length < 10) hasMore.value = false
	} catch {
		toast.error("Failed to load more check-in logs")
	} finally {
		loadingMore.value = false
	}
}

function onClickOutside(e) {
	if (rootRef.value && !rootRef.value.contains(e.target)) isOpen.value = false
}
function onKeydown(e) {
	if (e.key === "Escape") isOpen.value = false
}

onMounted(() => {
	document.addEventListener("click", onClickOutside)
	document.addEventListener("keydown", onKeydown)
})
onUnmounted(() => {
	document.removeEventListener("click", onClickOutside)
	document.removeEventListener("keydown", onKeydown)
})
</script>