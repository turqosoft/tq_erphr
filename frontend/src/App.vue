<template>
	<div class="min-h-screen flex flex-col bg-slate-100 text-slate-900 font-sans">
		<router-view v-slot="{ Component }">
			<transition name="fade" mode="out-in">
				<component :is="Component" />
			</transition>
		</router-view>

		<!-- Global Toast Notifications Overlay -->
		<ToastNotification />

		<!-- Global PWA Install Prompt Component -->
		<InstallPrompt />
	</div>
</template>

<script setup>
import InstallPrompt from "@/components/InstallPrompt.vue"
import ToastNotification from "@/components/ToastNotification.vue"
</script>
