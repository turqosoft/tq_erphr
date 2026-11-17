<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<header
				class="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 pt-3 pb-3 shadow-2xs">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-2.5">
						<button type="button" @click="goBack"
							class="w-9 h-9 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition-colors cursor-pointer"
							title="Go Back">
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
									d="M15 19l-7-7 7-7" />
							</svg>
						</button>
						<div class="min-w-0">
							<h1 class="text-base font-black text-slate-900 leading-tight truncate">My Visits</h1>
							<p class="text-[11px] text-teal-700 font-medium truncate">Status & history</p>
						</div>
					</div>

					<button type="button" @click="load" :disabled="current.loading"
						class="w-9 h-9 rounded-2xl bg-teal-50 hover:bg-teal-100 text-teal-700 border border-teal-200/80 flex items-center justify-center transition-colors cursor-pointer"
						title="Refresh">
						<svg class="w-4 h-4 transition-transform duration-500"
							:class="{ 'animate-spin': current.loading }" fill="none" viewBox="0 0 24 24"
							stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
					</button>
				</div>
			</header>

			<div class="p-4 space-y-3">
				<div class="flex rounded-2xl bg-slate-100 p-1 text-[11px] font-semibold">
					<button v-for="f in FILTERS" :key="f.key" type="button" @click="setFilter(f.key)"
						class="flex-1 py-2 rounded-xl transition"
						:class="filter === f.key ? 'bg-white text-teal-700 shadow-sm' : 'text-slate-500'">
						{{ f.label }}
					</button>
				</div>

				<div class="space-y-2">
					<input v-model="search" type="search" placeholder="Search customer, visit, task, serial..."
						class="w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white" />
					<div class="flex items-center gap-2">
						<input v-model="fromDate" type="date" :max="toDate || undefined"
							class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white" />
						<span class="text-[11px] text-slate-400">to</span>
						<input v-model="toDate" type="date" :min="fromDate || undefined"
							class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white" />
						<button v-if="hasFilters" type="button" @click="clearFilters"
							class="text-[11px] font-semibold text-teal-700 px-1">Clear</button>
					</div>
					<p class="text-[10px] text-slate-400">Date range filters by visit date.</p>
				</div>

				<p v-if="!visits.length && !current.loading" class="text-xs text-slate-500 text-center py-10">
					{{ hasFilters ? "No visits match your search." : "No visits yet." }}
				</p>

				<div v-for="v in visits" :key="v.name"
					class="rounded-2xl bg-white border border-slate-100 p-3.5 space-y-2 shadow-sm">
					<!-- Always visible -->
					<div class="flex items-start justify-between gap-2">
						<div class="min-w-0">
							<p class="text-sm font-bold truncate">{{ v.customer }}</p>
							<p class="text-[11px] text-slate-500 truncate">{{ v.name }}</p>
						</div>
						<div class="flex flex-col items-end gap-1 flex-shrink-0">
							<span class="text-[10px] font-bold px-2 py-0.5 rounded-full" :class="v.docstatus === 0 ? 'bg-slate-100 text-slate-600'
								: v.completion_status === 'Fully Completed' ? 'bg-emerald-50 text-emerald-700'
									: 'bg-amber-50 text-amber-700'">
								{{ v.docstatus === 0 ? "Draft" : v.completion_status }}
							</span>
							<span v-if="v.is_combined_visit"
								class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-50 text-violet-700">
								Combined · {{ v.tasks.length }} tasks
							</span>
						</div>
					</div>

					<p class="text-[11px] font-semibold text-slate-600">📅 {{ formatDate(v.mntc_date) }}</p>
					<p v-if="v.remarks" class="text-[11px] text-slate-600 line-clamp-2">📝 {{ v.remarks }}</p>

					<!-- Hidden until expanded -->
					<div v-if="isOpen(v.name)" class="space-y-2">
						<p v-if="v.sales_invoice" class="text-[11px] font-semibold text-slate-600">🧾 Invoice: {{
							v.sales_invoice }}</p>

						<div class="rounded-xl bg-slate-50 divide-y">
							<div v-for="t in v.tasks" :key="t.task" class="px-3 py-2">
								<div class="flex items-center justify-between gap-2">
									<p class="text-xs font-semibold truncate">{{ t.item_name }}</p>
									<span class="text-[10px] font-bold"
										:class="t.status === 'Fully Completed' ? 'text-emerald-600' : 'text-amber-600'">{{
											t.status }}</span>
								</div>
								<p class="text-[11px] text-slate-500">🧩 Task: {{ t.task }}</p>
								<p v-if="t.serial_no" class="text-[11px] text-slate-600 whitespace-pre-line">🔢 Serial
									No: {{ t.serial_no }}</p>
							</div>
						</div>

						<div v-if="v.materials?.length" class="rounded-xl bg-amber-50/60 divide-y">
							<p class="px-3 pt-2 text-[10px] font-bold uppercase tracking-wide text-amber-700">Spare
								parts used</p>
							<div v-for="(m, idx) in v.materials" :key="'m' + idx" class="px-3 py-2">
								<p class="text-xs font-semibold truncate">{{ m.item_code }} × {{ m.qty }} {{ m.uom || ""
									}}</p>
								<p v-if="m.serial_no" class="text-[11px] text-slate-600 whitespace-pre-line">🔢 Serial
									No: {{ m.serial_no }}</p>
							</div>
						</div>
					</div>

					<button type="button" @click="toggle(v.name)"
						class="w-full text-[11px] font-semibold text-teal-700 pt-1 active:scale-95">
						{{ isOpen(v.name) ? "Hide details ▲" : "View more details ▼" }}
					</button>
				</div>

				<button v-if="canLoadMore" type="button" @click="loadMore" :disabled="current.loading"
					class="w-full text-xs font-semibold py-2.5 rounded-xl bg-slate-100 text-slate-600 active:scale-95">
					{{ current.loading ? "Loading..." : "Load more" }}
				</button>
			</div>
		</div>

		<ServiceBottomNav active-tab="home" />
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { useRouter } from "vue-router"
import ServiceBottomNav from "@/components/ServiceBottomNav.vue"
import { myVisitsResources } from "@/data/crm_support"

const router = useRouter()
function goBack() {
	if (window.history.state && window.history.state.back) router.back()
	else router.push("/service")
}

// ---- expand / collapse per card ----
const expanded = ref({})
const isOpen = (id) => !!expanded.value[id]
const toggle = (id) => {
	expanded.value[id] = !expanded.value[id]
}

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