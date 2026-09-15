import { createResource } from "frappe-ui"
import router from "@/router"

export const employeeResource = createResource({
	url: "tq_erphr.pwa_api.get_current_employee_info",
	cache: "tq_erphr:employee",
	onError(error) {
		if (error && error.exc_type === "AuthenticationError") {
			router.push("/login")
		}
	},
})
