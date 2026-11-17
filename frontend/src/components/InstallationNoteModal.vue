<template>
	<div v-if="modelValue" class="fixed inset-0 z-50 bg-slate-900/50 flex items-end sm:items-center justify-center">
		<div class="bg-white w-full sm:max-w-md max-h-[92vh] overflow-y-auto rounded-t-3xl sm:rounded-3xl p-4 space-y-4">
			<div class="flex items-start justify-between">
				<div class="min-w-0">
					<h2 class="text-base font-bold truncate">{{ task?.customer_name }}</h2>
				</div>
				<button type="button" @click="close" class="p-1 text-slate-400 text-xl leading-none">✕</button>
			</div>

			<div class="-mt-2 rounded-xl bg-slate-50 border border-slate-200 px-3 py-2">
				<p class="text-xs font-semibold">{{ task?.item_name }}</p>
				<p class="text-[11px] text-slate-500">{{ task?.name }}</p>
			</div>

			<LocationStatus :coords="coords" :locating="locating" @retry="capture" />

			<div class="space-y-2">
				<label class="text-xs font-semibold text-slate-700">Completion status</label>
				<select v-model="status" :class="inputCls">
					<option>Fully Completed</option>
					<option>Partially Completed</option>
				</select>
				<div class="flex items-center gap-3">
					<label class="text-xs font-semibold text-slate-700">Installed qty</label>
					<div class="flex items-center rounded-lg border border-slate-200">
						<button type="button" class="px-2.5 py-1 text-sm" @click="qty = Math.max(1, qty - 1)">−</button>
						<span class="px-2 text-xs font-semibold min-w-6 text-center">{{ qty }}</span>
						<button type="button" class="px-2.5 py-1 text-sm" @click="qty++">+</button>
					</div>
				</div>
				<input v-if="task?.has_serial_no" v-model="serialNo" placeholder="Serial no(s) of installed unit" :class="inputCls" />
			</div>

			<div class="space-y-1.5">
				<label class="text-xs font-semibold text-slate-700">Setup checklist</label>
				<label v-for="c in checklist" :key="c.label" class="flex items-center gap-2 text-xs text-slate-700">
					<input type="checkbox" v-model="c.checked" class="rounded" />
					{{ c.label }}
				</label>
			</div>

			<!-- NEW: consumed materials -->
			<SparePartsPicker v-model="materials" />

			<textarea v-model="notes" rows="2" placeholder="Handover notes" :class="inputCls"></textarea>

			<div class="space-y-1">
				<label class="text-xs font-semibold text-slate-700">Customer signature</label>
				<SignaturePad v-model="signature" />
			</div>

			<!-- Save and OTP buttons -->
			<div class="flex gap-2">
				<button
					type="button"
					:disabled="!canSave"
					@click="saveDraft"
					class="flex-1 py-3 rounded-2xl text-sm font-bold border border-teal-600 text-teal-700 disabled:opacity-50 active:scale-95"
				>
					{{ saving ? "Saving..." : "Save" }}
				</button>

				<button
					v-if="otpRequired"
					type="button"
					:disabled="otpLoading || (remaining <= 0 && !canGenerate)"
					@click="onOtpButton"
					class="flex-1 py-3 rounded-2xl text-sm font-bold text-white bg-teal-600 disabled:opacity-50 active:scale-95"
				>
					{{ otpLoading ? "Generating..." : remaining > 0 ? "Enter OTP" : "Generate OTP" }}
				</button>

				<button
					v-else
					type="button"
					:disabled="!canSubmit"
					@click="submit"
					class="flex-1 py-3 rounded-2xl text-sm font-bold text-white bg-teal-600 disabled:opacity-50 active:scale-95"
				>
					{{ submitInstallationNoteResource.loading ? "Submitting..." : "Submit Installation Note" }}
				</button>
			</div>

			<!-- Existing hint -->
			<p v-if="hint" class="text-[11px] text-center text-slate-400">
				{{ hint }}
			</p>

			<!-- OTP popup -->
			<div
				v-if="showOtp"
				class="fixed inset-0 z-[60] bg-slate-900/50 flex items-center justify-center p-4"
			>
				<div class="bg-white w-full max-w-xs rounded-2xl p-4 space-y-3">
					<div class="flex items-start justify-between">
						<h3 class="text-sm font-bold">Customer confirmation code</h3>
						<button
							type="button"
							@click="showOtp = false"
							class="text-slate-400 text-lg leading-none"
						>
							✕
						</button>
					</div>

					<input
						v-model="otpCode"
						inputmode="numeric"
						maxlength="4"
						placeholder="Enter 4-digit code"
						:class="inputCls"
					/>

					<p v-if="remaining > 0" class="text-[11px] text-slate-500">
						Code expires in <span class="font-semibold">{{ timeLeft }}</span>
					</p>

					<p v-else class="text-[11px] text-red-600 font-semibold">
						Code expired. Close this and generate a new one.
					</p>

					<button
						type="button"
						:disabled="!canSubmit"
						@click="submit"
						class="w-full py-3 rounded-2xl text-sm font-bold text-white bg-teal-600 disabled:opacity-50 active:scale-95"
					>
						{{ submitInstallationNoteResource.loading ? "Submitting..." : "Confirm & Submit" }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount } from "vue"
