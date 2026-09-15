/**
 * Device capture and identification utilities for TQ ERP HR PWA
 */

export function getOrCreateDeviceId() {
	const KEY = "tq_erphr_device_uid"
	let uid = localStorage.getItem(KEY)
	if (!uid) {
		const randomPart = Math.random().toString(36).substring(2, 8).toUpperCase()
		const timePart = Date.now().toString(36).slice(-4).toUpperCase()
		uid = `DEV-${randomPart}-${timePart}`
		localStorage.setItem(KEY, uid)
	}
	return uid
}

export function detectDeviceDetails() {
	const ua = navigator.userAgent || ""
	let os = "Unknown OS"
	let browser = "Unknown Browser"
	let isPWA = false

	// Detect PWA Standalone Mode
	if (
		window.matchMedia("(display-mode: standalone)").matches ||
		window.navigator.standalone === true ||
		document.referrer.includes("android-app://")
	) {
		isPWA = true
	}

	// Detect Operating System
	if (/android/i.test(ua)) {
		const match = ua.match(/Android\s([0-9\.]*)/i)
		os = match ? `Android ${match[1]}` : "Android"
	} else if (/iPhone|iPad|iPod/i.test(ua)) {
		const match = ua.match(/OS\s([0-9_]*)/i)
		os = match ? `iOS ${match[1].replace(/_/g, ".")}` : "iOS"
	} else if (/Windows NT/i.test(ua)) {
		if (/Windows NT 10.0/i.test(ua)) os = "Windows 10/11"
		else os = "Windows"
	} else if (/Mac OS X/i.test(ua)) {
		os = "macOS"
	} else if (/Linux/i.test(ua)) {
		os = "Linux"
	}

	// Detect Browser
	if (/SamsungBrowser/i.test(ua)) {
		browser = "Samsung Internet"
	} else if (/Edg/i.test(ua)) {
		browser = "Edge"
	} else if (/Chrome/i.test(ua) && !/Chromium|Edg/i.test(ua)) {
		browser = "Chrome"
	} else if (/Safari/i.test(ua) && !/Chrome|CriOS/i.test(ua)) {
		browser = "Safari"
	} else if (/Firefox|FxiOS/i.test(ua)) {
		browser = "Firefox"
	}

	const deviceUid = getOrCreateDeviceId()
	const appMode = isPWA ? "PWA" : "Web"
	
	// Formatted concise device_id suitable for DocType field (e.g. "Android • Chrome (PWA) [DEV-A1B2]")
	const shortDeviceId = `${os} • ${browser} (${appMode}) [${deviceUid.slice(0, 10)}]`

	// Extended remark details
	const remarks = `Device: ${os} | Browser: ${browser} | Mode: ${appMode} | Screen: ${window.screen.width}x${window.screen.height} | UID: ${deviceUid}`

	return {
		deviceUid,
		os,
		browser,
		isPWA,
		appMode,
		shortDeviceId,
		remarks,
	}
}
