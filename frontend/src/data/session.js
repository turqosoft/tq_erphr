import { computed, reactive } from "vue"
import { createResource, call } from "frappe-ui"
import { employeeResource } from "./employee"
import router from "@/router"

export function sessionUser() {
	let cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest" || !_sessionUser) {
		return null
	}
	return _sessionUser
}

function handleLogin(response) {
	if (response.message === "Logged In") {
		session.user = sessionUser()
		employeeResource.reload()
		router.replace({ path: "/" })
	}
}

export const session = reactive({
	login: async (email, password) => {
		const response = await call("login", { usr: email, pwd: password })
		handleLogin(response)
		return response
	},
	logout: createResource({
		url: "logout",
		onSuccess() {
			session.user = null
			employeeResource.reset()
			router.replace({ name: "Login" })
			window.location.reload()
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})
