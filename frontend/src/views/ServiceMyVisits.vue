<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar page-title="My Visits" :is-refreshing="current.loading" @refresh="load">
				<template #actions><ModeSwitcher /></template>
				<template #profile><ServiceProfileMenu /></template>
			</TopNavBar>

			<div class="p-4 space-y-3">
				<div class="flex rounded-2xl bg-slate-100 p-1 text-[11px] font-semibold">
					<button
						v-for="f in FILTERS"
						:key="f.key"
						type="button"
						@click="setFilter(f.key)"
						class="flex-1 py-2 rounded-xl transition"
						:class="filter === f.key ? 'bg-white text-teal-700 shadow-sm' : 'text-slate-500'"
					>
						{{ f.label }}
					</button>
				</div>

				<p v-if="!visits.length && !current.loading" class="text-xs text-slate-500 text-center py-10">No visits yet.</p>

				<div v-for="v in visits" :key="v.name" class="rounded-2xl bg-white border border-slate-100 p-3.5 space-y-2 shadow-sm">
					<div class="flex items-start justify-between gap-2">
						<div class="min-w-0">
							<p class="text-sm font-bold truncate">{{ v.customer_name }}</p>
							<p class="text-[11px] text-slate-500 truncate">{{ v.name }}</p>
						</div>
						<div class="flex flex-col items-end gap-1 flex-shrink-0">
							<span
								class="text-[10px] font-bold px-2 py-0.5 rounded-full"
								:class="v.docstatus === 0 ? 'bg-slate-100 text-slate-600'
									: v.completion_status === 'Fully Completed' ? 'bg-emerald-50 text-emerald-700'
									: 'bg-amber-50 text-amber-700'"
							>
								{{ v.docstatus === 0 ? "Draft" : v.completion_status }}
							</span>
							<span v-if="v.is_combined_visit" class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-50 text-violet-700">
								Combined · {{ v.tasks.length }} tasks
							</span>
						</div>
					</div>

					<p class="text-[11px] font-semibold text-slate-600">📅 {{ formatDate(v.mntc_date) }}</p>
					<p v-if="v.sales_invoice" class="text-[11px] font-semibold text-slate-600">🧾 Invoice: {{ v.sales_invoice }}</p>

					<div class="rounded-xl bg-slate-50 divide-y">
						<div v-for="t in v.tasks" :key="t.task" class="px-3 py-2">
							<div class="flex items-center justify-between gap-2">
								<p class="text-xs font-semibold truncate">{{ t.item_name }}</p>
								<span class="text-[10px] font-bold" :class="t.status === 'Fully Completed' ? 'text-emerald-600' : 'text-amber-600'">{{ t.status }}</span>
							</div>
							<p class="text-[11px] text-slate-500">🧩 Task: {{ t.task }}</p>
							<p v-if="t.serial_no" class="text-[11px] text-slate-600 whitespace-pre-line">🔢 Serial No: {{ t.serial_no }}</p>
						</div>
					</div>

					<div v-if="v.materials.length" class="text-[11px] text-slate-600 space-y-0.5">
						<p class="font-semibold text-slate-700">Spare parts used</p>
						<p v-for="(m, i) in v.materials" :key="i" class="whitespace-pre-line">
							{{ m.item_code }} × {{ m.qty }}<span v-if="m.serial_no"> · {{ m.serial_no }}</span>
						</p>
					</div>
				</div>

				<button
					v-if="canLoadMore"
					type="button"
					@click="loadMore"
					:disabled="current.loading"
					class="w-full text-xs font-semibold py-2.5 rounded-xl bg-slate-100 text-slate-600 active:scale-95"
				>
					{{ current.loading ? "Loading..." : "Load more" }}
				</button>
			</div>
		</div>

		<ServiceBottomNav active-tab="home" />
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import TopNavBar from "@/components/TopNavBar.vue"
import ServiceBottomNav from "@/components/ServiceBottomNav.vue"
import ModeSwitcher from "@/components/ModeSwitcher.vue"
import ServiceProfileMenu from "@/components/ServiceProfileMenu.vue"
import { myVisitsResources } from "@/data/crm_support"

const FILTERS = [
	{ key: "all", label: "All" },
	{ key: "partial", label: "Partial" },
	{ key: "completed", label: "Completed" },
	{ key: "combined", label: "Combined" },
]
const filter = ref("all")
const current = computed(() => myVisitsResources[filter.value])
const visits = computed(() => current.value.data?.visits || [])

const PAGE = 20
const limit = ref(PAGE)
const canLoadMore = computed(() => visits.value.length >= limit.value)

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
function formatDate(s) {
	if (!s) return ""
	const [y, m, d] = String(s).split("-").map(Number)
	if (!y || !m || !d) return s
	return `${String(d).padStart(2, "0")} ${MONTHS[m - 1]} ${y}`
}

function load() {
	current.value.fetch({ status: filter.value, limit: limit.value })
}
function loadMore() {
	limit.value += PAGE
	load()
}
function setFilter(k) {
	filter.value = k
	limit.value = PAGE
	load()
}

onMounted(load)
</script>