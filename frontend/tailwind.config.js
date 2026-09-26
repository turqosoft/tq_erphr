import frappeUIPreset from "frappe-ui/src/tailwind/preset"
import colors from "tailwindcss/colors"

const turquoise = {
	50: '#f0fdfc',
	100: '#d5faf5',
	200: '#aaf4ec',
	300: '#6eeadb',
	400: '#40e0d0', // Exact User-Specified Turquoise (#40E0D0)
	500: '#20cdba',
	600: '#14b8a6',
	700: '#0d9488',
	800: '#115e59',
	900: '#134e4a',
	950: '#042f2c',
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
				rose: colors.rose,
				slate: colors.slate,
				emerald: colors.emerald,
				red: colors.red,
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
