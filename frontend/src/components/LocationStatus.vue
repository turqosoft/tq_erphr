<template>
	<div>
		<div v-if="locating" class="fixed inset-0 z-[60] bg-slate-900/50 flex items-center justify-center p-6">
			<div class="bg-white rounded-3xl p-6 text-center max-w-xs w-full space-y-1">
				<h3 class="text-sm font-bold">Fetching Location...</h3>
				<p class="text-[11px] text-slate-500">Please hold on while we get your current location...</p>
			</div>
		</div>
		<div
			class="rounded-xl p-2.5 text-xs flex items-center justify-between"
			:class="coords ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'"
		>
			<span>{{ coords ? "📍 Location Captured" : "📍 Location not captured yet" }}</span>
			<a v-if="coords" :href="mapLink" target="_blank" rel="noopener" class="font-semibold underline">Google Maps ↗</a>
			<button v-else type="button" @click="$emit('retry')" class="font-semibold underline">Retry</button>
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({ coords: Object, locating: Boolean })
defineEmits(["retry"])

const mapLink = computed(() =>
	props.coords ? `https://www.google.com/maps/search/?api=1&query=${props.coords.latitude},${props.coords.longitude}` : "#"
)
</script>