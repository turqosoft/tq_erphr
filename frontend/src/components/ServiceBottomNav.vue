<template>
	<nav class="fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur-xl border-t border-slate-200/80 py-1.5 px-3">
		<div class="max-w-md mx-auto flex items-center justify-around">
			<button
				v-for="t in tabs"
				:key="t.key"
				type="button"
				@click="router.push(t.to)"
				class="flex-1 flex flex-col items-center py-1 rounded-2xl active:scale-95 transition"
				:class="activeTab === t.key ? 'text-teal-700 font-bold' : 'text-slate-400 font-medium'"
			>
				<component :is="t.icon" class="w-5 h-5" />
				<span class="text-[11px] mt-1 leading-none">{{ t.label }}</span>
			</button>
		</div>
	</nav>
</template>

<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { Home, ClipboardList, Users, Package, User } from "lucide-vue-next"
import { employeeResource } from "@/data/employee"

defineProps({ activeTab: { type: String, default: "home" } })
const router = useRouter()

const tabs = computed(() =>
	[
		{ key: "home", label: "Home", icon: Home, to: "/service" },
		{ key: "visits", label: "Visits", icon: ClipboardList, to: "/service/visits" },
		employeeResource.data?.is_service_supervisor && { key: "team", label: "Team", icon: Users, to: "/service/team" },
		{ key: "stock", label: "Spares", icon: Package, to: "/stock" },
		// Profile opens the dialog on the service home page
		{ key: "profile", label: "Profile", icon: User, to: { path: "/service", query: { openProfile: 1 } } },
	].filter(Boolean)
)
</script>