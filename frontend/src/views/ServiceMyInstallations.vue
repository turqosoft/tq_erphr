<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar page-title="My Installations" :is-refreshing="myInstallationsResource.loading" @refresh="load">
				<template #actions><ModeSwitcher /></template>
				<template #profile><ServiceProfileMenu /></template>
			</TopNavBar>

			<div class="p-4 space-y-3">
				<div class="space-y-2">
					<input
						v-model="search"
						type="search"
						placeholder="Search customer, installation, task, item, serial..."
						class="w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white"
					/>
					<div class="flex items-center gap-2">
						<input v-model="fromDate" type="date" :max="toDate || undefined" class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white" />
						<span class="text-[11px] text-slate-400">to</span>
						<input v-model="toDate" type="date" :min="fromDate || undefined" class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white" />
						<button v-if="hasFilters" type="button" @click="clearFilters" class="text-[11px] font-semibold text-teal-700 px-1">Clear</button>
					</div>
					<p class="text-[10px] text-slate-400">Date range filters by installation date.</p>
				</div>

				<p v-if="!installations.length && !myInstallationsResource.loading" class="text-xs text-slate-500 text-center py-10">
					{{ hasFilters ? "No installations match your search." : "No installations yet." }}
				</p>

				<div v-for="n in installations" :key="n.name" class="rounded-2xl bg-white border border-slate-100 p-3.5 space-y-2 shadow-sm">
					<div class="flex items-start justify-between gap-2">
						<div class="min-w-0">
							<p class="text-sm font-bold truncate">{{ n.customer_name }}</p>
							<p class="text-[11px] text-slate-500 truncate">{{ n.name }}</p>
						</div>
						<span
							class="text-[10px] font-bold px-2 py-0.5 rounded-full flex-shrink-0"
							:class="n.completion_status === 'Fully Completed' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'"
						>
							{{ n.completion_status === "Fully Completed" ? "Installed" : "Partial" }}
						</span>
					</div>

					<p class="text-[11px] font-semibold text-slate-600">📅 {{ formatDate(n.inst_date) }}</p>
					<p v-if="n.installation_task" class="text-[11px] font-semibold text-slate-600">🧩 Task: {{ n.installation_task }}</p>

					<div class="rounded-xl bg-slate-50 divide-y">
						<p class="px-3 pt-2 text-[10px] font-bold uppercase tracking-wide text-slate-400">
							Installed (Qty {{ n.installed_qty }})
						</p>
						<div v-for="(i, idx) in n.items" :key="'i' + idx" class="px-3 py-2">
							<p class="text-xs font-semibold truncate">{{ i.description || i.item_code }} × {{ i.qty }}</p>
							<p v-if="i.serial_no" class="text-[11px] text-slate-600 whitespace-pre-line">🔢 Serial No: {{ i.serial_no }}</p>
						</div>
					</div>

					<div v-if="n.materials?.length" class="rounded-xl bg-amber-50/60 divide-y">
						<p class="px-3 pt-2 text-[10px] font-bold uppercase tracking-wide text-amber-700">Spare parts used</p>
						<div v-for="(m, idx) in n.materials" :key="'m' + idx" class="px-3 py-2">
							<p class="text-xs font-semibold truncate">{{ m.item_code }} × {{ m.qty }} {{ m.uom || "" }}</p>
							<p v-if="m.serial_no" class="text-[11px] text-slate-600 whitespace-pre-line">🔢 Serial No: {{ m.serial_no }}</p>
						</div>
					</div>
				</div>

				<button
					v-if="canLoadMore"
					type="button"
					@click="loadMore"
					:disabled="myInstallationsResource.loading"
					class="w-full text-xs font-semibold py-2.5 rounded-xl bg-slate-100 text-slate-600 active:scale-95"
				>
					{{ myInstallationsResource.loading ? "Loading..." : "Load more" }}
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
import { myInstallationsResource } from "@/data/crm_support"

const installations = computed(() => myInstallationsResource.data?.installations || [])
const total = computed(() => myInstallationsResource.data?.total || 0)

// ---- search, date range and paging (10 at a time) ----
const search = ref("")
const fromDate = ref("")
const toDate = ref("")
const PAGE = 10
const limit = ref(PAGE)
const canLoadMore = computed(() => installations.value.length < total.value)
const hasFilters = computed(() => !!(search.value || fromDate.value || toDate.value))

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
function formatDate(s) {
	if (!s) return ""
	const [y, m, d] = String(s).split("-").map(Number)
	if (!y || !m || !d) return s
	return `${String(d).padStart(2, "0")} ${MONTHS[m - 1]} ${y}`
}

function load() {
	myInstallationsResource.fetch({
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