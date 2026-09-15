import { createApp } from "vue"
import App from "./App.vue"
import router from "./router"
import "./style.css"

import {
	Button,
	Input,
	setConfig,
	frappeRequest,
	resourcesPlugin,
	FormControl,
	ErrorMessage,
	Dialog,
	Popover,
	FeatherIcon,
} from "frappe-ui"

import { session } from "@/data/session"
import { employeeResource } from "@/data/employee"

const app = createApp(App)

setConfig("resourceFetcher", frappeRequest)
app.use(resourcesPlugin)

app.component("Button", Button)
app.component("Input", Input)
app.component("FormControl", FormControl)
app.component("ErrorMessage", ErrorMessage)
app.component("Dialog", Dialog)
app.component("Popover", Popover)
app.component("FeatherIcon", FeatherIcon)

app.use(router)

app.provide("$session", session)
app.provide("$employee", employeeResource)

const registerServiceWorker = () => {
	if ("serviceWorker" in navigator) {
		navigator.serviceWorker
			.register("/assets/tq_erphr/frontend/sw.js", {
				type: "classic",
			})
			.then(() => {
				console.log("MobiBiz Lite Service Worker registered")
			})
			.catch((err) => {
				console.error("Failed to register service worker", err)
			})
	}
}

router.isReady().then(async () => {
	if (import.meta.env.DEV) {
		try {
			const bootInfo = await frappeRequest({
				url: "/api/method/tq_erphr.pwa_api.get_context_for_dev",
			})
			if (!window.frappe) window.frappe = {}
			window.frappe.boot = bootInfo
		} catch (err) {
			console.warn("Dev boot context fetch failed:", err)
		}
	}
	registerServiceWorker()
	app.mount("#app")
})
