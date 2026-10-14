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

			<!-- Outcome -->
			<div class="space-y-2">
				<label class="text-xs font-semibold text-slate-700">Resolution status</label>
				<select v-model="resolution" :class="inputCls">
					<option v-for="r in RESOLUTIONS" :key="r">{{ r }}</option>
				</select>
				<textarea v-model="workDone" rows="2" placeholder="Work done" :class="inputCls"></textarea>
				<input v-model="feedback" placeholder="Customer feedback (optional)" :class="inputCls" />
			</div>

			<!-- Spare parts -->
			<div class="space-y-2">
				<label class="text-xs font-semibold text-slate-700">Spare parts used</label>
				<input v-model="search" placeholder="Search spare part..." :class="inputCls" />
				<div v-if="results.length" class="rounded-xl border border-slate-200 max-h-40 overflow-y-auto divide-y">
					<button
						v-for="it in results"
						:key="it.item_code"
						type="button"
						@click="addItem(it)"
						class="w-full text-left px-3 py-2 text-xs hover:bg-slate-50"
					>
						<span class="font-semibold">{{ it.item_name }}</span>
						<span class="text-slate-400"> · {{ it.item_code }} · {{ formatInr(it.rate) }}</span>
					</button>
				</div>

				<div v-for="(r, i) in rows" :key="r.item_code" class="rounded-xl border border-slate-200 p-2.5 space-y-2">
					<div class="flex items-start justify-between gap-2">
						<p class="text-xs font-bold">{{ r.item_name }}</p>
						<button type="button" @click="rows.splice(i, 1)" class="text-slate-400 text-sm leading-none">✕</button>
					</div>
					<div class="flex items-center gap-2">
						<div class="flex items-center rounded-lg border border-slate-200">
							<button type="button" class="px-2.5 py-1 text-sm" @click="r.qty = Math.max(1, r.qty - 1)">−</button>
							<span class="px-2 text-xs font-semibold min-w-6 text-center">{{ r.qty }}</span>
							<button type="button" class="px-2.5 py-1 text-sm" @click="r.qty++">+</button>
						</div>
						<div class="flex items-center flex-1 rounded-lg border border-slate-200 px-2">
							<span class="text-xs text-slate-500">₹</span>
							<input v-model.number="r.rate" type="number" min="0" step="0.01" class="w-full p-1.5 text-xs outline-none" />
						</div>
						<select v-model="r.billing_type" class="rounded-lg border border-slate-200 p-1.5 text-xs bg-white">
							<option>Free</option>
							<option>Payable</option>
						</select>
					</div>
					<select v-model="r.warehouse" class="w-full rounded-lg border border-slate-200 p-1.5 text-xs bg-white">
						<option value="" disabled>Select warehouse</option>
						<option v-for="w in warehouses" :key="w">{{ w }}</option>
					</select>
					<input v-if="r.has_serial_no" v-model="r.serial_no" placeholder="Serial no(s), one per line or comma separated" class="w-full rounded-lg border border-slate-200 p-1.5 text-xs" />
					<input v-if="r.has_batch_no" v-model="r.batch_no" placeholder="Batch no" class="w-full rounded-lg border border-slate-200 p-1.5 text-xs" />
					<p class="text-right text-[11px] font-semibold text-slate-600">{{ formatInr(r.qty * r.rate) }}</p>
				</div>
				<p v-if="rows.length" class="text-right text-xs font-bold">Total: {{ formatInr(total) }}</p>
			</div>

			<!-- Sign-off -->
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
				{{ submitVisitResource.loading ? "Submitting..." : "Submit Visit" }}
			</button>
			<p v-if="!coords || !signature" class="text-[11px] text-center text-slate-400">Location and customer signature are required.</p>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { call } from "frappe-ui"
import LocationStatus from "@/components/LocationStatus.vue"
import SignaturePad from "@/components/SignaturePad.vue"
import { getCurrentLocation } from "@/utils/location"
import { toast } from "@/utils/toast"
import { submitVisitResource, SPARES_API, formatInr, errorText } from "@/data/crm_support"

const props = defineProps({ modelValue: Boolean, task: Object })
const emit = defineEmits(["update:modelValue", "done"])

const RESOLUTIONS = ["Fully Resolved", "Temporary Fix", "Pending Spare Parts", "Requires Factory Repair"]
const inputCls = "w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white"

const coords = ref(null)
const locating = ref(false)
const resolution = ref(RESOLUTIONS[0])
const workDone = ref("")
const feedback = ref("")
const search = ref("")
const results = ref([])
const rows = ref([])
const signature = ref(null)
const warehouses = ref([])
const defaultWarehouse = ref("")

const total = computed(() => rows.value.reduce((s, r) => s + (Number(r.qty) || 0) * (Number(r.rate) || 0), 0))
const canSubmit = computed(() => !!coords.value && !!signature.value && !submitVisitResource.loading)

async function capture() {
	locating.value = true
	coords.value = await getCurrentLocation()
	locating.value = false
}

async function loadSpares(txt) {
	try {
		const res = await call(SPARES_API, { txt })
		warehouses.value = res.warehouses || []
		defaultWarehouse.value = res.default_warehouse || ""
		return res.items || []
	} catch {
		return []
	}
}

let timer
watch(search, (v) => {
	clearTimeout(timer)
	if (!v || v.length < 2) {
		results.value = []
		return
	}
	timer = setTimeout(async () => (results.value = await loadSpares(v)), 300)
})

function addItem(it) {
	if (!rows.value.find((r) => r.item_code === it.item_code)) {
		rows.value.push({
			item_code: it.item_code,
			item_name: it.item_name,
			uom: it.stock_uom,
			qty: 1,
			rate: it.rate || 0,
			warehouse: defaultWarehouse.value,
			billing_type: "Free",
			serial_no: "",
			batch_no: "",
			has_serial_no: !!it.has_serial_no,
			has_batch_no: !!it.has_batch_no,
		})
	}
	search.value = ""
	results.value = []
}

function close() {
	emit("update:modelValue", false)
}

async function submit() {
	if (!canSubmit.value) return
	try {
		await submitVisitResource.submit({
			data: {
				task: props.task.name,
				resolution_status: resolution.value,
				work_done: workDone.value,
				feedback: feedback.value,
				latitude: coords.value.latitude,
				longitude: coords.value.longitude,
				signature: signature.value,
				materials: rows.value.map((r) => ({
					item_code: r.item_code, qty: r.qty, rate: r.rate, uom: r.uom,
					warehouse: r.warehouse, billing_type: r.billing_type,
					serial_no: r.serial_no, batch_no: r.batch_no,
				})),
			},
		})
		toast.success("Maintenance visit submitted", "Visit Saved")
		emit("done")
		close()
	} catch (err) {
		toast.error(errorText(err), "Could not submit visit")
	}
}

watch(
	() => props.modelValue,
	async (open) => {
		if (!open) return
		coords.value = null
		resolution.value = RESOLUTIONS[0]
		workDone.value = ""
		feedback.value = ""
		search.value = ""
		results.value = []
		rows.value = []
		signature.value = null
		loadSpares("") // fills warehouses + default warehouse
		capture()
	}
)
</script>