import { createRouter, createWebHistory } from "vue-router"
import { session } from "@/data/session"
import { employeeResource } from "@/data/employee"

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
		path: "/login",
		name: "Login",
		component: () => import("@/views/Login.vue"),
	},
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

