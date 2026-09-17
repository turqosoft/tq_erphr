import { reactive } from "vue"

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

// Immediate listener executed at module load time (HRMS pattern)
if (typeof window !== "undefined") {
	pwaState.isInstalled = isInStandaloneMode()

	window.addEventListener("beforeinstallprompt", (e) => {
		// Prevent default browser mini-infobar
		e.preventDefault()
		pwaState.deferredPrompt = e
		pwaState.isInstallable = true

		if (isIos() && !isInStandaloneMode()) {
			pwaState.showIosGuide = true
		} else {
			// Automatically show install prompt dialog
			pwaState.showInstallDialog = true
		}
		console.log("'beforeinstallprompt' event was fired and auto-dialog opened.")
	})

	window.addEventListener("appinstalled", () => {
		pwaState.isInstalled = true
		pwaState.isInstallable = false
		pwaState.deferredPrompt = null
		pwaState.showInstallDialog = false
		pwaState.showIosGuide = false
		pwaState.showManualGuide = false
		console.log("MobiBiz app installed successfully.")
	})
}

export function initPwa() {
	if (typeof window === "undefined") return
	pwaState.isInstalled = isInStandaloneMode()
}

export async function promptPwaInstall() {
	if (pwaState.deferredPrompt) {
		try {
			pwaState.deferredPrompt.prompt()
			const choice = await pwaState.deferredPrompt.userChoice
			if (choice && choice.outcome === "accepted") {
				pwaState.isInstallable = false
				pwaState.deferredPrompt = null
			}
			pwaState.showInstallDialog = false
		} catch (err) {
			console.error("[PWA] Install prompt error:", err)
		}
	} else if (isIos() && !isInStandaloneMode()) {
		pwaState.showIosGuide = true
	} else {
		pwaState.showManualGuide = true
	}
}