import { call } from "frappe-ui"
import LocationStatus from "@/components/LocationStatus.vue"
import SignaturePad from "@/components/SignaturePad.vue"
import SparePartsPicker from "@/components/SparePartsPicker.vue"
import { getCurrentLocation } from "@/utils/location"
import { toast } from "@/utils/toast"
import {
	submitInstallationNoteResource, INSTALLATION_OTP_GENERATE_API, INSTALLATION_OTP_REQUIRED_API,
	SAVE_INSTALLATION_DRAFT_API, DRAFT_STATUS_API, errorText,
} from "@/data/crm_support"

const props = defineProps({ modelValue: Boolean, task: Object })
const emit = defineEmits(["update:modelValue", "done"])

const inputCls = "w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white"
const CHECKLIST = [
	"Unit unpacked and checked for damage",
	"Installed and mounted correctly",
	"Power and connections tested",
	"Demo given to customer",
	"User manual and warranty card handed over",
]

const coords = ref(null)
const locating = ref(false)
const status = ref("Fully Completed")
const qty = ref(1)
const serialNo = ref("")
const notes = ref("")
const signature = ref(null)
const checklist = ref([])
const materials = ref([])
const otpRequired = ref(false)
const otpSent = ref(false)
const otpCode = ref("")
const otpLoading = ref(false)
const remaining = ref(0)
const draftSaved = ref(false)
const saving = ref(false)
const showOtp = ref(false)

let otpTimer, otpEndsAt = 0

const timeLeft = computed(
	() => `${Math.floor(remaining.value / 60)}:${String(remaining.value % 60).padStart(2, "0")}`
)
const otpReady = computed(
	() => !otpRequired.value || (otpSent.value && remaining.value > 0 && otpCode.value.trim().length === 4)
)

function stopTimer() {
	clearInterval(otpTimer)
	otpTimer = null
}
function startTimer(seconds) {
	stopTimer()
	otpEndsAt = Date.now() + seconds * 1000
	remaining.value = seconds
	otpTimer = setInterval(() => {
		remaining.value = Math.max(0, Math.ceil((otpEndsAt - Date.now()) / 1000))
		if (remaining.value === 0) stopTimer()
	}, 1000)
}
function resetOtp() {
	stopTimer()
	otpSent.value = false
	otpCode.value = ""
	remaining.value = 0
}
onBeforeUnmount(stopTimer)

function buildPayload(final) {
	const payload = {
		task: props.task.name,
		completion_status: status.value,
		installed_qty: qty.value,
		serial_no: props.task?.has_serial_no ? serialNo.value : "",
		checklist: checklist.value,
		handover_notes: notes.value,
		latitude: coords.value.latitude,
		longitude: coords.value.longitude,
		materials: materials.value.map((r) => ({
			item_code: r.item_code, qty: r.qty, rate: r.rate, uom: r.uom,
			warehouse: r.warehouse, billing_type: r.billing_type,
			serial_no: r.serial_no, batch_no: r.batch_no,
		})),
	}
	if (final) payload.signature = signature.value
	return payload
}

