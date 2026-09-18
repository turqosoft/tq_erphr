<template>
	<header class="sticky top-0 z-30 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 px-4 py-3 sm:px-5 transition-all shadow-xs">
		<div class="flex items-center justify-between">
			<!-- Left Side: Back Button OR Company Logo & Name -->
			<div class="flex items-center space-x-2.5 min-w-0 flex-1 mr-2">
				<!-- Back Button (if showBack is true) -->
				<button
					v-if="showBack"
					type="button"
					@click="handleBack"
					class="p-2 -ml-1 rounded-2xl text-slate-600 hover:text-teal-700 hover:bg-teal-50/80 active:scale-95 transition cursor-pointer flex-shrink-0"
					:title="backTitle || 'Go Back'"
				>
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
					</svg>
				</button>

				<!-- Company Logo (if not back or if explicitly requested) -->
				<div
					v-if="!showBack || showLogoWithBack"
					class="w-9 h-9 rounded-2xl bg-white p-1 flex items-center justify-center shadow-md shadow-teal-600/10 border border-slate-100 ring-2 ring-teal-50 overflow-hidden flex-shrink-0"
				>
					<img
						v-if="companyLogoUrl"
						:src="companyLogoUrl"
						:alt="companyDisplayName"
						class="w-full h-full object-contain"
					/>
					<img
						v-else
						:src="mobibizIcon"
						alt="MobiBiz"
						class="w-full h-full object-contain"
					/>
				</div>

				<!-- Company Name / Page Title & Subtitle -->
				<div class="min-w-0 flex-1">
					<div class="flex items-center space-x-1.5 flex-wrap">
						<h1 class="text-sm font-bold text-slate-900 leading-tight truncate">
							{{ pageTitle || companyDisplayName }}
						</h1>
						<span
							v-if="!showBack"
							class="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse flex-shrink-0"
							title="Live Connected"
						></span>
						<span
							v-else-if="companyDisplayName && pageTitle"
							class="hidden xs:inline-block px-1.5 py-0.2 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-teal-200/80 truncate max-w-[120px]"
							:title="companyDisplayName"
						>
							{{ companyDisplayName }}
						</span>
					</div>
					<p class="text-[10px] font-medium text-slate-500 leading-none truncate mt-0.5">
						{{ pageSubtitle || (showBack ? companyDisplayName : 'Employee Portal') }}
					</p>
				</div>
			</div>

			<!-- Right Side: Custom Actions + Refresh + Profile/Menu Slot -->
			<div class="flex items-center space-x-1.5 flex-shrink-0">
				<!-- Custom Actions Slot -->
				<slot name="actions"></slot>

				<!-- Refresh Action Button -->
				<button
					v-if="showRefresh"
					type="button"
					@click="$emit('refresh')"
					:disabled="isRefreshing"
					class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
					title="Refresh data"
				>
					<svg
						class="w-4 h-4"
						:class="{ 'animate-spin text-teal-600': isRefreshing }"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
						/>
					</svg>
				</button>

				<!-- Profile / Menu Slot -->
				<slot name="profile"></slot>
			</div>
		</div>

		<!-- Extra Bottom Header Content Slot (e.g. Search Bar or Filter Bar) -->
		<slot name="bottom"></slot>
	</header>
</template>

<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { employeeResource } from "@/data/employee"
import mobibizIcon from "@/assets/mobibiz_icon.png"

const props = defineProps({
	pageTitle: {
		type: String,
		default: "",
	},
	pageSubtitle: {
		type: String,
		default: "",
	},
	showBack: {
		type: Boolean,
		default: false,
	},
	backTitle: {
		type: String,
		default: "Back",
	},
	showLogoWithBack: {
		type: Boolean,
		default: false,
	},
	showRefresh: {
		type: Boolean,
		default: true,
	},
	isRefreshing: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["back", "refresh"])
const router = useRouter()

const employee = computed(() => employeeResource.data)

const companyDisplayName = computed(() => {
	return employee.value?.company_name || employee.value?.company || "Total Quality"
})

const companyLogoUrl = computed(() => {
	return employee.value?.company_logo || employee.value?.app_logo || null
})

function handleBack() {
	emit("back")
}
</script>
