<template>
	<!-- Install PWA Dialog (Auto / Manual) -->
	<Dialog v-model="pwaState.showInstallDialog">
		<template #body-title>
			<div class="flex items-center gap-2">
				<div class="w-8 h-8 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600">
					<FeatherIcon name="download" class="w-4 h-4" />
				</div>
				<h2 class="text-base font-bold text-slate-900">{{ __("Install MobiBiz Lite") }}</h2>
			</div>
		</template>
		<template #body-content>
			<p class="text-sm text-slate-600 mt-2 leading-relaxed">
				{{ __("Install MobiBiz Lite on your device for instant offline-ready access, fast attendance check-in, and full-screen experience!") }}
			</p>
		</template>
		<template #actions>
			<div class="flex gap-2 w-full">
				<Button variant="subtle" @click="pwaState.showInstallDialog = false" class="w-1/3 py-2.5 rounded-xl font-medium text-slate-600">
					{{ __("Later") }}
				</Button>
				<Button variant="solid" @click="handleInstallClick" class="w-2/3 py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-bold rounded-xl shadow-md shadow-teal-500/20">
					<template #prefix>
						<FeatherIcon name="download" class="w-4 h-4 mr-1" />
					</template>
					{{ __("Install Now") }}
				</Button>
			</div>
		</template>
	</Dialog>

	<!-- Manual Instructions Dialog (When browser install icon is in address bar or menu) -->
	<Dialog v-model="pwaState.showManualGuide">
		<template #body-title>
			<div class="flex items-center gap-2">
				<div class="w-8 h-8 rounded-xl bg-teal-50 flex items-center justify-center text-teal-600">
					<FeatherIcon name="smartphone" class="w-4 h-4" />
				</div>
				<h2 class="text-base font-bold text-slate-900">{{ __("How to Install MobiBiz") }}</h2>
			</div>
		</template>
		<template #body-content>
			<div class="space-y-3.5 mt-2 text-xs text-slate-600">
				<div class="p-3 bg-teal-50/60 rounded-2xl border border-teal-100/80 flex items-start gap-3">
					<span class="w-5 h-5 rounded-full bg-teal-600 text-white font-bold text-[10px] flex items-center justify-center flex-shrink-0 mt-0.5">1</span>
					<div>
						<p class="font-bold text-slate-800 text-xs">{{ __("On Chrome / Edge (Desktop or Android):") }}</p>
						<p class="mt-0.5 text-slate-600">{{ __("Click the Install icon in the browser address bar, or open the 3-dot menu (⋮) and choose 'Install MobiBiz Lite' or 'Add to Home screen'.") }}</p>
					</div>
				</div>

				<div class="p-3 bg-slate-50 rounded-2xl border border-slate-100 flex items-start gap-3">
					<span class="w-5 h-5 rounded-full bg-slate-700 text-white font-bold text-[10px] flex items-center justify-center flex-shrink-0 mt-0.5">2</span>
					<div>
						<p class="font-bold text-slate-800 text-xs">{{ __("On Safari (iPhone / iPad):") }}</p>
						<p class="mt-0.5 text-slate-600">{{ __("Tap the Share button (square with arrow up) at the bottom, scroll down, and tap 'Add to Home Screen'.") }}</p>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<Button variant="solid" @click="pwaState.showManualGuide = false" class="w-full py-2.5 bg-teal-600 hover:bg-teal-500 text-white font-bold rounded-xl">
				{{ __("Got It") }}
			</Button>
		</template>
	</Dialog>

	<!-- iOS Installation Info Banner/Popover -->
	<Popover :show="pwaState.showIosGuide" placement="bottom">
		<template #body>
			<div
				class="mt-[calc(100vh-15rem)] flex flex-col gap-3 mx-2 rounded-2xl py-5 px-4 bg-teal-50 border border-teal-200 shadow-2xl text-slate-900"
			>
				<div class="flex flex-row text-center items-center justify-between mb-1 px-1">
					<span class="text-base text-slate-900 font-bold flex items-center gap-1.5">
						<FeatherIcon name="smartphone" class="w-4 h-4 text-teal-600" />
						{{ __("Install MobiBiz Lite") }}
					</span>
					<span class="inline-flex items-baseline">
						<FeatherIcon
							name="x"
							class="ml-auto h-4 w-4 text-slate-600 hover:text-slate-900 cursor-pointer"
							@click="pwaState.showIosGuide = false"
						/>
					</span>
				</div>
				<div class="text-xs text-slate-700 px-1">
					<span class="flex flex-col gap-2">
						<span>{{ __("Get the app on your iPhone for easy access & a full-screen experience:") }}</span>
						<span class="inline-flex items-center whitespace-nowrap font-medium text-teal-800 bg-white p-2 rounded-xl border border-teal-200 shadow-xs">
							<span>Tap&nbsp;</span>
							<FeatherIcon name="share" class="h-4 w-4 text-teal-600 inline mx-0.5" />
							<span>&nbsp;and then "Add to Home Screen"</span>
						</span>
					</span>
				</div>
			</div>
		</template>
	</Popover>
</template>

<script setup>
import { onMounted } from "vue"
import { Dialog, Popover, FeatherIcon, Button } from "frappe-ui"
import { pwaState, initPwa, promptPwaInstall, isIos, isInStandaloneMode } from "@/data/pwa"

const __ = (text) => text

onMounted(() => {
	initPwa()

	// Automatically show iOS guide only once if iOS and not in standalone mode
	if (isIos() && !isInStandaloneMode()) {
		const dismissed = sessionStorage.getItem("mobibiz_ios_pwa_dismissed")
		if (!dismissed) {
			pwaState.showIosGuide = true
			sessionStorage.setItem("mobibiz_ios_pwa_dismissed", "true")
		}
	}
})

async function handleInstallClick() {
	pwaState.showInstallDialog = false
	await promptPwaInstall()
}
</script>