async function saveDraft() {
	if (!canSave.value) return
	saving.value = true
	try {
		await call(SAVE_INSTALLATION_DRAFT_API, { data: buildPayload(false) })
		draftSaved.value = true
		toast.success("Installation saved as draft", "Draft Saved")
	} catch (err) {
		toast.error(errorText(err), "Could not save draft")
	} finally {
		saving.value = false
	}
}

async function generateOtp() {
	if (!canGenerate.value) return
	otpLoading.value = true
	try {
		const res = await call(INSTALLATION_OTP_GENERATE_API, { task: props.task.name })
		if (!res.confirmation_required) {
			otpRequired.value = false
			return
		}
		otpCode.value = ""
		otpSent.value = true
		startTimer(res.expires_in || 300)
		showOtp.value = true
		if (res.dev_code) console.log("Installation OTP (dev):", res.dev_code)
	} catch (err) {
		toast.error(errorText(err), "Could not generate OTP")
	} finally {
		otpLoading.value = false
	}
}

function onOtpButton() {
	if (remaining.value > 0) showOtp.value = true
	else generateOtp()
}

function close() {
	resetOtp()
	showOtp.value = false
	emit("update:modelValue", false)
}

async function submit() {
	if (!canSubmit.value) return
	try {
		await submitInstallationNoteResource.submit({
			data: { ...buildPayload(true), ...(otpRequired.value ? { otp: otpCode.value.trim() } : {}) },
		})
		toast.success("Installation note submitted", "Installation Saved")
		emit("done")
		close()
	} catch (err) {
		toast.error(errorText(err), "Could not submit installation note")
	}
}

const checklistOk = computed(() => status.value !== "Fully Completed" || checklist.value.every((c) => c.checked))
const serialsOk = computed(() =>
	materials.value.every((r) => !r.has_serial_no || (r.serial_nos || []).length === Number(r.qty))
)
const baseOk = computed(() => !!coords.value && !!signature.value && checklistOk.value && serialsOk.value)
const canSave = computed(() => !!coords.value && serialsOk.value && !saving.value)
const canGenerate = computed(() => draftSaved.value && baseOk.value && !otpLoading.value)
const canSubmit = computed(() => baseOk.value && otpReady.value && !submitInstallationNoteResource.loading)
const hint = computed(() => {
	if (!coords.value) return "Location is required."
	if (!checklistOk.value) return "Tick every checklist item to mark as Fully Completed."
	if (!serialsOk.value) return "Select serial no(s) for every spare part."
	if (!signature.value) return "Customer signature is required."
	if (otpRequired.value && !draftSaved.value) return "Save the installation first, then generate the OTP."
	return ""
})

async function capture() {
	locating.value = true
	coords.value = await getCurrentLocation()
	locating.value = false
}


watch(
	() => props.modelValue,
	async (open) => {
		if (!open) return
		coords.value = null
		status.value = "Fully Completed"
		qty.value = Number(props.task?.installed_qty) || 1
		serialNo.value = (props.task?.serial_no || "")
			.split(/[\n,]+/)
			.map((s) => s.trim())
			.filter(Boolean)
			.join(", ")
		notes.value = ""
		signature.value = null
		checklist.value = CHECKLIST.map((label) => ({ label, checked: false }))
		materials.value = []
		draftSaved.value = false
		showOtp.value = false
		capture()
		resetOtp()
		otpRequired.value = false
		try {
			otpRequired.value = !!(await call(INSTALLATION_OTP_REQUIRED_API)).required
		} catch {}
		try {
			const st = await call(DRAFT_STATUS_API, { task: props.task.name, kind: "installation" })
			if (st.draft) {
				draftSaved.value = true
				const f = st.form || {}
				if (f.completion_status) status.value = f.completion_status
				if (f.installed_qty) qty.value = Number(f.installed_qty)
				if (f.serial_no) serialNo.value = f.serial_no
				notes.value = f.handover_notes || ""
				const done = new Set(f.checked || [])
				checklist.value = CHECKLIST.map((label) => ({ label, checked: done.has(label) }))
				materials.value = f.materials || []
				if (st.pending) {
					otpSent.value = true
					startTimer(st.remaining)
				}
			}
		} catch {}
	}
)
</script>