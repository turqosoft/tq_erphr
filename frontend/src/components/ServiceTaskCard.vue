<template>
	<div class="rounded-2xl bg-white border border-slate-100 p-3.5 space-y-2 shadow-sm">
		<div class="flex items-start justify-between gap-2">
			<div class="min-w-0">
				<p class="text-sm font-bold truncate">{{ task.customer_name }}</p>
				<p class="text-[11px] text-slate-500 truncate">{{ task.item_name }}</p>
			</div>
			<div class="flex flex-col items-end gap-1 flex-shrink-0">
				<span class="text-[10px] font-bold px-2 py-0.5 rounded-full" :class="task.kind === 'installation' ? 'bg-violet-50 text-violet-700' : 'bg-amber-50 text-amber-700'">
					{{ task.kind === "installation" ? task.task_type || "Installation" : task.visit_no ? `Maintenance Visit ${task.visit_no} of ${task.visit_total}` : "Maintenance" }}
				</span>
				<span v-if="task.is_overdue" class="text-[10px] font-bold text-rose-600">Overdue</span>
			</div>
		</div>

		<!-- Maintenance / installation date -->
		<div
			v-if="task.scheduled_date"
			class="flex items-center gap-1.5 text-[11px] font-semibold"
			:class="task.is_overdue ? 'text-rose-600' : 'text-slate-600'"
		>
			<span>📅</span>
			<span>{{ task.kind === "installation" ? "Installation" : "Maintenance" }} date: {{ formatDate(task.scheduled_date) }}</span>
			<span v-if="relativeLabel" class="px-1.5 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[10px] font-bold">{{ relativeLabel }}</span>
		</div>

		<!-- Visit period (maintenance only) -->
		<div
			v-if="task.kind === 'maintenance' && task.start_date && task.end_date"
			class="flex items-center gap-1.5 text-[11px] font-semibold text-slate-600"
		>
			<span>🗓️</span>
			<span>Visit period: {{ formatDate(task.start_date) }} – {{ formatDate(task.end_date) }}</span>
		</div>
		<p v-if="task.sales_invoice" class="text-[11px] font-semibold text-slate-600">🧾 Invoice: {{ task.sales_invoice }}</p>

		<div class="flex items-center gap-2 pt-1">
			<a v-if="task.phone" :href="`tel:${task.phone}`" class="flex-1 text-center text-xs font-semibold py-2 rounded-xl bg-emerald-50 text-emerald-700">📞 Call Customer</a>
			<a v-if="hasPin" :href="mapLink" target="_blank" rel="noopener" class="flex-1 text-center text-xs font-semibold py-2 rounded-xl bg-sky-50 text-sky-700">🧭 Directions</a>
		</div>
				<button
			type="button"
			@click="showDetails = !showDetails"
			class="w-full text-[11px] font-semibold py-1.5 rounded-xl bg-slate-50 text-slate-600 active:scale-95"
		>
			{{ showDetails ? "Hide details ▴" : "View more details ▾" }}
		</button>

		<div v-if="showDetails" class="rounded-xl bg-slate-50 p-3 space-y-1.5 text-[11px] text-slate-600">
			<p><span class="font-semibold text-slate-700">Customer:</span> {{ task.customer_name }}</p>
			<p v-if="task.phone">
				<span class="font-semibold text-slate-700">Phone:</span>
				<a :href="`tel:${task.phone}`" class="text-teal-700 font-semibold">{{ task.phone }}</a>
			</p>
			<p v-if="task.email"><span class="font-semibold text-slate-700">Email:</span> {{ task.email }}</p>
			<p v-if="task.address" class="whitespace-pre-line">
				<span class="font-semibold text-slate-700">Address:</span> {{ task.address }}
			</p>
			<p
				v-if="task.billing_address && task.billing_address !== task.address"
				class="whitespace-pre-line"
			>
				<span class="font-semibold text-slate-700">Billing address:</span> {{ task.billing_address }}
			</p>
			<p v-if="task.territory"><span class="font-semibold text-slate-700">Territory:</span> {{ task.territory }}</p>
		</div>
		<button
			v-if="task.completion_status !== 'Fully Completed'"
			type="button"
			@click="$emit('start', task)"
			class="w-full text-xs font-bold py-2.5 rounded-xl bg-teal-600 text-white active:scale-95"
		>
			{{ task.kind === "installation" ? "Complete Installation" : "Start Visit" }}
		</button>
		<p v-else class="text-center text-xs font-semibold text-emerald-600">✓ Completed</p>
	</div>
</template>

<script setup>
import { ref, computed } from "vue"

const props = defineProps({ task: { type: Object, required: true } })
defineEmits(["start"])
const showDetails = ref(false)
const hasPin = computed(() => {
	const { latitude: la, longitude: lo } = props.task
	return !!(la && lo && Number(la) !== 0 && Number(lo) !== 0)
})
const mapLink = computed(
	() => `https://www.google.com/maps/dir/?api=1&destination=${props.task.latitude},${props.task.longitude}`
)

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

// "2026-09-30" -> "30 Sep 2026"
function formatDate(s) {
	if (!s) return ""
	const [y, m, d] = String(s).split("-").map(Number)
	if (!y || !m || !d) return s
	return `${String(d).padStart(2, "0")} ${MONTHS[m - 1]} ${y}`
}

// Today / Tomorrow / Yesterday next to the date
const relativeLabel = computed(() => {
	const [y, m, d] = String(props.task.scheduled_date || "").split("-").map(Number)
	if (!y || !m || !d) return ""
	const now = new Date()
	const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
	const diff = Math.round((new Date(y, m - 1, d) - today) / 86400000)
	if (diff === 0) return "Today"
	if (diff === 1) return "Tomorrow"
	if (diff === -1) return "Yesterday"
	return ""
})
</script>