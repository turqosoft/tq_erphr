
<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar
				page-title="Service Tasks"
				:is-refreshing="current.loading"
				@refresh="load"
			>
				<template #actions>
					<ModeSwitcher />
				</template>

				<template #profile>
					<ServiceProfileMenu />
				</template>
			</TopNavBar>

			<div class="p-4 space-y-3">
				<!-- Status Filter -->
				<div class="flex rounded-2xl bg-slate-100 p-1 text-[11px] font-semibold">
					<button
						v-for="f in FILTERS"
						:key="f.key"
						type="button"
						@click="setFilter(f.key)"
						class="flex-1 py-2 rounded-xl transition"
						:class="
							filter === f.key
								? 'bg-white text-teal-700 shadow-sm'
								: 'text-slate-500'
						"
					>
						{{ f.label }}
					</button>
				</div>

				<!-- Task Type Filter -->
				<div class="flex gap-2">
					<button
						v-for="k in KINDS"
						:key="k.key"
						type="button"
						@click="setKind(k.key)"
						class="text-[11px] font-semibold px-3 py-1.5 rounded-full border transition"
						:class="
							kind === k.key
								? 'bg-teal-600 text-white border-teal-600'
								: 'bg-white text-slate-600 border-slate-200'
						"
					>
						{{ k.label }}
					</button>
				</div>

				<!-- Search and Date Filters -->
				<div class="space-y-2">
					<input
						v-model="search"
						type="search"
						placeholder="Search customer, task, item, serial..."
						class="w-full rounded-xl border border-slate-200 p-2.5 text-sm bg-white"
					/>

					<div class="flex items-center gap-2">
						<input
							v-model="fromDate"
							type="date"
							:max="toDate || undefined"
							class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white"
						/>

						<span class="text-[11px] text-slate-400">
							to
						</span>

						<input
							v-model="toDate"
							type="date"
							:min="fromDate || undefined"
							class="flex-1 min-w-0 rounded-xl border border-slate-200 p-2 text-xs bg-white"
						/>

						<button
							v-if="hasFilters"
							type="button"
							@click="clearFilters"
							class="text-[11px] font-semibold text-teal-700 px-1"
						>
							Clear
						</button>
					</div>

					<p class="text-[10px] text-slate-400">
						Date range filters by scheduled date.
					</p>
				</div>

				<!-- Combined Visit Selection -->
				<div v-if="canSelect" class="flex justify-end">
					<button
						type="button"
						@click="toggleSelectMode"
						class="text-[11px] font-semibold px-3 py-1.5 rounded-xl"
						:class="
							selectMode
								? 'bg-teal-600 text-white'
								: 'bg-slate-100 text-slate-600'
						"
					>
						{{ selectMode ? "Cancel" : "Select tasks" }}
					</button>
				</div>

				<!-- Empty State -->
				<p
					v-if="!tasks.length && !current.loading"
					class="text-xs text-slate-500 text-center py-10"
				>
					{{ hasFilters ? "No tasks match your filters." : "Nothing here." }}
				</p>

				<!-- Task Cards -->
				<div
					v-for="t in tasks"
					:key="t.name"
					class="relative"
				>
					<ServiceTaskCard
						:task="t"
						:class="selectMode ? 'pointer-events-none' : ''"
						@start="openTask"
					/>

					<div
						v-if="selectMode"
						@click="togglePick(t)"
						class="absolute inset-0 rounded-2xl"
						:class="[
							isPicked(t)
								? 'ring-2 ring-teal-600 bg-teal-50/30'
								: '',
							isBlocked(t)
								? 'bg-white/70 cursor-not-allowed'
								: 'cursor-pointer',
						]"
					>
						<span
							v-if="!isBlocked(t)"
							class="absolute top-2 right-2 w-5 h-5 rounded-md border-2 flex items-center justify-center text-[11px] text-white"
							:class="
								isPicked(t)
									? 'bg-teal-600 border-teal-600'
									: 'bg-white border-slate-300'
							"
						>
							{{ isPicked(t) ? "✓" : "" }}
						</span>
					</div>
				</div>

				<!-- Load More -->
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

		<!-- Service Visit Modal -->
		<ServiceVisitModal
			v-model="showVisit"
			:task="selected"
			:tasks="combinedTasks"
			@done="onVisitDone"
		/>

		<!-- Installation Modal -->
		<InstallationNoteModal
			v-model="showInstall"
			:task="selected"
			@done="reload"
		/>

		<!-- Combined Visit Action -->
		<div
			v-if="selectMode"
			class="fixed bottom-20 inset-x-0 z-40 px-4"
		>
			<div class="sm:max-w-md mx-auto">
				<button
					type="button"
					:disabled="picked.length < 2"
					@click="openCombined"
					class="w-full py-3 rounded-2xl text-sm font-bold text-white bg-teal-600 disabled:opacity-50 shadow-lg active:scale-95"
				>
					Create combined visit ({{ picked.length }})
				</button>
			</div>
		</div>

		<ServiceBottomNav active-tab="visits" />
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue"

