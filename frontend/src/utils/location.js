export function getCurrentLocation() {
	return new Promise((resolve) => {
		if (!navigator.geolocation) return resolve(null)
		navigator.geolocation.getCurrentPosition(
			(p) => resolve({ latitude: p.coords.latitude, longitude: p.coords.longitude }),
			() => resolve(null),
			{ enableHighAccuracy: true, timeout: 6000, maximumAge: 5000 }
		)
	})
}