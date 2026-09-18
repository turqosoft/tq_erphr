<template>
	<div
		class="fixed top-4 left-0 right-0 z-[99999] flex flex-col items-center pointer-events-none px-4 space-y-2.5"
		aria-live="polite"
	>
		<transition-group
			enter-active-class="transform ease-out duration-300 transition"
			enter-from-class="-translate-y-4 opacity-0 scale-95"
			enter-to-class="translate-y-0 opacity-100 scale-100"
			leave-active-class="transition ease-in duration-200"
			leave-from-class="opacity-100 scale-100"
			leave-to-class="opacity-0 scale-90 -translate-y-2"
		>
			<div
				v-for="t in toastState.toasts"
				:key="t.id"
				:class="[
					'pointer-events-auto w-full max-w-sm rounded-2xl p-3.5 border shadow-2xl backdrop-blur-md flex items-start gap-3 relative overflow-hidden transition-all select-none',
					cardClass(t.type),
				]"
			>
				<!-- Icon Container -->
				<div :class="['w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-xs', iconBgClass(t.type)]">
					<!-- Warning Icon -->
					<svg v-if="t.type === 'warning'" class="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
					</svg>
					<!-- Error Icon -->
					<svg v-else-if="t.type === 'error'" class="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<!-- Success Icon -->
					<svg v-else-if="t.type === 'success'" class="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
					</svg>
					<!-- Info Icon -->
					<svg v-else class="w-5 h-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
				</div>

				<!-- Content -->
				<div class="flex-1 min-w-0 pr-1 pt-0.5">
					<h4 :class="['text-xs font-bold leading-tight', titleClass(t.type)]">
						{{ t.title }}
					</h4>
					<p class="text-xs text-slate-600 font-medium leading-snug mt-0.5 break-words">
						{{ t.message }}
					</p>
				</div>

				<!-- Dismiss Button -->
				<button
					type="button"
					@click="removeToast(t.id)"
					class="p-1 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-black/5 active:scale-95 transition-all flex-shrink-0"
					aria-label="Close notification"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>
		</transition-group>
	</div>
</template>

<script setup>
import { toastState, removeToast } from "@/utils/toast"

function cardClass(type) {
	switch (type) {
		case "warning":
			return "bg-amber-50/95 border-amber-200/90 shadow-amber-500/10 text-amber-950"
		case "error":
			return "bg-rose-50/95 border-rose-200/90 shadow-rose-500/10 text-rose-950"
		case "success":
			return "bg-emerald-50/95 border-emerald-200/90 shadow-emerald-500/10 text-emerald-950"
		default:
			return "bg-teal-50/95 border-teal-200/90 shadow-teal-500/10 text-teal-950"
	}
}

function iconBgClass(type) {
	switch (type) {
		case "warning":
			return "bg-amber-100/90 border border-amber-200/80"
		case "error":
			return "bg-rose-100/90 border border-rose-200/80"
		case "success":
			return "bg-emerald-100/90 border border-emerald-200/80"
		default:
			return "bg-teal-100/90 border border-teal-200/80"
	}
}

function titleClass(type) {
	switch (type) {
		case "warning":
			return "text-amber-900"
		case "error":
			return "text-rose-900"
		case "success":
			return "text-emerald-900"
		default:
			return "text-teal-900"
	}
}
</script>
