<template>
	<div v-if="modes.length > 1" class="flex rounded-full bg-slate-100 p-0.5 text-[11px] font-semibold">
		<button
			v-for="m in modes"
			:key="m"
			type="button"
			@click="switchTo(m)"
			class="px-2.5 py-1 rounded-full transition"
			:class="mode === m ? 'bg-teal-600 text-white shadow-sm' : 'text-slate-500'"
		>
			{{ m === "support" ? "Support" : "Sales" }}
		</button>
	</div>
</template>

<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { mode, availableModes, setMode } from "@/data/mode"

const router = useRouter()
const modes = computed(() => availableModes())

function switchTo(m) {
	if (m === mode.value) return
	setMode(m)
	router.push(m === "support" ? "/service" : "/")
}
</script>