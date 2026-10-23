<template>
	<div v-if="hasSerial" class="space-y-1.5">
		<input v-model="search" placeholder="Search serial no..." class="w-full rounded-lg border border-slate-200 p-1.5 text-xs" />
		<p v-if="!loading && !options.length" class="text-[11px] text-slate-400">
			{{ search ? "No matching serials" :  "This item with the specified serial no is not in stock in the selected warehouse" }}
		</p>
		<div class="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto">
			<button
				v-for="s in shown"
				:key="s"
				type="button"
				@click="toggle(s)"
				:class="['px-2 py-1 rounded-full text-[11px] border', modelValue.includes(s) ? 'bg-teal-600 text-white border-teal-600' : 'bg-white text-slate-600 border-slate-200']"
			>{{ s }}</button>
		</div>
		<p class="text-[11px] text-slate-500">{{ modelValue.length }} / {{ qty }} selected</p>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { call } from "frappe-ui"
import { SERIALS_API } from "@/data/crm_support"

const props = defineProps({
	itemCode: String,
	warehouse: String,
	qty: Number,
	hasSerial: Boolean,
	modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(["update:modelValue"])

const options = ref([])
const search = ref("")
const loading = ref(false)

// selected serials always stay visible, even when the search hides them
const shown = computed(() => [...new Set([...props.modelValue, ...options.value])])

async function load() {
	if (!props.hasSerial || !props.itemCode || !props.warehouse) return
	loading.value = true
	try {
		const res = await call(SERIALS_API, {
			item_code: props.itemCode,
			warehouse: props.warehouse,
			search: search.value,
		})
		options.value = res.serial_nos || []
	} catch {
		options.value = []
	} finally {
		loading.value = false
	}
}

function toggle(s) {
	const list = [...props.modelValue]
	const i = list.indexOf(s)
	if (i >= 0) list.splice(i, 1)
	else if (list.length < props.qty) list.push(s)
	emit("update:modelValue", list)
}

let timer
watch(search, () => {
	clearTimeout(timer)
	timer = setTimeout(load, 300)
})

watch(() => props.warehouse, () => {
	emit("update:modelValue", [])
	search.value = ""
	load()
})

watch(() => props.qty, (q) => {
	if (props.modelValue.length > q) emit("update:modelValue", props.modelValue.slice(0, q))
})

onMounted(load)
</script>