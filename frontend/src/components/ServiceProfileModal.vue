<template>
	<Dialog v-model="open">
		<template #body-title>
			<div class="flex items-center space-x-2.5">
				<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
					</svg>
				</div>
				<h2 class="text-base font-bold text-slate-900">{{ view === "password" ? "Change Password" : "My Profile" }}</h2>
			</div>
		</template>

		<template #body-content>
			<!-- DETAILS -->
			<div v-if="view === 'details'" class="mt-2 space-y-3">
				<div class="flex items-center space-x-3 p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
					<div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-teal-600 to-teal-400 text-white font-bold text-base flex items-center justify-center flex-shrink-0 shadow-sm overflow-hidden">
						<img v-if="employee?.image" :src="employee.image" :alt="employee.employee_name" class="w-full h-full object-cover" />
						<span v-else>{{ getInitials(employee?.employee_name || session.user) }}</span>
					</div>
					<div class="min-w-0 flex-1">
						<h4 class="text-sm font-bold text-slate-900 truncate">{{ employee?.employee_name || session.user }}</h4>
						<p class="text-xs text-slate-500 truncate">{{ employee?.designation || "Service Engineer" }}</p>
						<div class="flex items-center gap-1.5 mt-1">
							<span class="inline-flex px-2 py-0.5 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
								{{ employee?.is_service_supervisor ? "Service Team Lead" : "Service Engineer" }}
							</span>
							<span class="inline-flex px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Active</span>
						</div>
					</div>
				</div>

				<p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider pt-1">Service Details</p>
				<div class="grid grid-cols-2 gap-2 text-xs">
					<div v-for="f in serviceFields" :key="f.label" class="p-3 rounded-2xl bg-slate-50 border border-slate-100" :class="f.wide ? 'col-span-2' : ''">
						<span class="text-[10px] text-slate-400 font-medium block">{{ f.label }}</span>
						<span class="font-bold text-slate-900 truncate block" :class="f.mono ? 'font-mono text-[11px]' : ''">{{ f.value || "-" }}</span>
					</div>
				</div>

				<p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider pt-1">Employee Details</p>
				<div class="grid grid-cols-2 gap-2 text-xs">
					<div v-for="f in employeeFields" :key="f.label" class="p-3 rounded-2xl bg-slate-50 border border-slate-100" :class="f.wide ? 'col-span-2' : ''">
						<span class="text-[10px] text-slate-400 font-medium block">{{ f.label }}</span>
						<span class="font-bold text-slate-900 truncate block" :class="f.mono ? 'font-mono text-[11px]' : ''">{{ f.value || "-" }}</span>
					</div>
				</div>

				<button
					type="button"
					@click="openPassword"
					class="w-full py-2.5 px-3 rounded-2xl bg-slate-50 hover:bg-teal-50 border border-slate-200/80 text-slate-700 text-xs font-semibold flex items-center justify-between"
				>
					<span>Change Password</span>
					<span class="text-slate-400">›</span>
				</button>

				<div v-if="!confirmingLogout">
					<button type="button" @click="confirmingLogout = true" class="w-full py-2.5 rounded-2xl bg-rose-50 text-rose-600 text-xs font-bold">Log out</button>
				</div>
				<div v-else class="rounded-2xl bg-rose-50 border border-rose-200 p-3 space-y-2">
					<p class="text-xs text-rose-700 font-semibold">Log out of MobiBiz?</p>
					<div class="flex gap-2">
						<button type="button" @click="confirmingLogout = false" class="flex-1 py-2 rounded-xl bg-white text-slate-700 text-xs font-semibold border border-slate-200">Cancel</button>
						<button type="button" @click="session.logout.submit()" class="flex-1 py-2 rounded-xl bg-rose-600 text-white text-xs font-bold">Yes, Log out</button>
					</div>
				</div>
			</div>

			<!-- CHANGE PASSWORD -->
			<div v-else class="mt-2 space-y-3">
				<p v-if="pwdError" class="p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">{{ pwdError }}</p>
				<p v-if="pwdSuccess" class="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs">{{ pwdSuccess }}</p>
				<div v-for="f in pwdInputs" :key="f.key" class="space-y-1">
					<label class="block text-xs font-bold text-slate-700">{{ f.label }}</label>
					<input
						v-model="pwd[f.key]"
						type="password"
						:placeholder="f.placeholder"
						class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50/70 focus:bg-white text-slate-900 placeholder-slate-400 text-xs outline-none focus:border-teal-500"
					/>
				</div>
				<div class="flex gap-2 pt-1">
					<button type="button" @click="startView === 'password' ? (open = false) : (view = 'details')" class="flex-1 py-2.5 rounded-xl bg-slate-100 text-slate-700 text-xs font-semibold">Back</button>
					<button
						type="button"
						:disabled="saving"
						@click="submitPassword"
						class="flex-1 py-2.5 rounded-xl bg-teal-600 text-white text-xs font-bold disabled:opacity-60"
					>
						{{ saving ? "Updating..." : "Update Password" }}
					</button>
				</div>
			</div>
		</template>

		<template #actions>
			<div v-if="view === 'details'" class="flex items-center justify-end w-full pt-1">
				<Button variant="solid" @click="open = false" class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl">Close</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { Dialog, Button, call } from "frappe-ui"
