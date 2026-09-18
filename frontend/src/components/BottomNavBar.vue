<template>
	<nav class="fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur-xl border-t border-slate-200/80 shadow-[0_-4px_24px_rgba(0,0,0,0.06)] py-1.5 px-3">
		<div class="max-w-md mx-auto flex items-center justify-around">
			<!-- Home / Attendance Tab -->
			<button
				type="button"
				@click="navigate('home')"
				class="flex-1 flex flex-col items-center justify-center py-1 px-2 rounded-2xl transition-all duration-150 active:scale-95"
				:class="activeTab === 'home' ? 'text-teal-700 font-bold' : 'text-slate-400 hover:text-slate-600 font-medium'"
			>
				<div class="relative">
					<div
						v-if="activeTab === 'home'"
						class="absolute -inset-1.5 bg-teal-50 rounded-xl -z-10"
					></div>
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>
				<span class="text-[11px] mt-1 leading-none">Attendance</span>
			</button>

			<!-- EEM Site & Trip Tab (Visible only for Sales Persons) -->
			<button
				v-if="showEem"
				type="button"
				@click="navigate('eem')"
				class="flex-1 flex flex-col items-center justify-center py-1 px-1 sm:px-2 rounded-2xl transition-all duration-150 active:scale-95 relative"
				:class="activeTab === 'eem' ? 'text-teal-700 font-bold' : 'text-slate-400 hover:text-slate-600 font-medium'"
			>
				<div class="relative">
					<div
						v-if="activeTab === 'eem'"
						class="absolute -inset-1.5 bg-teal-50 rounded-xl -z-10"
					></div>
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
					</svg>
					<!-- Live indicator badge if trip is running -->
					<span
						v-if="isTripActive"
						class="absolute -top-1 -right-1 flex h-2.5 w-2.5"
					>
						<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
						<span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
					</span>
				</div>
				<span class="text-[11px] mt-1 leading-none">Site & Trip</span>
			</button>

			<!-- Customers Tab -->
			<button
				type="button"
				@click="navigate('customers')"
				class="flex-1 flex flex-col items-center justify-center py-1 px-1 sm:px-2 rounded-2xl transition-all duration-150 active:scale-95"
				:class="activeTab === 'customers' ? 'text-teal-700 font-bold' : 'text-slate-400 hover:text-slate-600 font-medium'"
			>
				<div class="relative">
					<div
						v-if="activeTab === 'customers'"
						class="absolute -inset-1.5 bg-teal-50 rounded-xl -z-10"
					></div>
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
				</div>
				<span class="text-[11px] mt-1 leading-none">Customers</span>
			</button>

			<!-- History Logs Tab -->
			<button
				type="button"
				@click="$emit('openHistory')"
				class="flex-1 flex flex-col items-center justify-center py-1 px-1 sm:px-2 rounded-2xl transition-all duration-150 active:scale-95"
				:class="activeTab === 'history' ? 'text-teal-700 font-bold' : 'text-slate-400 hover:text-slate-600 font-medium'"
			>
				<div class="relative">
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
					</svg>
				</div>
				<span class="text-[11px] mt-1 leading-none">Logs</span>
			</button>

			<!-- Profile Tab -->
			<button
				type="button"
				@click="$emit('openProfile')"
				class="flex-1 flex flex-col items-center justify-center py-1 px-1 sm:px-2 rounded-2xl transition-all duration-150 active:scale-95"
				:class="activeTab === 'profile' ? 'text-teal-700 font-bold' : 'text-slate-400 hover:text-slate-600 font-medium'"
			>
				<div class="relative">
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
					</svg>
				</div>
				<span class="text-[11px] mt-1 leading-none">Profile</span>
			</button>
		</div>
	</nav>
</template>

<script setup>
import { useRouter } from "vue-router"

const props = defineProps({
	activeTab: {
		type: String,
		default: "home",
	},
	isTripActive: {
		type: Boolean,
		default: false,
	},
	showEem: {
		type: Boolean,
		default: true,
	},
})

const emit = defineEmits(["openHistory", "openProfile"])
const router = useRouter()

function navigate(tab) {
	if (tab === "home") {
		router.push("/")
	} else if (tab === "eem") {
		router.push("/eem")
	} else if (tab === "customers") {
		router.push("/customers")
	}
}
</script>