import TopNavBar from "@/components/TopNavBar.vue"
import ServiceBottomNav from "@/components/ServiceBottomNav.vue"
import ModeSwitcher from "@/components/ModeSwitcher.vue"
import ServiceTaskCard from "@/components/ServiceTaskCard.vue"
import ServiceVisitModal from "@/components/ServiceVisitModal.vue"
import InstallationNoteModal from "@/components/InstallationNoteModal.vue"
import ServiceProfileMenu from "@/components/ServiceProfileMenu.vue"

import { serviceVisitsResources } from "@/data/crm_support"

// --------------------------------------------------
// Filters
// --------------------------------------------------

const FILTERS = [
	{ key: "upcoming", label: "Upcoming", source: "upcoming" },
	{ key: "overdue", label: "Pending", source: "overdue" },
	{ key: "completed", label: "Completed", source: "completed" },
	{ key: "spares", label: "Requires Spares", source: "spares" },
]

const KINDS = [
	{ key: "all", label: "All" },
	{ key: "installation", label: "Installation" },
	{ key: "maintenance", label: "Maintenance" },
]

const filter = ref("upcoming")
const kind = ref("all")

const activeFilter = computed(() =>
	FILTERS.find((f) => f.key === filter.value)
)

const current = computed(
	() => serviceVisitsResources[activeFilter.value.source]
)
const search = ref("")
const fromDate = ref("")
const toDate = ref("")

const PAGE = 10
const limit = ref(PAGE)

const allTasks = computed(
	() => current.value.data?.tasks || []
)

const total = computed(
	() => current.value.data?.total || 0
)
const tasks = computed(() =>
	kind.value === "all"
		? allTasks.value
		: allTasks.value.filter(
				(t) => t.kind === kind.value
			)
)
const canLoadMore = computed(
	() => allTasks.value.length < total.value
)

const hasFilters = computed(
	() =>
		!!search.value.trim() ||
		!!fromDate.value ||
		!!toDate.value
)

const showVisit = ref(false)
const showInstall = ref(false)
const selected = ref(null)

// --------------------------------------------------
// Combined Visit Selection
// --------------------------------------------------

const selectMode = ref(false)
const picked = ref([])
const combinedTasks = ref([])

const canSelect = computed(
	() =>
		filter.value !== "completed" &&
		tasks.value.some(
			(t) => t.kind === "maintenance"
		)
)

const pickedTasks = computed(() =>
	tasks.value.filter(
		(t) => picked.value.includes(t.name)
	)
)

function isPicked(t) {
	return picked.value.includes(t.name)
}

function isBlocked(t) {
	if (
		t.kind !== "maintenance" ||
		t.completion_status === "Fully Completed"
	) {
		return true
	}

	const first = pickedTasks.value[0]

	return (
		!!first &&
		!isPicked(t) &&
		(
			t.customer !== first.customer ||
			(t.address || "") !== (first.address || "")
		)
	)
}

function togglePick(t) {
	if (isBlocked(t)) return

	picked.value = isPicked(t)
		? picked.value.filter((name) => name !== t.name)
		: [...picked.value, t.name]
}

function toggleSelectMode() {
	selectMode.value = !selectMode.value
	picked.value = []
}

function openCombined() {
	if (picked.value.length < 2) return

	combinedTasks.value = pickedTasks.value
	selected.value = pickedTasks.value[0]

	showVisit.value = true
}

function onVisitDone() {
	selectMode.value = false
	picked.value = []
	combinedTasks.value = []

	reload()
}

function load() {
	const params = {
		status: activeFilter.value.source,
		limit: limit.value,
		search: search.value.trim() || undefined,
		from_date: fromDate.value || undefined,
		to_date: toDate.value || undefined,
	}

	current.value.fetch(params)
}

function reload() {
	limit.value = PAGE

	selectMode.value = false
	picked.value = []

	load()
}

function loadMore() {
	if (current.value.loading) return

	limit.value += PAGE

	load()
}

function setFilter(k) {
	filter.value = k

	reload()
}

function setKind(k) {
	kind.value = k

	selectMode.value = false
	picked.value = []
}

function clearFilters() {
	search.value = ""
	fromDate.value = ""
	toDate.value = ""

	// Reset pagination immediately
	limit.value = PAGE

	selectMode.value = false
	picked.value = []

	load()
}

function openTask(t) {
	selected.value = t
	combinedTasks.value = []

	if (t.kind === "installation") {
		showInstall.value = true
	} else {
		showVisit.value = true
	}
}

let timer = null

watch(search, () => {
	clearTimeout(timer)

	timer = setTimeout(() => {
		reload()
	}, 400)
})

watch([fromDate, toDate], () => {
	reload()
})

onMounted(load)

onBeforeUnmount(() => {
	clearTimeout(timer)
})
</script>
