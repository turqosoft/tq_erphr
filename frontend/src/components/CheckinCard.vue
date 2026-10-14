<template>
	<div>
		<div class="bg-white rounded-3xl p-4 sm:p-5 shadow-sm border border-slate-100 space-y-4 relative overflow-hidden">
			<!-- Clock & status -->
			<div class="flex items-start justify-between">
				<div>
					<span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{{ dateText }}</span>
					<div class="text-2xl font-black tracking-tight text-slate-900 font-mono mt-0.5">{{ timeText }}</div>
				</div>
				<div class="flex flex-col items-end">
					<span
						v-if="isCheckedIn"
						class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200/80"
					>
						<span class="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
						Checked In
					</span>
					<span
						v-else
						class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200"
					>
						<span class="w-2 h-2 rounded-full bg-slate-400 mr-1.5"></span>
						Checked Out
					</span>
					<span class="text-[10px] text-slate-400 mt-1 font-medium">{{ lastPunchSummary }}</span>
				</div>
			</div>

			<!-- Punch button -->
			<div class="pt-1">
				<button
					@click="promptPunch"
					:disabled="isSubmitting || isAcquiringGps"
					class="w-full py-3.5 px-4 rounded-2xl font-bold text-sm flex items-center justify-center space-x-2.5 transition-all transform active:scale-[0.98] focus:outline-none shadow-md text-white"
					:class="[
						nextAction === 'IN'
							? 'bg-gradient-to-r from-teal-600 to-teal-500 shadow-teal-600/25'
							: 'bg-gradient-to-r from-amber-500 to-amber-600 shadow-amber-500/25',
						isSubmitting ? 'opacity-80 cursor-wait' : '',
					]"
				>
					<svg v-if="isSubmitting" class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					<svg v-else-if="nextAction === 'IN'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
					</svg>
					<svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
					</svg>
					<span>
						{{ isSubmitting ? (nextAction === 'IN' ? 'Recording Check In...' : 'Recording Check Out...') : (nextAction === 'IN' ? 'Check In Now' : 'Check Out Now') }}
					</span>
				</button>

				<!-- GPS + logs link -->
				<div class="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
					<div class="flex items-center space-x-1.5 truncate max-w-[220px]">
						<svg class="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
						</svg>
						<span class="truncate">{{ gpsText }}</span>
					</div>
					<button type="button" @click="isPunchesExpanded = !isPunchesExpanded" class="text-teal-700 font-bold flex items-center space-x-1">
						<span>{{ isPunchesExpanded ? "Hide Logs" : "Today's Logs" }}</span>
						<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': isPunchesExpanded }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
						</svg>
					</button>
				</div>
			</div>

			<!-- Today's logs -->
			<div v-if="isPunchesExpanded" class="pt-2 border-t border-slate-100">
				<div class="flex items-center justify-between mb-2">
					<span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Today's Attendance</span>
					<span class="text-[10px] text-slate-400 font-medium">{{ todayCheckins.length }} {{ todayCheckins.length === 1 ? "record" : "records" }}</span>
				</div>
				<div v-if="todayCheckins.length" class="space-y-1.5 max-h-36 overflow-y-auto pr-1">
					<div v-for="log in todayCheckins" :key="log.name" class="flex items-center space-x-2 px-3 py-2 rounded-2xl bg-slate-50 border border-slate-100 text-xs">
						<span class="px-2 py-0.5 rounded-lg text-[10px] font-bold" :class="log.log_type === 'IN' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'">{{ log.log_type }}</span>
						<span class="font-bold text-slate-800">{{ formatLogTime(log.time) }}</span>
					</div>
				</div>
				<div v-else class="text-center py-2 text-[11px] text-slate-400 italic">No check-in entries logged yet today.</div>
			</div>
		</div>

		<!-- GPS overlay -->
		<div v-if="isAcquiringGps" class="fixed inset-0 z-50 bg-slate-900/50 flex items-center justify-center p-6">
			<div class="bg-white rounded-3xl p-6 text-center max-w-xs w-full space-y-1">
				<h3 class="text-sm font-bold">Fetching Location...</h3>
				<p class="text-[11px] text-slate-500">Please hold on while we get your current location...</p>
			</div>
		</div>

		<!-- Confirm punch -->
		<Dialog v-model="showConfirm">
			<template #body-title>
				<h2 class="text-base font-bold text-slate-900">Confirm {{ nextAction === "IN" ? "Check In" : "Check Out" }}</h2>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-3">
					<p class="text-xs text-slate-600">
						Are you sure you want to <strong class="text-slate-900">{{ nextAction === "IN" ? "Check In" : "Check Out" }}</strong> now?
					</p>
					<div class="bg-slate-50 rounded-2xl p-3.5 border border-slate-100 space-y-2 text-xs">
						<div class="flex justify-between py-0.5 border-b border-slate-100">
							<span class="text-slate-500 font-medium">Punch Time</span>
							<span class="font-bold font-mono text-slate-900">{{ timeText }}</span>
						</div>
						<div class="flex justify-between py-0.5 border-b border-slate-100">
							<span class="text-slate-500 font-medium">Date</span>
							<span class="font-bold text-slate-900">{{ dateText }}</span>
						</div>
						<div class="flex justify-between py-0.5">
							<span class="text-slate-500 font-medium">GPS Location</span>
							<span class="font-bold text-slate-900">{{ gpsText }}</span>
						</div>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button variant="subtle" :disabled="isSubmitting" @click="showConfirm = false">Cancel</Button>
					<Button
						variant="solid"
						:loading="isSubmitting"
						@click="confirmPunch"
						class="text-white"
						:class="nextAction === 'IN' ? 'bg-teal-600 hover:bg-teal-500' : 'bg-amber-600 hover:bg-amber-500'"
					>
						{{ nextAction === "IN" ? "Yes, Check In" : "Yes, Check Out" }}
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- GPS permission help -->
		<Dialog v-model="showLocationHelp">
			<template #body-title><h2 class="text-base font-bold text-slate-900">Location Required</h2></template>
			<template #body-content>
				<p class="mt-2 text-xs text-slate-600 leading-relaxed">
					We could not get your location. Turn on GPS and allow location access for this site, then try again.
				</p>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button variant="subtle" @click="showLocationHelp = false">Close</Button>
					<Button variant="solid" class="bg-teal-600 text-white" @click="retry">Try Again</Button>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { Dialog, Button } from "frappe-ui"
