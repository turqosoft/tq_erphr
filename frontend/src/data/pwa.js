import { ref, reactive } from "vue"

export const pwaState = reactive({
	deferredPrompt: null,
	isInstallable: false,
	isInstalled: false,
	showInstallDialog: false,
	showIosGuide: false,
	showManualGuide: false,
})

export const isIos = () => {
	if (typeof window === "undefined") return false
	const userAgent = window.navigator.userAgent.toLowerCase()
	return /iphone|ipad|ipod/.test(userAgent)
}

export const isInStandaloneMode = () => {
	if (typeof window === "undefined") return false
	return (
		("standalone" in window.navigator && window.navigator.standalone) ||
		window.matchMedia("(display-mode: standalone)").matches
	)
}

export function initPwa() {
	if (typeof window === "undefined") return

	pwaState.isInstalled = isInStandaloneMode()

	window.addEventListener("beforeinstallprompt", (e) => {
		e.preventDefault()
		pwaState.deferredPrompt = e
		pwaState.isInstallable = true
		console.log("[PWA] beforeinstallprompt event captured")
	})

	window.addEventListener("appinstalled", () => {
		pwaState.isInstalled = true
		pwaState.isInstallable = false
		pwaState.deferredPrompt = null
		pwaState.showInstallDialog = false
		pwaState.showIosGuide = false
		pwaState.showManualGuide = false
		console.log("[PWA] App installed successfully")
	})
}

export async function promptPwaInstall() {
	if (pwaState.deferredPrompt) {
		try {
			pwaState.deferredPrompt.prompt()
			const choice = await pwaState.deferredPrompt.userChoice
			if (choice.outcome === "accepted") {
				pwaState.isInstallable = false
				pwaState.deferredPrompt = null
			}
		} catch (err) {
			console.error("[PWA] Install prompt error:", err)
		}
	} else if (isIos() && !isInStandaloneMode()) {
		pwaState.showIosGuide = true
	} else {
		pwaState.showManualGuide = true
	}
}
