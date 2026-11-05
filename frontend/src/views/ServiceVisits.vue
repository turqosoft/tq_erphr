<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar page-title="Service Tasks" :is-refreshing="current.loading" @refresh="load">
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

				<div class="flex gap-2">
					<button
						v-for="k in KINDS"
						:key="k.key"
						type="button"
						@click="setKind(k.key)"
						class="text-[11px] font-semibold px-3 py-1.5 rounded-full border transition"
						:class="kind === k.key ? 'bg-teal-600 text-white border-teal-600' : 'bg-white text-slate-600 border-slate-200'"
					>
						{{ k.label }}
					</button>
				</div>

				<div v-if="canSelect" class="flex justify-end">
					<button
						type="button"
						@click="toggleSelectMode"
						class="text-[11px] font-semibold px-3 py-1.5 rounded-xl"
						:class="selectMode ? 'bg-teal-600 text-white' : 'bg-slate-100 text-slate-600'"
					>
						{{ selectMode ? "Cancel" : "Select tasks" }}
					</button>
				</div>

				<p v-if="!tasks.length && !current.loading" class="text-xs text-slate-500 text-center py-10">Nothing here.</p>

				<div v-for="t in visibleTasks" :key="t.name" class="relative">
					<ServiceTaskCard :task="t" :class="selectMode ? 'pointer-events-none' : ''" @start="openTask" />
					<div
						v-if="selectMode"
						@click="togglePick(t)"
						class="absolute inset-0 rounded-2xl"
						:class="[
							isPicked(t) ? 'ring-2 ring-teal-600 bg-teal-50/30' : '',
							isBlocked(t) ? 'bg-white/70 cursor-not-allowed' : 'cursor-pointer',
						]"
					>
						<span
							v-if="!isBlocked(t)"
							class="absolute top-2 right-2 w-5 h-5 rounded-md border-2 flex items-center justify-center text-[11px] text-white"
							:class="isPicked(t) ? 'bg-teal-600 border-teal-600' : 'bg-white border-slate-300'"
						>{{ isPicked(t) ? "✓" : "" }}</span>
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

		<ServiceVisitModal v-model="showVisit" :task="selected" :tasks="combinedTasks" @done="onVisitDone" />
		<InstallationNoteModal v-model="showInstall" :task="selected" @done="load" />

		<div v-if="selectMode" class="fixed bottom-20 inset-x-0 z-40 px-4">
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
import { ref, computed, onMounted } from "vue"
import TopNavBar from "@/components/TopNavBar.vue"
import ServiceBottomNav from "@/components/ServiceBottomNav.vue"
import ModeSwitcher from "@/components/ModeSwitcher.vue"
import ServiceTaskCard from "@/components/ServiceTaskCard.vue"
import ServiceVisitModal from "@/components/ServiceVisitModal.vue"
import InstallationNoteModal from "@/components/InstallationNoteModal.vue"
import { serviceVisitsResources } from "@/data/crm_support"
import ServiceProfileMenu from "@/components/ServiceProfileMenu.vue"

const FILTERS = [
	{ key: "upcoming", label: "Upcoming", source: "pending", test: (t) => !t.is_overdue },
	{ key: "overdue", label: "Pending", source: "pending", test: (t) => t.is_overdue },
	{ key: "completed", label: "Completed", source: "completed", test: () => true },
	{ key: "spares", label: "Requires Spares", source: "spares", test: () => true },
]
const KINDS = [
	{ key: "all", label: "All" },
	{ key: "installation", label: "Installation" },
	{ key: "maintenance", label: "Maintenance" },
]
const kind = ref("all")

const filter = ref("upcoming")
const activeFilter = computed(() => FILTERS.find((f) => f.key === filter.value))
const current = computed(() => serviceVisitsResources[activeFilter.value.source])
const statusTasks = computed(() => (current.value.data?.tasks || []).filter(activeFilter.value.test))
const tasks = computed(() =>
	kind.value === "all" ? statusTasks.value : statusTasks.value.filter((t) => t.kind === kind.value)
)
const PAGE = 20
const completedLimit = ref(PAGE)
const shown = ref(PAGE)
const visibleTasks = computed(() =>
	filter.value === "completed" ? tasks.value : tasks.value.slice(0, shown.value)
)
const canLoadMore = computed(() =>
	filter.value === "completed"
		? statusTasks.value.length >= completedLimit.value
		: tasks.value.length > shown.value
)
const showVisit = ref(false)
const showInstall = ref(false)
const selected = ref(null)

// ---- combined visit selection ----
const selectMode = ref(false)
const picked = ref([])
const combinedTasks = ref([])

const canSelect = computed(
	() => filter.value !== "completed" && tasks.value.some((t) => t.kind === "maintenance")
)
const pickedTasks = computed(() => tasks.value.filter((t) => picked.value.includes(t.name)))

function isPicked(t) {
	return picked.value.includes(t.name)
}
function isBlocked(t) {
	if (t.kind !== "maintenance" || t.completion_status === "Fully Completed") return true
	const f = pickedTasks.value[0]
	return !!f && !isPicked(t) && (t.customer !== f.customer || (t.address || "") !== (f.address || ""))
}
function togglePick(t) {
	if (isBlocked(t)) return
	picked.value = isPicked(t) ? picked.value.filter((n) => n !== t.name) : [...picked.value, t.name]
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
	load()
}

// ---- loading ----
function load() {
	const params = { status: activeFilter.value.source }
	if (filter.value === "completed") params.limit = completedLimit.value
	current.value.fetch(params)
}
function loadMore() {
	if (filter.value === "completed") {
		completedLimit.value += PAGE
		load()
	} else {
		shown.value += PAGE
	}
}
function setFilter(k) {
	filter.value = k
	completedLimit.value = PAGE
	shown.value = PAGE
	selectMode.value = false
	picked.value = []
	load()
}
// NEW: kind chip handler
function setKind(k) {
	kind.value = k
	shown.value = PAGE
	selectMode.value = false
	picked.value = []
}
function openTask(t) {
	selected.value = t
	combinedTasks.value = []
	if (t.kind === "installation") showInstall.value = true
	else showVisit.value = true
}

onMounted(load)
</script>