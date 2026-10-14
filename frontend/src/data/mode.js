import { ref } from "vue"
import { employeeResource } from "./employee"

const KEY = "mobibiz_mode"
export const mode = ref(localStorage.getItem(KEY))

export const availableModes = () => employeeResource.data?.available_modes || ["sales"]

export function setMode(m) {
	mode.value = m
	localStorage.setItem(KEY, m)
}
export function resetMode() {
	mode.value = null
	localStorage.removeItem(KEY)
}
export function ensureMode() {
	const modes = availableModes()
	if (!modes.includes(mode.value)) {
		setMode(employeeResource.data?.default_mode || modes[0])
	}
	return mode.value
}