import { employeeResource } from "@/data/employee"
import { session } from "@/data/session"

const props = defineProps({ startView: { type: String, default: "details" } })
const open = defineModel()
const employee = computed(() => employeeResource.data)

const view = ref("details")
const confirmingLogout = ref(false)
const saving = ref(false)
const pwdError = ref("")
const pwdSuccess = ref("")
const pwd = ref({ old: "", next: "", confirm: "" })

const pwdInputs = [
	{ key: "old", label: "Current Password", placeholder: "Enter your current password" },
	{ key: "next", label: "New Password", placeholder: "Minimum 6 characters" },
	{ key: "confirm", label: "Confirm New Password", placeholder: "Re-enter the new password" },
]

const serviceFields = computed(() => [
	{ label: "Service Team", value: employee.value?.service_team },
	{ label: "Role", value: employee.value?.is_service_supervisor ? "Team Lead" : "Service Engineer" },
])

const employeeFields = computed(() => {
	const e = employee.value || {}
	return [
		{ label: "Employee ID", value: e.name, mono: true },
		{ label: "Designation", value: e.designation },
		{ label: "Department", value: e.department },
		{ label: "Company", value: e.company },
		{ label: "Reports To", value: e.reports_to || "None" },
		{ label: "Joining Date", value: e.date_of_joining, mono: true },
		{ label: "Mobile Phone", value: e.cell_number, mono: true },
		{ label: "User ID", value: e.user_id || session.user, mono: true },
		{ label: "Email Address", value: e.company_email || e.personal_email || e.user_id, mono: true, wide: true },
	]
})

function getInitials(name) {
	if (!name) return "SE"
	const parts = name.trim().split(" ")
	return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase()
}

function resetPassword() {
	pwd.value = { old: "", next: "", confirm: "" }
	pwdError.value = ""
	pwdSuccess.value = ""
}

function openPassword() {
	resetPassword()
	view.value = "password"
}

async function submitPassword() {
	pwdError.value = ""
	pwdSuccess.value = ""
	const { old, next, confirm } = pwd.value
	if (!old) return (pwdError.value = "Please enter your current password.")
	if (next.length < 6) return (pwdError.value = "New password must be at least 6 characters long.")
	if (next !== confirm) return (pwdError.value = "New password and confirmation do not match.")
	if (next === old) return (pwdError.value = "New password cannot be the same as your current password.")

	saving.value = true
	try {
		const res = await call("tq_erphr.pwa_api.change_user_password", { old_password: old, new_password: next })
		pwdSuccess.value = res?.message || "Password updated successfully."
		pwd.value = { old: "", next: "", confirm: "" }
		setTimeout(() => {
			if (props.startView === "password") open.value = false
			else view.value = "details"
		}, 2000)
	} catch (err) {
		const msg = err?.messages?.[0] || err?.message || "Failed to change password."
		pwdError.value = String(msg).replace(/<[^>]+>/g, "").replace(/^Error:\s*/, "")
	} finally {
		saving.value = false
	}
}

watch(open, (v) => {
	if (v) {
		view.value = props.startView
		confirmingLogout.value = false
		resetPassword()
	}
})
</script>