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

				<div class="space-y-2">
					<input
						v-model="search"
						type="search"
						placeholder="Search customer, visit, task, serial..."
						class="w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white"
					/>
					<div class="flex items-center gap-2">
						<input v-model="fromDate" type="date" :max="toDate || undefined" class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white" />
						<span class="text-[11px] text-slate-400">to</span>
						<input v-model="toDate" type="date" :min="fromDate || undefined" class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white" />
						<button v-if="hasFilters" type="button" @click="clearFilters" class="text-[11px] font-semibold text-teal-700 px-1">Clear</button>
					</div>
					<p class="text-[10px] text-slate-400">Date range filters by visit date.</p>
				</div>

				<p v-if="!visits.length && !current.loading" class="text-xs text-slate-500 text-center py-10">
					{{ hasFilters ? "No visits match your search." : "No visits yet." }}
				</p>

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

					<div v-if="v.materials?.length" class="rounded-xl bg-amber-50/60 divide-y">
						<p class="px-3 pt-2 text-[10px] font-bold uppercase tracking-wide text-amber-700">Spare parts used</p>
						<div v-for="(m, idx) in v.materials" :key="'m' + idx" class="px-3 py-2">
							<p class="text-xs font-semibold truncate">{{ m.item_code }} × {{ m.qty }} {{ m.uom || "" }}</p>
							<p v-if="m.serial_no" class="text-[11px] text-slate-600 whitespace-pre-line">🔢 Serial No: {{ m.serial_no }}</p>
						</div>
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
import { ref, computed, watch, onMounted } from "vue"
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
const total = computed(() => current.value.data?.total || 0)

// ---- search, date range and paging (10 at a time) ----
const search = ref("")
const fromDate = ref("")
const toDate = ref("")
const PAGE = 10
const limit = ref(PAGE)
const canLoadMore = computed(() => visits.value.length < total.value)
const hasFilters = computed(() => !!(search.value || fromDate.value || toDate.value))

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
function formatDate(s) {
	if (!s) return ""
	const [y, m, d] = String(s).split("-").map(Number)
	if (!y || !m || !d) return s
	return `${String(d).padStart(2, "0")} ${MONTHS[m - 1]} ${y}`
}

function load() {
	current.value.fetch({
		status: filter.value,
		limit: limit.value,
		search: search.value.trim() || undefined,
		from_date: fromDate.value || undefined,
		to_date: toDate.value || undefined,
	})
}
function reload() {
	limit.value = PAGE
	load()
}
function loadMore() {
	limit.value += PAGE
	load()
}
function setFilter(k) {
	filter.value = k
	reload()
}
function clearFilters() {
	search.value = ""
	fromDate.value = ""
	toDate.value = ""
}

let timer
watch(search, () => {
	clearTimeout(timer)
	timer = setTimeout(reload, 400)
})
watch([fromDate, toDate], reload)

onMounted(load)
</script>