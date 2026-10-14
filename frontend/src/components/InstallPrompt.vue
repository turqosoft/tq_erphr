<template>
	<!-- Install PWA Dialog (Auto popup on beforeinstallprompt & Manual trigger) -->
	<Dialog v-model="pwaState.showInstallDialog">
		<template #body-title>
			<div class="flex items-center gap-2.5">
				<div class="w-9 h-9 rounded-2xl bg-teal-50 border border-teal-200/80 flex items-center justify-center text-teal-600 flex-shrink-0">
					<FeatherIcon name="download" class="w-5 h-5" />
				</div>
				<h2 class="text-base font-bold text-slate-900">{{ __("Install Mobi Lite") }}</h2>
			</div>
		</template>
		<template #body-content>
			<p class="text-xs text-slate-600 mt-2 leading-relaxed">
				{{ __("Install Mobi Lite on your device for fast access, seamless Purchase Order workflow approvals, and an app-like experience!") }}
			</p>
		</template>
		<template #actions>
			<div class="flex items-center gap-2 w-full pt-1">
				<Button
					variant="subtle"
					@click="pwaState.showInstallDialog = false"
					class="w-1/3 py-2.5 rounded-xl font-semibold text-xs text-slate-600 bg-slate-100 hover:bg-slate-200 cursor-pointer"
				>
					{{ __("Later") }}
				</Button>
				<Button
					variant="solid"
					@click="handleInstallClick"
					class="w-2/3 py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs rounded-xl shadow-md shadow-teal-500/20 cursor-pointer"
				>
					<template #prefix>
						<FeatherIcon name="download" class="w-4 h-4 mr-1.5" />
					</template>
					{{ __("Install Now") }}
				</Button>
			</div>
		</template>
	</Dialog>

	<!-- iOS installation info message -->
	<Dialog v-model="pwaState.showIosGuide">
		<template #body-title>
			<div class="flex items-center gap-2.5">
				<div class="w-9 h-9 rounded-2xl bg-teal-50 border border-teal-200/80 flex items-center justify-center text-teal-600 flex-shrink-0">
					<FeatherIcon name="smartphone" class="w-5 h-5" />
				</div>
				<h2 class="text-base font-bold text-slate-900">{{ __("Install on iPhone / iPad") }}</h2>
			</div>
		</template>
		<template #body-content>
			<div class="space-y-3 mt-2 text-xs text-slate-700">
				<p>{{ __("To install Mobi Lite on your iPhone or iPad home screen:") }}</p>
				<div class="p-3 bg-teal-50 rounded-2xl border border-teal-200 flex items-center gap-2.5">
					<FeatherIcon name="share" class="w-5 h-5 text-teal-600 flex-shrink-0" />
					<p class="leading-snug">
						Tap the <strong>Share</strong> button in Safari, then scroll down and tap <strong>'Add to Home Screen'</strong>.
					</p>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="solid" @click="pwaState.showIosGuide = false" class="w-full py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs rounded-xl cursor-pointer">
				{{ __("Got It") }}
			</Button>
		</template>
	</Dialog>

	<!-- Manual Instructions Dialog (When browser install icon is in address bar or menu) -->
	<Dialog v-model="pwaState.showManualGuide">
		<template #body-title>
			<div class="flex items-center gap-2.5">
				<div class="w-9 h-9 rounded-2xl bg-teal-50 border border-teal-200/80 flex items-center justify-center text-teal-600 flex-shrink-0">
					<FeatherIcon name="smartphone" class="w-5 h-5" />
				</div>
				<h2 class="text-base font-bold text-slate-900">{{ __("How to Install Mobi Lite") }}</h2>
			</div>
		</template>
		<template #body-content>
			<div class="space-y-3 mt-2 text-xs text-slate-600">
				<div class="p-3 bg-teal-50/70 rounded-2xl border border-teal-100/90 flex items-start gap-3">
					<span class="w-5 h-5 rounded-full bg-teal-600 text-white font-bold text-[10px] flex items-center justify-center flex-shrink-0 mt-0.5">1</span>
					<div>
						<p class="font-bold text-slate-900 text-xs">{{ __("Chrome / Edge (Desktop or Android):") }}</p>
						<p class="mt-0.5 text-slate-600 leading-snug">{{ __("Click the Install icon (⊕) in the browser address bar, or tap the 3-dot menu (⋮) and choose 'Install Mobi Lite' or 'Add to Home screen'.") }}</p>
					</div>
				</div>

				<div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-start gap-3">
					<span class="w-5 h-5 rounded-full bg-slate-700 text-white font-bold text-[10px] flex items-center justify-center flex-shrink-0 mt-0.5">2</span>
					<div>
						<p class="font-bold text-slate-900 text-xs">{{ __("Safari (iOS / macOS):") }}</p>
						<p class="mt-0.5 text-slate-600 leading-snug">{{ __("Tap the Share button, scroll down, and tap 'Add to Home Screen'.") }}</p>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="solid" @click="pwaState.showManualGuide = false" class="w-full py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs rounded-xl cursor-pointer">
				{{ __("Got It") }}
			</Button>
		</template>
	</Dialog>
</template>

<script setup>
import { onMounted } from "vue"
import { Dialog, Popover, FeatherIcon, Button } from "frappe-ui"
import { pwaState, initPwa, promptPwaInstall, isIos, isInStandaloneMode } from "@/data/pwa"

const __ = (text) => text

onMounted(() => {
	initPwa()

	// Automatically show iOS guide if on iOS and not in standalone mode
	if (isIos() && !isInStandaloneMode()) {
		pwaState.showIosGuide = true
	}
})

async function handleInstallClick() {
	await promptPwaInstall()
}
</script>
