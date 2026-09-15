<template>
	<!-- Install PWA dialog -->
	<Dialog v-model="showDialog">
		<template #body-title>
			<h2 class="text-lg font-bold text-slate-900">{{ __("Install MobiBiz Lite") }}</h2>
		</template>
		<template #body-content>
			<p class="text-sm text-slate-600">
				{{ __("Get the app on your device for easy access & a better experience!") }}
			</p>
		</template>
		<template #actions>
			<Button variant="solid" @click="() => install()" class="py-3.5 w-full bg-brand-600 hover:bg-brand-500 text-white font-bold rounded-xl shadow-md shadow-brand-500/20">
				<template #prefix>
					<FeatherIcon name="download" class="w-4 mr-1.5" />
				</template>
				{{ __("Install") }}
			</Button>
		</template>
	</Dialog>

	<!-- iOS installation info message -->
	<Popover :show="iosInstallMessage" placement="bottom">
		<template #body>
			<div
				class="mt-[calc(100vh-15rem)] flex flex-col gap-3 mx-2 rounded-2xl py-5 px-4 bg-brand-50 border border-brand-200 shadow-2xl text-slate-900"
			>
				<div
					class="flex flex-row text-center items-center justify-between mb-1 px-1"
				>
					<span class="text-base text-slate-900 font-bold">
						{{ __("Install MobiBiz Lite") }}
					</span>
					<span class="inline-flex items-baseline">
						<FeatherIcon
							name="x"
							class="ml-auto h-4 w-4 text-slate-600 hover:text-slate-900 cursor-pointer"
							@click="iosInstallMessage = false"
						/>
					</span>
				</div>
				<div class="text-xs text-slate-700 px-1">
					<span class="flex flex-col gap-2">
						<span>
							{{ __("Get the app on your iPhone for easy access & a better experience") }}
						</span>
						<span class="inline-flex items-center whitespace-nowrap">
							<span>Tap&nbsp;</span>
							<FeatherIcon name="share" class="h-4 w-4 text-brand-600 inline" />
							<span>&nbsp;and then "Add to Home Screen"</span>
						</span>
					</span>
				</div>
			</div>
		</template>
	</Popover>
</template>

<script setup>
import { ref } from "vue"
import { Dialog, Popover, FeatherIcon, Button } from "frappe-ui"

const __ = (text) => text

// Initialize deferredPrompt for use later to show browser install prompt.
const deferredPrompt = ref(null)
const showDialog = ref(false)
const iosInstallMessage = ref(false)

const isIos = () => {
	// Detects if device is on iOS
	const userAgent = window.navigator.userAgent.toLowerCase()
	return /iphone|ipad|ipod/.test(userAgent)
}

// Detects if device is in standalone mode
const isInStandaloneMode = () =>
	("standalone" in window.navigator && window.navigator.standalone) ||
	window.matchMedia("(display-mode: standalone)").matches

// Checks if should display install popup notification on iOS:
if (isIos() && !isInStandaloneMode()) {
	iosInstallMessage.value = true
}

window.addEventListener("beforeinstallprompt", (e) => {
	// Prevent the mini-infobar from appearing on mobile
	e.preventDefault()
	// Stash the event so it can be triggered later.
	deferredPrompt.value = e
	if (isIos() && !isInStandaloneMode()) {
		iosInstallMessage.value = true
	} else {
		showDialog.value = true
	}
	// Optionally, send analytics event that PWA install promo was shown.
	console.log(`'beforeinstallprompt' event was fired.`)
})

window.addEventListener("appinstalled", () => {
	showDialog.value = false
	deferredPrompt.value = null
})

async function install() {
	if (deferredPrompt.value) {
		deferredPrompt.value.prompt()
	}
	showDialog.value = false
}
</script>
