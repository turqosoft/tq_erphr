<template>
	<div class="min-h-screen w-full bg-[#f8fafc] text-slate-900 flex flex-col justify-center items-center p-4 sm:p-6 font-sans relative overflow-x-hidden">
		<!-- Subtle Background ambient glow on desktop -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-400/20 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-teal-200/30 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full max-w-sm sm:max-w-md my-auto relative z-10 space-y-4">
			
			<!-- Top Hero Brand Section (Mobile App Style) -->
			<div class="text-center pt-2 pb-1">
				<div class="inline-flex justify-center mb-3">
					<div class="p-3 bg-white rounded-3xl shadow-lg shadow-teal-700/10 border border-slate-100 flex items-center justify-center max-w-[220px]">
						<img :src="mobibizLogo" alt="MobiBiz" class="h-12 w-auto object-contain" />
					</div>
				</div>

				<h1 class="text-2xl font-black tracking-tight text-slate-900">MobiBiz Lite</h1>
				<div class="flex items-center justify-center space-x-1.5 mt-1">
					<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
						Employee Portal
					</span>
					<span class="text-slate-300">•</span>
					<span class="text-xs text-slate-500 font-medium">Business Anytime</span>
				</div>
			</div>

			<!-- Modern White Login Card -->
			<div class="bg-white rounded-3xl shadow-xl shadow-slate-200/60 border border-slate-200/90 p-6 sm:p-7 space-y-5">
				<div>
					<h2 class="text-lg font-bold text-slate-900 tracking-tight">Sign In</h2>
					<p class="text-xs text-slate-500 mt-0.5">Enter your credentials to access your account</p>
				</div>

				<form class="space-y-4" @submit.prevent="handleLogin">
					<!-- Error Alert -->
					<div
						v-if="errorMessage"
						class="p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start space-x-2 animate-shake"
					>
						<svg class="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span class="break-words font-medium leading-tight">{{ errorMessage }}</span>
					</div>

					<!-- Email / Mobile / Username Input -->
					<div class="space-y-1.5">
						<label class="block text-xs font-bold text-slate-700">
							Email, Mobile Number or Username
						</label>
						<div class="relative group">
							<div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition">
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
								</svg>
							</div>
							<input
								v-model="email"
								type="text"
								required
								autocomplete="username"
								placeholder="Email, mobile number or username"
								class="w-full pl-10 pr-4 py-3 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 focus:bg-white text-slate-900 placeholder-slate-400 text-sm font-medium focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition outline-none"
							/>
						</div>
					</div>

					<!-- Password Input -->
					<div class="space-y-1.5">
						<label class="block text-xs font-bold text-slate-700">
							Password
						</label>
						<div class="relative group">
							<div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition">
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
								</svg>
							</div>
							<input
								v-model="password"
								:type="showPassword ? 'text' : 'password'"
								required
								autocomplete="current-password"
								placeholder="••••••••"
								class="w-full pl-10 pr-10 py-3 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 focus:bg-white text-slate-900 placeholder-slate-400 text-sm font-medium focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition outline-none"
							/>
							<button
								type="button"
								@click="showPassword = !showPassword"
								class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 transition"
								aria-label="Toggle password visibility"
							>
								<svg v-if="!showPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								</svg>
								<svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Submit Button -->
					<button
						type="submit"
						:disabled="loading"
						class="w-full pt-3 pb-3 px-4 rounded-xl bg-gradient-to-r from-brand-600 via-brand-500 to-brand-600 hover:from-brand-500 hover:to-brand-400 active:scale-[0.98] text-white font-bold text-sm shadow-md shadow-brand-500/30 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 transition-all flex items-center justify-center space-x-2 disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
					>
						<svg
							v-if="loading"
							class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
							fill="none"
							viewBox="0 0 24 24"
						>
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
						</svg>
						<span>{{ loading ? "Signing in..." : "Sign in to Portal" }}</span>
					</button>
				</form>
			</div>

			<!-- Footer info & security badge -->
			<div class="text-center pt-2 space-y-1">
				<p class="inline-flex items-center text-[11px] text-slate-400 font-medium">
					<svg class="w-3.5 h-3.5 text-slate-400 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
					</svg>
					Enterprise Secure Authentication
				</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue"
import mobibizLogo from "@/assets/mobibiz_logo.png"
import { session } from "@/data/session"

const email = ref("")
const password = ref("")
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref("")

async function handleLogin() {
	if (!email.value || !password.value) {
		errorMessage.value = "Please provide both email and password"
		return
	}

	loading.value = true
	errorMessage.value = ""

	try {
		await session.login(email.value, password.value)
	} catch (err) {
		if (err && err.messages && err.messages.length) {
			errorMessage.value = err.messages.join("\n")
		} else if (err && err.message) {
			errorMessage.value = err.message
		} else {
			errorMessage.value = "Invalid username or password. Please try again."
		}
	} finally {
		loading.value = false
	}
}
</script>
