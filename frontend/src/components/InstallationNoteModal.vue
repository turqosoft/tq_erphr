<template>
	<div v-if="modelValue" class="fixed inset-0 z-50 bg-slate-900/50 flex items-end sm:items-center justify-center">
		<div class="bg-white w-full sm:max-w-md max-h-[92vh] overflow-y-auto rounded-t-3xl sm:rounded-3xl p-4 space-y-4">
			<div class="flex items-start justify-between">
				<div class="min-w-0">
					<h2 class="text-base font-bold truncate">{{ task?.customer_name }}</h2>
					<p class="text-[11px] text-slate-500 truncate">{{ task?.item_name }} · {{ task?.name }}</p>
				</div>
				<button type="button" @click="close" class="p-1 text-slate-400 text-xl leading-none">✕</button>
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

			<textarea v-model="notes" rows="2" placeholder="Handover notes" :class="inputCls"></textarea>

			<div class="space-y-1">
				<label class="text-xs font-semibold text-slate-700">Customer signature</label>
				<SignaturePad v-model="signature" />
			</div>

			<button
				type="button"
				:disabled="!canSubmit"
				@click="submit"
				class="w-full py-3 rounded-2xl text-sm font-bold text-white bg-teal-600 disabled:opacity-50 active:scale-95"
			>
				{{ submitInstallationNoteResource.loading ? "Submitting..." : "Submit Installation Note" }}
			</button>
			<p v-if="hint" class="text-[11px] text-center text-slate-400">{{ hint }}</p>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import LocationStatus from "@/components/LocationStatus.vue"
import SignaturePad from "@/components/SignaturePad.vue"
import { getCurrentLocation } from "@/utils/location"
import { toast } from "@/utils/toast"
import { submitInstallationNoteResource, errorText } from "@/data/crm_support"

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

const checklistOk = computed(() => status.value !== "Fully Completed" || checklist.value.every((c) => c.checked))
const canSubmit = computed(
	() => !!coords.value && !!signature.value && checklistOk.value && !submitInstallationNoteResource.loading
)
const hint = computed(() => {
	if (!coords.value) return "Location is required."
	if (!checklistOk.value) return "Tick every checklist item to mark as Fully Completed."
	if (!signature.value) return "Customer signature is required."
	return ""
})

async function capture() {
	locating.value = true
	coords.value = await getCurrentLocation()
	locating.value = false
}

function close() {
	emit("update:modelValue", false)
}

async function submit() {
	if (!canSubmit.value) return
	try {
		await submitInstallationNoteResource.submit({
			data: {
				task: props.task.name,
				completion_status: status.value,
				installed_qty: qty.value,
				serial_no: props.task?.has_serial_no ? serialNo.value : "",
				checklist: checklist.value,
				handover_notes: notes.value,
				latitude: coords.value.latitude,
				longitude: coords.value.longitude,
				signature: signature.value,
			},
		})
		toast.success("Installation note submitted", "Installation Saved")
		emit("done")
		close()
	} catch (err) {
		toast.error(errorText(err), "Could not submit installation note")
	}
}

watch(
	() => props.modelValue,
	(open) => {
		if (!open) return
		coords.value = null
		status.value = "Fully Completed"
		qty.value = Number(props.task?.installed_qty) || 1
		serialNo.value = props.task?.serial_no || ""
		notes.value = ""
		signature.value = null
		checklist.value = CHECKLIST.map((label) => ({ label, checked: false }))
		capture()
	}
)
</script>