import frappeUIPreset from "frappe-ui/src/tailwind/preset"

const turquoise = {
	50: '#f0fdfc',
	100: '#d3faf6',
	200: '#aaf4ec',
	300: '#73ebd9',
	400: '#40e0d0', // User Specified Turquoise
	500: '#1fc7b6',
	600: '#139f92',
	700: '#137e75',
	800: '#14645d',
	900: '#15534e',
	950: '#06312e',
}

/** @type {import('tailwindcss').Config} */
export default {
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			colors: {
				brand: turquoise,
				teal: turquoise,
				surface: {
					bg: '#f4f5f7',
					card: '#ffffff',
					subtle: '#f8fafc',
				}
			},
			screens: {
				standalone: {
					raw: "(display-mode: standalone)",
				},
			},
		},
	},
	plugins: [],
}
