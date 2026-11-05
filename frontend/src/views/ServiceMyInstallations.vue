<template>
	<div class="min-h-screen bg-[#f8fafc] pb-24">
		<div class="w-full sm:max-w-md mx-auto">
			<TopNavBar page-title="My Installations" :is-refreshing="myInstallationsResource.loading" @refresh="load">
				<template #actions><ModeSwitcher /></template>
				<template #profile><ServiceProfileMenu /></template>
			</TopNavBar>

			<div class="p-4 space-y-3">
				<p v-if="!installations.length && !myInstallationsResource.loading" class="text-xs text-slate-500 text-center py-10">
					No installations yet.
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

					<div class="rounded-xl bg-slate-50 divide-y">
						<div v-for="(i, idx) in n.items" :key="idx" class="px-3 py-2">
							<p class="text-xs font-semibold truncate">{{ i.item_name }} × {{ i.qty }}</p>
							<p v-if="i.serial_no" class="text-[11px] text-slate-600 whitespace-pre-line">🔢 Serial No: {{ i.serial_no }}</p>
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
import { ref, computed, onMounted } from "vue"
import TopNavBar from "@/components/TopNavBar.vue"
import ServiceBottomNav from "@/components/ServiceBottomNav.vue"
import ModeSwitcher from "@/components/ModeSwitcher.vue"
import ServiceProfileMenu from "@/components/ServiceProfileMenu.vue"
import { myInstallationsResource } from "@/data/crm_support"

const installations = computed(() => myInstallationsResource.data?.installations || [])

const PAGE = 20
const limit = ref(PAGE)
const canLoadMore = computed(() => installations.value.length >= limit.value)

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
function formatDate(s) {
	if (!s) return ""
	const [y, m, d] = String(s).split("-").map(Number)
	if (!y || !m || !d) return s
	return `${String(d).padStart(2, "0")} ${MONTHS[m - 1]} ${y}`
}

function load() {
	myInstallationsResource.fetch({ limit: limit.value })
}
function loadMore() {
	limit.value += PAGE
	load()
}

onMounted(load)
</script>