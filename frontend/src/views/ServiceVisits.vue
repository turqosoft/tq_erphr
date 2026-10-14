<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar page-title="Service Visits" :is-refreshing="current.loading" @refresh="load">
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

				<p v-if="!tasks.length && !current.loading" class="text-xs text-slate-500 text-center py-10">Nothing here.</p>
				<ServiceTaskCard v-for="t in tasks" :key="t.name" :task="t" @start="openTask" />
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

		<ServiceVisitModal v-model="showVisit" :task="selected" @done="load" />
		<InstallationNoteModal v-model="showInstall" :task="selected" @done="load" />
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
const filter = ref("upcoming")
const activeFilter = computed(() => FILTERS.find((f) => f.key === filter.value))
const current = computed(() => serviceVisitsResources[activeFilter.value.source])
const tasks = computed(() => (current.value.data?.tasks || []).filter(activeFilter.value.test))
const PAGE = 20
const completedLimit = ref(PAGE)
const canLoadMore = computed(
	() => filter.value === "completed" && tasks.value.length >= completedLimit.value
)

const showVisit = ref(false)
const showInstall = ref(false)
const selected = ref(null)

function load() {
	const params = { status: activeFilter.value.source }
	if (filter.value === "completed") params.limit = completedLimit.value
	current.value.fetch(params)
}
function loadMore() {
	completedLimit.value += PAGE
	load()
}
function setFilter(k) {
	filter.value = k
	completedLimit.value = PAGE
	load()
}
function openTask(t) {
	selected.value = t
	if (t.kind === "installation") showInstall.value = true
	else showVisit.value = true
}

onMounted(load)
</script>