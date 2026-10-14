import { createRouter, createWebHistory } from "vue-router"
import { session } from "@/data/session"
import { employeeResource } from "@/data/employee"
import { availableModes, ensureMode } from "@/data/mode"

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("@/views/Home.vue"),
	},
	{
		path: "/eem",
		name: "ExecutiveExpenseManager",
		component: () => import("@/views/ExecutiveExpenseManager.vue"),
	},
	{
		path: "/eem/history",
		name: "ExecutiveExpenseHistory",
		component: () => import("@/views/ExecutiveExpenseHistory.vue"),
	},
	{
		path: "/eem-history",
		redirect: "/eem/history",
	},
	{
		path: "/eem/team",
		name: "SupervisorEEM",
		component: () => import("@/views/SupervisorEEM.vue"),
	},
	{
		path: "/eem-team",
		redirect: "/eem/team",
	},
	{
		path: "/customers",
		name: "Customers",
		component: () => import("@/views/Customers.vue"),
	},
	{
		path: "/stock",
		name: "Stock",
		component: () => import("@/views/Stock.vue"),
	},
	{
		path: "/login",
		name: "Login",
		component: () => import("@/views/Login.vue"),
	},

	{ path: "/service", name: "ServiceHome", component: () => import("@/views/ServiceHome.vue") },
	{ path: "/service/visits", name: "ServiceVisits", component: () => import("@/views/ServiceVisits.vue") },
	{ path: "/service/team", name: "ServiceTeam", component: () => import("@/views/SupervisorService.vue") },

	{
		path: "/:catchAll(.*)",
		redirect: "/",
	},
]

const router = createRouter({
	history: createWebHistory("/mobibiz"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	const isLoggedIn = session.isLoggedIn

	if (!isLoggedIn && to.name !== "Login") {
		return next({ name: "Login" })
	}

	if (isLoggedIn) {
		if (!employeeResource.data && !employeeResource.loading) {
			await employeeResource.fetch()
		}
		if (to.name === "Login") {
			return next({ name: "Home" })
		}
		// Old cached employee data may not have the new mode fields yet
		if (employeeResource.data && !employeeResource.data.available_modes) {
			await employeeResource.reload()
		}
		if (employeeResource.data) {
			const canSupport = availableModes().includes("support")
			const current = ensureMode()
			const isService = to.path.startsWith("/service")

			if (isService && !canSupport) return next({ name: "Home" })
			if (!isService && to.name !== "Stock" && current === "support") {
				return next({ path: "/service", query: to.query })
			}
			if (isService && current === "sales") return next({ name: "Home" })
		}

		if (to.name === "ServiceTeam" && employeeResource.data && !employeeResource.data.is_service_supervisor) {
			return next({ name: "ServiceHome" })
		}

		if (
			(to.name === "ExecutiveExpenseManager" || to.name === "ExecutiveExpenseHistory") &&
			employeeResource.data &&
			!employeeResource.data.is_sales_person
		) {
			return next({ name: "Home" })
		}
	}

	next()
})

router.afterEach(() => {
	document.title = "MobiBiz Lite"
})

export default router