import { checkinStatusResource, addCheckinResource } from "@/data/checkin"
import { getCurrentLocation } from "@/utils/location"
import { detectDeviceDetails } from "@/utils/device"
import { toast } from "@/utils/toast"

const emit = defineEmits(["punched"])

const currentTime = ref(new Date())
let timer = null
const isPunchesExpanded = ref(false)
const isSubmitting = ref(false)
const isAcquiringGps = ref(false)
const showConfirm = ref(false)
const showLocationHelp = ref(false)
const gpsText = ref("GPS Ready")
const coords = ref(null)

const timeText = computed(() =>
	currentTime.value.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
)
const dateText = computed(() =>
	currentTime.value.toLocaleDateString([], { weekday: "short", day: "numeric", month: "short", year: "numeric" })
)

const status = computed(() => checkinStatusResource.data || {})
const lastCheckin = computed(() => status.value.last_checkin)
const isCheckedIn = computed(() => lastCheckin.value && lastCheckin.value.log_type === "IN")
const nextAction = computed(() => status.value.next_action || "IN")
const todayCheckins = computed(() => status.value.today_checkins || [])

function formatLogTime(t) {
	if (!t) return "-"
	const d = new Date(t)
	return isNaN(d.getTime()) ? t : d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

const lastPunchSummary = computed(() => {
	if (!lastCheckin.value) return "No recent punch"
	return `${lastCheckin.value.log_type === "IN" ? "In" : "Out"} at ${formatLogTime(lastCheckin.value.time)}`
})

async function promptPunch() {
	if (isSubmitting.value || isAcquiringGps.value) return
	isAcquiringGps.value = true
	try {
		const c = await getCurrentLocation()
		if (!c || (!c.latitude && !c.longitude)) {
			gpsText.value = "📍 GPS not enabled"
			showLocationHelp.value = true
			return
		}
		coords.value = c
		gpsText.value = "📍 Location Acquired"
		showConfirm.value = true
	} finally {
		isAcquiringGps.value = false
	}
}

function retry() {
	showLocationHelp.value = false
	promptPunch()
}

async function confirmPunch() {
	if (isSubmitting.value || !coords.value) return
	const action = nextAction.value
	isSubmitting.value = true
	try {
		const dev = detectDeviceDetails()
		await addCheckinResource.submit({
			log_type: action,
			latitude: coords.value.latitude,
			longitude: coords.value.longitude,
			device_id: dev.shortDeviceId,
			remarks: dev.remarks,
		})
		toast.success(`Punch ${action} recorded successfully!`, "Attendance Updated")
		showConfirm.value = false
		await checkinStatusResource.fetch()
		emit("punched")
	} catch (err) {
		toast.error(err.messages?.[0] || err.message || "Failed to record check-in.", "Punch Failed")
	} finally {
		isSubmitting.value = false
	}
}

onMounted(() => {
	timer = setInterval(() => (currentTime.value = new Date()), 1000)
})
onUnmounted(() => clearInterval(timer))
</script>