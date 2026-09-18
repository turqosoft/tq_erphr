import { ref, reactive } from "vue"

export const toastState = reactive({
	toasts: [],
})

let toastIdCounter = 0

export function showToast({ type = "info", title = "", message = "", duration = 4000 }) {
	const id = ++toastIdCounter

	// Set sensible default titles based on type if omitted
	if (!title) {
		switch (type) {
			case "warning":
				title = "Action Required"
				break
			case "error":
				title = "Error Occurred"
				break
			case "success":
				title = "Success"
				break
			default:
				title = "Notice"
				break
		}
	}

	const newToast = {
		id,
		type,
		title,
		message,
		duration,
		timer: null,
		createdAt: Date.now(),
	}

	// Keep at most 3 simultaneous toasts to prevent screen clutter
	if (toastState.toasts.length >= 3) {
		const removed = toastState.toasts.shift()
		if (removed && removed.timer) clearTimeout(removed.timer)
	}

	if (duration > 0) {
		newToast.timer = setTimeout(() => {
			removeToast(id)
		}, duration)
	}

	toastState.toasts.push(newToast)
	return id
}

export function removeToast(id) {
	const idx = toastState.toasts.findIndex((t) => t.id === id)
	if (idx !== -1) {
		const toast = toastState.toasts[idx]
		if (toast.timer) clearTimeout(toast.timer)
		toastState.toasts.splice(idx, 1)
	}
}

export function clearAllToasts() {
	toastState.toasts.forEach((t) => {
		if (t.timer) clearTimeout(t.timer)
	})
	toastState.toasts = []
}

export const toast = {
	warning(message, title = "Action Required", duration = 4500) {
		if (typeof message === "object" && message !== null) {
			return showToast({ type: "warning", ...message })
		}
		return showToast({ type: "warning", title, message, duration })
	},
	error(message, title = "Error", duration = 5000) {
		if (typeof message === "object" && message !== null) {
			return showToast({ type: "error", ...message })
		}
		return showToast({ type: "error", title, message, duration })
	},
	success(message, title = "Success", duration = 3500) {
		if (typeof message === "object" && message !== null) {
			return showToast({ type: "success", ...message })
		}
		return showToast({ type: "success", title, message, duration })
	},
	info(message, title = "Notice", duration = 4000) {
		if (typeof message === "object" && message !== null) {
			return showToast({ type: "info", ...message })
		}
		return showToast({ type: "info", title, message, duration })
	},
	remove: removeToast,
	clear: clearAllToasts,
}

export default toast
