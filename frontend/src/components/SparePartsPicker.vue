<template>
	<div class="space-y-2">
		<label class="text-xs font-semibold text-slate-700">Consumed materials</label>
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
			<SerialPicker
				v-if="r.has_serial_no"
				:model-value="r.serial_nos"
				@update:modelValue="(v) => { r.serial_nos = v; r.serial_no = v.join('\n') }"
				:item-code="r.item_code"
				:warehouse="r.warehouse"
				:qty="r.qty"
				:has-serial="r.has_serial_no"
			/>
			<input v-if="r.has_batch_no" v-model="r.batch_no" placeholder="Batch no" class="w-full rounded-lg border border-slate-200 p-1.5 text-xs" />
			<p class="text-right text-[11px] font-semibold text-slate-600">{{ formatInr(r.qty * r.rate) }}</p>
		</div>
		<p v-if="rows.length" class="text-right text-xs font-bold">Total: {{ formatInr(total) }}</p>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { call } from "frappe-ui"
import SerialPicker from "@/components/SerialPicker.vue"
import { SPARES_API, formatInr } from "@/data/crm_support"

const rows = defineModel({ default: () => [] })
const inputCls = "w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white"

const search = ref("")
const results = ref([])
const warehouses = ref([])
const defaultWarehouse = ref("")

const total = computed(() => rows.value.reduce((s, r) => s + (Number(r.qty) || 0) * (Number(r.rate) || 0), 0))

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
			serial_nos: [],
			batch_no: "",
			has_serial_no: !!it.has_serial_no,
			has_batch_no: !!it.has_batch_no,
		})
	}
	search.value = ""
	results.value = []
}

onMounted(() => loadSpares("")) // fills warehouses and the default warehouse
</script>