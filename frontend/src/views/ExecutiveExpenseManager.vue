<template>
	<div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-start items-center p-0 sm:p-4 font-sans selection:bg-teal-500 selection:text-white relative overflow-x-hidden pb-24">
		<!-- Background ambient soft gradients for desktop container -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-emerald-200/20 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full sm:max-w-md bg-[#f8fafc] min-h-screen sm:min-h-[720px] sm:rounded-3xl sm:shadow-2xl sm:border sm:border-slate-200/80 flex flex-col justify-between relative z-10 overflow-hidden pb-6">
			
			<!-- Mobile Top Header -->
			<header class="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200/70 px-4 py-3 sm:px-5 transition-all shadow-xs">
				<div class="flex items-center justify-between">
					<!-- Back Navigation & Title -->
					<div class="flex items-center space-x-2.5">
						<button
							@click="goBack"
							class="p-2 -ml-1 rounded-2xl text-slate-600 hover:text-teal-700 hover:bg-teal-50/80 active:scale-95 transition"
							title="Back to Dashboard"
						>
							<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
							</svg>
						</button>
						<div>
							<h1 class="text-sm font-bold text-slate-900 leading-tight">Expense Manager</h1>
							<p class="text-[10px] font-medium text-slate-500 leading-none">Daily Travel & Site Tracking</p>
						</div>
					</div>

					<!-- Header Actions -->
					<div class="flex items-center space-x-1.5">
						<!-- History Button -->
						<button
							@click="openHistoryModal"
							class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition"
							title="View Past Trips"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
						</button>

						<!-- Refresh Button -->
						<button
							@click="refreshData"
							:disabled="todayEemResource.loading"
							class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition"
							title="Refresh trip data"
						>
							<svg
								class="w-4 h-4"
								:class="{ 'animate-spin text-teal-600': todayEemResource.loading }"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
						</button>
					</div>
				</div>
			</header>

			<!-- Main Scrollable Body -->
			<main class="flex-1 w-full px-4 py-4 space-y-4 overflow-y-auto">
				<!-- Loading State -->
				<div v-if="todayEemResource.loading && !eemDoc && !tripStatus" class="p-8 text-center bg-white rounded-3xl shadow-sm border border-slate-100 my-6">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent mb-3"></div>
					<h3 class="text-sm font-bold text-slate-900">Loading Trip Details...</h3>
					<p class="text-xs text-slate-500 mt-0.5">Fetching today's expense manager status</p>
				</div>

				<div v-else class="space-y-4">
					<!-- Date & Trip Status Hero Banner (Light Turquoise & Teal Theme) -->
					<div class="relative overflow-hidden rounded-3xl bg-gradient-to-tr from-teal-700 via-teal-600 to-teal-500 text-white p-5 shadow-lg shadow-teal-700/20">
						<div class="absolute -right-8 -bottom-8 w-40 h-40 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>

						<div class="relative z-10 flex items-center justify-between">
							<div>
								<div class="flex items-center space-x-2">
									<span class="text-[10px] uppercase tracking-wider font-bold text-teal-100">
										{{ liveDateFormatted }}
									</span>
									<span v-if="eemDoc?.name" class="font-mono text-[9px] bg-white/20 px-2 py-0.5 rounded-lg text-white font-semibold">
										{{ eemDoc.name }}
									</span>
								</div>
								<h2 class="text-lg font-black tracking-tight text-white mt-1">
									{{ tripStatusTitle }}
								</h2>
							</div>

							<!-- Status Pill -->
							<div>
								<span
									class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border shadow-sm"
									:class="statusBadgeClasses"
								>
									<span
										v-if="tripStatus === 'IN_PROGRESS'"
										class="w-2 h-2 rounded-full bg-emerald-300 mr-1.5 animate-pulse"
									></span>
									{{ tripStatusLabel }}
								</span>
							</div>
						</div>

						<!-- Quick Mini Metrics Bar inside Hero -->
						<div v-if="tripStatus === 'IN_PROGRESS' || tripStatus === 'COMPLETED' || tripStatus === 'READY_TO_SUBMIT'" class="mt-4 pt-3 border-t border-white/15 grid grid-cols-3 gap-2 text-center text-xs">
							<div class="bg-white/10 rounded-2xl p-2.5 backdrop-blur-sm border border-white/10">
								<span class="text-[10px] text-teal-100 block font-medium">Vehicle</span>
								<span class="font-bold text-white text-xs truncate block mt-0.5">{{ eemDoc?.vehicle_type || '-' }}</span>
							</div>
							<div class="bg-white/10 rounded-2xl p-2.5 backdrop-blur-sm border border-white/10">
								<span class="text-[10px] text-teal-100 block font-medium">{{ tripStatus === 'IN_PROGRESS' ? 'Visits' : 'Distance' }}</span>
								<span class="font-bold text-white text-xs mt-0.5 block">{{ tripStatus === 'IN_PROGRESS' ? siteVisitsList.length : (eemDoc?.total_distance || 0) + ' km' }}</span>
							</div>
							<div class="bg-white/10 rounded-2xl p-2.5 backdrop-blur-sm border border-white/10">
								<span class="text-[10px] text-teal-100 block font-medium">{{ tripStatus === 'IN_PROGRESS' ? 'Expenses' : 'Total Claim' }}</span>
								<span class="font-bold text-white text-xs mt-0.5 block">₹{{ formatAmount(tripStatus === 'IN_PROGRESS' ? totalExpensesSum : (eemDoc?.total_expense ?? eemDoc?.total_claim_amount ?? totalExpensesSum ?? 0)) }}</span>
							</div>
						</div>
					</div>

					<!-- ========================================================= -->
					<!-- PHASE 1: TRIP NOT STARTED VIEW                            -->
					<!-- ========================================================= -->
					<div v-if="tripStatus === 'NOT_STARTED'" class="bg-white rounded-3xl p-5 shadow-sm border border-slate-100 space-y-4">
						<div class="flex items-center space-x-2.5 pb-2.5 border-b border-slate-100">
							<div class="p-2.5 rounded-2xl bg-teal-50 text-teal-700 border border-teal-100">
								<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
								</svg>
							</div>
							<div>
								<h3 class="font-bold text-slate-900 text-sm">Start Today's Travel Day</h3>
								<p class="text-[11px] text-slate-500">Record vehicle and starting odometer reading</p>
							</div>
						</div>

						<!-- Vehicle Type Selection (Mobile 3-Card Grid) -->
						<div class="space-y-1.5">
							<label class="block text-xs font-bold text-slate-700">Select Vehicle Type <span class="text-rose-500">*</span></label>
							<div class="grid grid-cols-3 gap-2">
								<button
									type="button"
									@click="startForm.vehicle_type = 'Two Wheeler'"
									class="p-3 rounded-2xl border text-center transition-all flex flex-col items-center justify-center space-y-1 active:scale-95"
									:class="startForm.vehicle_type === 'Two Wheeler' ? 'border-teal-500 bg-teal-50/70 text-teal-950 ring-2 ring-teal-500/30 shadow-sm' : 'border-slate-200/90 bg-white text-slate-700 hover:bg-slate-50'"
								>
									<span class="text-xl">🛵</span>
									<span class="text-xs font-bold leading-tight">2-Wheeler</span>
									<span class="text-[9px] text-slate-500 font-medium">Bike / Scooter</span>
								</button>

								<button
									type="button"
									@click="startForm.vehicle_type = 'Four Wheeler'"
									class="p-3 rounded-2xl border text-center transition-all flex flex-col items-center justify-center space-y-1 active:scale-95"
									:class="startForm.vehicle_type === 'Four Wheeler' ? 'border-teal-500 bg-teal-50/70 text-teal-950 ring-2 ring-teal-500/30 shadow-sm' : 'border-slate-200/90 bg-white text-slate-700 hover:bg-slate-50'"
								>
									<span class="text-xl">🚗</span>
									<span class="text-xs font-bold leading-tight">4-Wheeler</span>
									<span class="text-[9px] text-slate-500 font-medium">Car / Van</span>
								</button>

								<button
									type="button"
									@click="startForm.vehicle_type = 'Other'"
									class="p-3 rounded-2xl border text-center transition-all flex flex-col items-center justify-center space-y-1 active:scale-95"
									:class="startForm.vehicle_type === 'Other' ? 'border-teal-500 bg-teal-50/70 text-teal-950 ring-2 ring-teal-500/30 shadow-sm' : 'border-slate-200/90 bg-white text-slate-700 hover:bg-slate-50'"
								>
									<span class="text-xl">🚌</span>
									<span class="text-xs font-bold leading-tight">Other / Public</span>
									<span class="text-[9px] text-slate-500 font-medium">Bus / Cab</span>
								</button>
							</div>
						</div>

						<!-- Start Odometer Input -->
						<div class="space-y-1.5">
							<label class="block text-xs font-bold text-slate-700">Start Odometer Reading (KM) <span class="text-rose-500">*</span></label>
							<div class="relative">
								<input
									type="number"
									step="0.1"
									v-model="startForm.start_odometerkm"
									placeholder="e.g. 12450.5"
									class="w-full px-4 py-3 text-sm font-mono font-bold rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 placeholder:font-normal placeholder:text-slate-400 transition"
								/>
								<span class="absolute right-4 top-3.5 text-xs font-bold text-slate-400">KM</span>
							</div>
							<p class="text-[10px] text-slate-500">Enter your vehicle's dashboard odometer before departure.</p>
						</div>

						<!-- GPS & Device Status Bar -->
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between text-[11px] text-slate-600">
							<div class="flex items-center space-x-2 truncate">
								<svg class="w-4 h-4 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
								</svg>
								<span class="truncate font-medium">{{ locationStatusText }}</span>
							</div>
							<span class="font-mono text-[10px] text-slate-400 flex-shrink-0">{{ liveTimeFormatted }}</span>
						</div>

						<!-- Start Trip Action Button -->
						<button
							@click="submitStartTrip"
							:disabled="isSubmittingStart"
							class="w-full py-3.5 px-4 rounded-2xl font-bold text-sm bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white shadow-md shadow-teal-600/20 flex items-center justify-center space-x-2 active:scale-[0.98] transition disabled:opacity-75"
						>
							<svg
								v-if="isSubmittingStart"
								class="animate-spin h-5 w-5 text-white"
								fill="none"
								viewBox="0 0 24 24"
							>
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
							</svg>
							<span>{{ isSubmittingStart ? 'Starting Trip...' : 'Start Travel Day' }}</span>
						</button>
					</div>

					<!-- ========================================================= -->
					<!-- PHASE 2: TRIP IN PROGRESS / ACTIVE TRACKING VIEW          -->
					<!-- ========================================================= -->
					<div v-else-if="tripStatus === 'IN_PROGRESS'" class="space-y-4">
						<!-- Active Trip Summary Card -->
						<div class="bg-white rounded-3xl p-4 sm:p-5 shadow-sm border border-slate-100 space-y-3.5">
							<div class="flex items-center justify-between pb-2 border-b border-slate-100">
								<div class="flex items-center space-x-2">
									<span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
									<span class="text-xs font-bold text-slate-900">Trip In Progress</span>
								</div>
								<span class="text-[11px] text-slate-500 font-mono">Started: {{ formatLogTime(eemDoc?.start_time) }}</span>
							</div>

							<!-- Metrics Row -->
							<div class="grid grid-cols-2 gap-2.5 text-xs">
								<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100/90">
									<span class="text-[10px] text-slate-500 font-semibold block uppercase">Start Odometer</span>
									<span class="font-bold text-slate-900 font-mono text-sm mt-0.5 block">{{ eemDoc?.start_odometerkm || 0 }} KM</span>
								</div>
								<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100/90">
									<span class="text-[10px] text-slate-500 font-semibold block uppercase">Vehicle Type</span>
									<span class="font-bold text-teal-700 text-sm mt-0.5 block truncate">{{ eemDoc?.vehicle_type || 'Vehicle' }}</span>
								</div>
							</div>

							<!-- Action Buttons Grid (Mobile optimized) -->
							<div class="grid grid-cols-2 gap-2 pt-1">
								<button
									@click="openSiteVisitModal"
									class="py-3 px-3 rounded-2xl bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white font-bold text-xs flex items-center justify-center space-x-1.5 shadow-sm active:scale-[0.98] transition"
								>
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
									</svg>
									<span>+ Site Visit</span>
								</button>

								<button
									@click="openExpenseModal"
									class="py-3 px-3 rounded-2xl bg-white hover:bg-slate-50 text-slate-800 font-bold text-xs flex items-center justify-center space-x-1.5 border border-slate-200 active:scale-[0.98] transition shadow-xs"
								>
									<svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
									</svg>
									<span>+ Expense</span>
								</button>
							</div>

							<!-- End Trip Full Button -->
							<div class="pt-0.5">
								<button
									@click="openEndTripModal"
									class="w-full py-3 px-4 rounded-2xl font-bold text-xs bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200/80 flex items-center justify-center space-x-2 transition active:scale-[0.98]"
								>
									<svg class="w-4 h-4 text-amber-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
									</svg>
									<span>Finish & End Travel Day</span>
								</button>
							</div>
						</div>

						<!-- Tabbed Switcher for Child Tables -->
						<div class="bg-white rounded-3xl p-4 shadow-sm border border-slate-100 space-y-3.5">
							<!-- Tab Pills -->
							<div class="flex items-center space-x-1 p-1 bg-slate-100/80 rounded-2xl">
								<button
									@click="activeTab = 'visits'"
									class="flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all text-center flex items-center justify-center space-x-1.5"
									:class="activeTab === 'visits' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
								>
									<span>📍 Site Visits</span>
									<span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="activeTab === 'visits' ? 'bg-teal-50 text-teal-700' : 'bg-slate-200 text-slate-600'">
										{{ siteVisitsList.length }}
									</span>
								</button>

								<button
									@click="activeTab = 'expenses'"
									class="flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all text-center flex items-center justify-center space-x-1.5"
									:class="activeTab === 'expenses' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
								>
									<span>💰 Expenses</span>
									<span class="px-1.5 py-0.2 rounded-full text-[10px]" :class="activeTab === 'expenses' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-200 text-slate-600'">
										{{ expensesList.length }}
									</span>
								</button>
							</div>

							<!-- TAB 1: Site Visits List -->
							<div v-if="activeTab === 'visits'" class="space-y-2.5">
								<div v-if="siteVisitsList.length === 0" class="text-center py-6 text-xs text-slate-400 italic">
									No client site visits logged for this trip yet.
									<div class="mt-2">
										<button
											@click="openSiteVisitModal"
											class="text-xs font-bold text-teal-600 hover:underline"
										>
											+ Add First Site Visit
										</button>
									</div>
								</div>

								<div
									v-else
									v-for="(visit, idx) in siteVisitsList"
									:key="visit.name || idx"
									class="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-100 space-y-1.5 text-xs relative"
								>
									<div class="flex items-start justify-between">
										<div class="flex items-center space-x-2">
											<span class="w-5 h-5 rounded-full bg-teal-100 text-teal-800 font-bold text-[10px] flex items-center justify-center">
												{{ idx + 1 }}
											</span>
											<h4 class="font-bold text-slate-900 truncate max-w-[180px]">
												{{ visit.customer || visit.site || 'Site Location' }}
											</h4>
										</div>
										<span class="text-[10px] text-slate-500 font-mono">{{ formatLogTime(visit.checkin_time) }}</span>
									</div>

									<div class="flex items-center justify-between text-[11px] text-slate-600 pl-7">
										<span class="truncate max-w-[180px]">{{ visit.site || visit.location_name || 'Client Premises' }}</span>
										<span v-if="visit.actual_distance" class="text-teal-700 font-bold font-mono text-[11px] bg-teal-50 px-2 py-0.5 rounded-lg border border-teal-100">
											{{ visit.actual_distance }} km
										</span>
									</div>

									<p v-if="visit.remarks" class="text-[10px] text-slate-500 italic bg-white p-2 rounded-xl border border-slate-100 ml-7">
										"{{ visit.remarks }}"
									</p>

									<div v-if="(visit.site_lat && visit.site_long) || (visit.checkin_lat && visit.checkin_long)" class="text-[9px] text-slate-400 font-mono pl-7">
										📍 {{ Number(visit.site_lat || visit.checkin_lat).toFixed(4) }}, {{ Number(visit.site_long || visit.checkin_long).toFixed(4) }}
									</div>
								</div>
							</div>

							<!-- TAB 2: Daily Expenses List -->
							<div v-if="activeTab === 'expenses'" class="space-y-2.5">
								<div v-if="expensesList.length === 0" class="text-center py-6 text-xs text-slate-400 italic">
									No other daily expenses logged yet.
									<div class="mt-2">
										<button
											@click="openExpenseModal"
											class="text-xs font-bold text-teal-600 hover:underline"
										>
											+ Add Travel / Food / Toll Expense
										</button>
									</div>
								</div>

								<div
									v-else
									v-for="(exp, idx) in expensesList"
									:key="exp.name || idx"
									class="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-100 flex items-center justify-between text-xs"
								>
									<div class="space-y-0.5">
										<div class="flex items-center space-x-1.5">
											<span class="font-bold text-slate-900">{{ exp.expense_type }}</span>
										</div>
										<p v-if="exp.description" class="text-[10px] text-slate-500 truncate max-w-[200px]">
											{{ exp.description }}
										</p>
									</div>
									<div class="text-right">
										<span class="font-bold font-mono text-slate-900 text-sm">₹{{ formatAmount(exp.amount) }}</span>
									</div>
								</div>

								<!-- Total Expenses Sum Card -->
								<div v-if="expensesList.length > 0" class="pt-2 border-t border-slate-100 flex items-center justify-between px-1">
									<span class="text-xs font-bold text-slate-600">Total Expenses</span>
									<span class="text-sm font-bold font-mono text-emerald-700">₹{{ formatAmount(totalExpensesSum) }}</span>
								</div>
							</div>
						</div>
					</div>

					<!-- ========================================================= -->
					<!-- PHASE 3: COMPLETED / SUBMITTED DAY SUMMARY VIEW           -->
					<!-- ========================================================= -->
					<div v-else-if="tripStatus === 'COMPLETED' || tripStatus === 'READY_TO_SUBMIT'" class="bg-white rounded-3xl p-5 shadow-sm border border-slate-100 space-y-4">
						<div class="flex items-center space-x-2.5 pb-2.5 border-b border-slate-100">
							<div class="p-2.5 rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-100">
								<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
							</div>
							<div>
								<h3 class="font-bold text-slate-900 text-sm">Travel Day Summary</h3>
								<p class="text-[10px] text-slate-500">Document {{ eemDoc?.docstatus === 1 ? 'Submitted' : 'Saved Draft' }}</p>
							</div>
						</div>

						<!-- Comprehensive Stats Grid -->
						<div class="grid grid-cols-2 gap-2.5 text-xs">
							<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
								<span class="text-[10px] text-slate-500 uppercase font-semibold block">Total Travel Dist.</span>
								<span class="font-bold text-slate-900 font-mono text-sm mt-0.5 block">{{ eemDoc?.total_distance || 0 }} KM</span>
							</div>
							<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
								<span class="text-[10px] text-slate-500 uppercase font-semibold block">Travel Allowance</span>
								<span class="font-bold text-teal-700 font-mono text-sm mt-0.5 block">₹{{ formatAmount(eemDoc?.total_travel_expense || ((eemDoc?.total_distance || 0) * (eemDoc?.rate_per_km || 0))) }}</span>
							</div>
							<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
								<span class="text-[10px] text-slate-500 uppercase font-semibold block">Daily Expenses</span>
								<span class="font-bold text-slate-900 font-mono text-sm mt-0.5 block">₹{{ formatAmount(eemDoc?.total_other_expenses ?? eemDoc?.total_daily_expense ?? totalExpensesSum ?? 0) }}</span>
							</div>
							<div class="p-3 rounded-2xl bg-emerald-50/70 border border-emerald-100">
								<span class="text-[10px] text-emerald-800 uppercase font-bold block">Grand Total Claim</span>
								<span class="font-black text-emerald-800 font-mono text-sm mt-0.5 block">₹{{ formatAmount(eemDoc?.total_expense ?? eemDoc?.total_claim_amount ?? 0) }}</span>
							</div>
						</div>

						<!-- Odometer Details -->
						<div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-2 text-xs">
							<div class="flex justify-between">
								<span class="text-slate-500">Start Odometer</span>
								<span class="font-mono font-bold text-slate-900">{{ eemDoc?.start_odometerkm || 0 }} KM ({{ formatLogTime(eemDoc?.start_time) }})</span>
							</div>
							<div class="flex justify-between">
								<span class="text-slate-500">End Odometer</span>
								<span class="font-mono font-bold text-slate-900">{{ eemDoc?.end_odometerkm || 0 }} KM ({{ formatLogTime(eemDoc?.end_time) }})</span>
							</div>
							<div class="flex justify-between pt-1.5 border-t border-slate-200/60 font-semibold">
								<span class="text-slate-700">Odometer Distance</span>
								<span class="font-mono text-teal-700 font-bold">{{ eemDoc?.odometer_distance || 0 }} KM</span>
							</div>
							<div v-if="eemDoc?.end_narration" class="pt-1.5 text-[11px] text-slate-600 italic bg-white p-2 rounded-xl border border-slate-100">
								"{{ eemDoc.end_narration }}"
							</div>
						</div>

						<!-- Site Visits Count / List Preview -->
						<div class="pt-1">
							<h4 class="text-xs font-bold text-slate-700 mb-2">Visits Logged ({{ siteVisitsList.length }})</h4>
							<div class="space-y-1.5 max-h-48 overflow-y-auto pr-1">
								<div
									v-for="(v, idx) in siteVisitsList"
									:key="v.name || idx"
									class="p-3 rounded-2xl bg-slate-50/80 border border-slate-100 flex items-center justify-between text-xs"
								>
									<div class="truncate max-w-[200px]">
										<span class="font-bold text-slate-900">{{ v.customer || v.site || 'Site' }}</span>
										<span class="text-[10px] text-slate-500 block truncate">{{ v.site || v.location_name || '-' }}</span>
									</div>
									<span class="text-teal-700 font-mono font-bold text-[11px] bg-teal-50 px-2 py-0.5 rounded-lg border border-teal-100">{{ v.actual_distance || 0 }} km</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</main>
		</div>

		<!-- ========================================================= -->
		<!-- MODAL: ADD SITE VISIT                                     -->
		<!-- ========================================================= -->
		<Dialog v-model="showSiteVisitModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">Record Site Visit</h2>
						<p class="text-[10px] text-slate-500">Adds site entry to Executive Expense Manager</p>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-3.5">
					<!-- Customer Selection -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Customer / Client</label>
						<select
							v-model="siteVisitForm.customer"
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 font-medium"
						>
							<option value="">Select Customer (or type custom site below)</option>
							<option
								v-for="c in customersList"
								:key="c.name"
								:value="c.name"
							>
								{{ c.customer_name || c.name }}
							</option>
						</select>
					</div>

					<!-- Site / Location Name -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Site / Branch Location</label>
						<input
							type="text"
							v-model="siteVisitForm.site"
							placeholder="e.g. Central Warehouse / Head Office"
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900"
						/>
					</div>

					<!-- Distance in KM -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Distance from Previous Stop (KM)</label>
						<input
							type="number"
							step="0.1"
							v-model="siteVisitForm.actual_distance"
							placeholder="0.0"
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 font-mono"
						/>
					</div>

					<!-- Remarks / Purpose -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Discussion Remarks / Purpose</label>
						<textarea
							v-model="siteVisitForm.remarks"
							rows="2"
							placeholder="Brief meeting notes or outcome..."
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900"
						></textarea>
					</div>

					<!-- GPS Indicator -->
					<div class="p-2.5 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
						<div class="flex items-center space-x-1.5 truncate">
							<svg class="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
							</svg>
							<span class="truncate">{{ locationStatusText }}</span>
						</div>
						<span class="text-[10px] font-mono text-slate-400">{{ liveTimeFormatted }}</span>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						:disabled="isSubmittingSiteVisit"
						@click="showSiteVisitModal = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Cancel
					</Button>
					<Button
						variant="solid"
						:loading="isSubmittingSiteVisit"
						@click="submitSiteVisit"
						class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl shadow-sm"
					>
						Save Visit
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- ========================================================= -->
		<!-- MODAL: ADD DAILY EXPENSE                                  -->
		<!-- ========================================================= -->
		<Dialog v-model="showExpenseModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">Add Daily Expense</h2>
						<p class="text-[10px] text-slate-500">Record food, toll, parking, or other claim</p>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-3.5">
					<!-- Expense Type -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Expense Type <span class="text-rose-500">*</span></label>
						<select
							v-model="expenseForm.expense_type"
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 font-medium"
						>
							<option value="">Select Expense Type</option>
							<option
								v-for="t in expenseTypesList"
								:key="t.name || t"
								:value="t.name || t"
							>
								{{ t.name || t }}
							</option>
						</select>
					</div>

					<!-- Amount -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Amount (₹) <span class="text-rose-500">*</span></label>
						<input
							type="number"
							step="1"
							v-model="expenseForm.amount"
							placeholder="0.00"
							class="w-full px-3.5 py-2.5 text-sm font-mono font-bold rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900"
						/>
					</div>

					<!-- Description -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Description / Bill Notes</label>
						<textarea
							v-model="expenseForm.description"
							rows="2"
							placeholder="e.g. Lunch with client, Toll plaza receipt..."
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900"
						></textarea>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						:disabled="isSubmittingExpense"
						@click="showExpenseModal = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Cancel
					</Button>
					<Button
						variant="solid"
						:loading="isSubmittingExpense"
						@click="submitExpense"
						class="px-4 py-2.5 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-2xl shadow-sm"
					>
						Add Expense
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- ========================================================= -->
		<!-- MODAL: END TRIP CONFIRMATION & DETAILS                    -->
		<!-- ========================================================= -->
		<Dialog v-model="showEndTripModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">Finish Travel Day</h2>
						<p class="text-[10px] text-slate-500">Record final odometer and complete day's log</p>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-3.5">
					<!-- Start Odometer Reference -->
					<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100 flex justify-between items-center text-xs">
						<span class="text-slate-500 font-medium">Start Odometer</span>
						<span class="font-bold font-mono text-slate-900">{{ eemDoc?.start_odometerkm || 0 }} KM</span>
					</div>

					<!-- End Odometer Reading -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">End Odometer Reading (KM) <span class="text-rose-500">*</span></label>
						<div class="relative">
							<input
								type="number"
								step="0.1"
								v-model="endForm.end_odometerkm"
								placeholder="e.g. 12495.0"
								class="w-full px-3.5 py-2.5 text-sm font-mono font-bold rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900"
							/>
							<span class="absolute right-3.5 top-2.5 text-xs font-bold text-slate-400">KM</span>
						</div>
						<span v-if="calculatedOdoDistance > 0" class="text-[11px] font-bold text-teal-700 mt-1 block font-mono">
							Calculated Distance: {{ calculatedOdoDistance.toFixed(1) }} KM
						</span>
					</div>

					<!-- Final Leg Distance -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Return Leg Distance (KM)</label>
						<input
							type="number"
							step="0.1"
							v-model="endForm.actual_end_distance"
							placeholder="Distance from last site to base (0.0)"
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 font-mono"
						/>
					</div>

					<!-- End Narration -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">End Narration / Summary Notes</label>
						<textarea
							v-model="endForm.end_narration"
							rows="2"
							placeholder="Summary of today's field visits and travel..."
							class="w-full px-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900"
						></textarea>
					</div>

					<!-- Submit Doc Toggle -->
					<div class="flex items-center space-x-2 pt-1">
						<input
							type="checkbox"
							id="submit_doc_check"
							v-model="endForm.submit_doc"
							class="rounded text-teal-600 focus:ring-teal-500 h-4 w-4"
						/>
						<label for="submit_doc_check" class="text-xs text-slate-700 font-medium">
							Finalize & Submit document (Locks edits)
						</label>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						:disabled="isSubmittingEnd"
						@click="showEndTripModal = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Cancel
					</Button>
					<Button
						variant="solid"
						:loading="isSubmittingEnd"
						@click="submitEndTrip"
						class="px-4 py-2.5 text-xs font-bold text-white bg-amber-600 hover:bg-amber-500 rounded-2xl shadow-sm"
					>
						Complete Trip
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- ========================================================= -->
		<!-- MODAL: TRIP HISTORY                                       -->
		<!-- ========================================================= -->
		<Dialog v-model="showHistoryModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
					<h2 class="text-base font-bold text-slate-900">Past Travel Logs</h2>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2.5 max-h-80 overflow-y-auto pr-1">
					<div v-if="eemHistoryResource.loading" class="py-6 text-center text-xs text-slate-500">
						<div class="inline-block animate-spin rounded-full h-5 w-5 border-2 border-teal-500 border-t-transparent mb-2"></div>
						<p>Loading trip history...</p>
					</div>
					<div v-else-if="!historyRecords || historyRecords.length === 0" class="py-6 text-center text-xs text-slate-400">
						No past travel records found.
					</div>
					<div
						v-else
						v-for="rec in historyRecords"
						:key="rec.name"
						class="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1 text-xs"
					>
						<div class="flex items-center justify-between">
							<span class="font-bold text-slate-900">{{ formatDate(rec.date) }}</span>
							<span
								class="px-2 py-0.5 rounded-full text-[10px] font-bold"
								:class="rec.docstatus === 1 ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-700'"
							>
								{{ rec.docstatus === 1 ? 'Submitted' : 'Draft' }}
							</span>
						</div>
						<div class="flex items-center justify-between text-[11px] text-slate-600">
							<span>{{ rec.vehicle_type || 'Vehicle' }}</span>
							<span class="font-mono font-bold text-slate-900">{{ rec.total_distance || 0 }} km</span>
						</div>
						<div class="flex items-center justify-between text-[10px] text-slate-400 pt-0.5 font-mono">
							<span>{{ rec.name }}</span>
							<span class="font-bold text-emerald-700">₹{{ formatAmount(rec.total_expense ?? rec.total_claim_amount ?? 0) }}</span>
						</div>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-between w-full pt-1">
					<Button
						variant="subtle"
						@click="eemHistoryResource.fetch()"
						:loading="eemHistoryResource.loading"
						class="px-3 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Refresh
					</Button>
					<Button
						variant="solid"
						@click="showHistoryModal = false"
						class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl"
					>
						Close
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- ========================================================= -->
		<!-- MODAL: LOCATION PERMISSION REQUIRED                       -->
		<!-- ========================================================= -->
		<Dialog v-model="showLocationModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">
							{{ locationModalTitle }}
						</h2>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2.5 text-xs text-slate-600 leading-relaxed">
					<p>
						{{ locationModalDescription }}
					</p>
					<div class="p-3 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-amber-900 space-y-1">
						<p class="font-bold">Please follow these steps:</p>
						<ul class="list-disc list-inside space-y-0.5 text-[11px]">
							<li>Turn on <strong>Location / GPS</strong> on your mobile phone.</li>
							<li>Allow <strong>Location Permission</strong> in your browser prompt.</li>
						</ul>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						@click="showLocationModal = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Dismiss
					</Button>
					<Button
						variant="solid"
						:loading="isAcquiringLocation"
						@click="retryAcquireLocation"
						class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl shadow-sm"
					>
						Enable & Retry GPS
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- ========================================================= -->
		<!-- MODAL: CHECK-IN REQUIRED TO START TRAVEL                  -->
		<!-- ========================================================= -->
		<Dialog v-model="showCheckinRequiredModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">Attendance Check-In Required</h2>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2 text-xs text-slate-600 leading-relaxed">
					<p>
						You cannot start your travel day before completing daily attendance <strong>Check-In</strong>.
					</p>
					<p class="text-[11px] text-slate-500">
						Please return to your dashboard and perform Check In before starting your travel day.
					</p>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						@click="showCheckinRequiredModal = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Cancel
					</Button>
					<Button
						variant="solid"
						@click="goToHomeCheckin"
						class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl shadow-sm"
					>
						Go to Check-In
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- Global Mobile Bottom Navigation Bar -->
		<BottomNavBar
			active-tab="eem"
			:is-trip-active="tripStatus === 'IN_PROGRESS'"
			:show-eem="!!employeeResource.data?.is_sales_person"
			@open-history="showHistoryModal = true"
			@open-profile="goToHomeProfile"
		/>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import { Dialog, Button } from "frappe-ui"
import BottomNavBar from "@/components/BottomNavBar.vue"
import { employeeResource } from "@/data/employee"
import { checkinStatusResource } from "@/data/checkin"
import {
	todayEemResource,
	startTripResource,
	addEemSiteVisitResource,
	addEemExpenseResource,
	endTripResource,
	eemHistoryResource,
	expenseTypesResource,
	customersResource,
} from "@/data/eem"

const router = useRouter()

// UI state
const activeTab = ref("visits")
const showSiteVisitModal = ref(false)
const showExpenseModal = ref(false)
const showEndTripModal = ref(false)
const showHistoryModal = ref(false)
const showLocationModal = ref(false)
const showCheckinRequiredModal = ref(false)
const isAcquiringLocation = ref(false)
const locationModalContext = ref("start") // 'start' | 'site' | 'end'

// Geolocation state
const locationCoords = ref(null)
const locationStatusText = ref("GPS Ready")

// Live clock
const currentTime = ref(new Date())
let clockTimer = null

// Submission states
const isSubmittingStart = ref(false)
const isSubmittingSiteVisit = ref(false)
const isSubmittingExpense = ref(false)
const isSubmittingEnd = ref(false)

// Forms
const startForm = ref({
	vehicle_type: "Two Wheeler",
	start_odometerkm: "",
})

const siteVisitForm = ref({
	customer: "",
	site: "",
	actual_distance: "",
	remarks: "",
})

const expenseForm = ref({
	expense_type: "",
	amount: "",
	description: "",
})

const endForm = ref({
	end_odometerkm: "",
	actual_end_distance: "",
	end_narration: "",
	submit_doc: true,
})

// Data Accessors
const eemData = computed(() => todayEemResource.data || {})
const eemDoc = computed(() => eemData.value.doc)
const tripStatus = computed(() => eemData.value.trip_status || "NOT_STARTED")
const isCheckedIn = computed(() => {
	if (eemData.value && eemData.value.is_checked_in !== undefined) {
		return Boolean(eemData.value.is_checked_in)
	}
	if (checkinStatusResource.data && checkinStatusResource.data.next_action) {
		return checkinStatusResource.data.next_action === "OUT"
	}
	return false
})
const rates = computed(() => eemData.value.rates || { two_wheeler: 3.5, four_wheeler: 7.0, other: 2.0 })
const siteVisitsList = computed(() => eemDoc.value?.employee_site_tracking || [])
const expensesList = computed(() => eemDoc.value?.employee_expense_tracking || [])
const customersList = computed(() => customersResource.data || [])
const expenseTypesList = computed(() => expenseTypesResource.data || ["Food", "Toll", "Parking", "Fuel", "Other"])
const historyRecords = computed(() => eemHistoryResource.data || [])

const totalExpensesSum = computed(() => {
	if (!expensesList.value || expensesList.value.length === 0) return 0
	return expensesList.value.reduce((sum, item) => sum + (Number(item.amount) || 0), 0)
})

const calculatedOdoDistance = computed(() => {
	const start = Number(eemDoc.value?.start_odometerkm) || 0
	const end = Number(endForm.value.end_odometerkm) || 0
	return end > start ? end - start : 0
})

// Status labels & badges
const tripStatusLabel = computed(() => {
	switch (tripStatus.value) {
		case "NOT_STARTED":
			return "Not Started"
		case "IN_PROGRESS":
			return "In Progress"
		case "READY_TO_SUBMIT":
			return "Ready to Submit"
		case "COMPLETED":
			return "Completed"
		default:
			return "Unknown"
	}
})

const tripStatusTitle = computed(() => {
	switch (tripStatus.value) {
		case "NOT_STARTED":
			return "Ready to Travel?"
		case "IN_PROGRESS":
			return "Active Travel Day"
		case "READY_TO_SUBMIT":
			return "Trip Finished (Draft)"
		case "COMPLETED":
			return "Day Completed & Logged"
		default:
			return "Executive Expense Manager"
	}
})

const statusBadgeClasses = computed(() => {
	switch (tripStatus.value) {
		case "NOT_STARTED":
			return "bg-white/20 text-white border-white/30"
		case "IN_PROGRESS":
			return "bg-emerald-300 text-emerald-950 border-emerald-200 font-extrabold"
		case "READY_TO_SUBMIT":
			return "bg-amber-300 text-amber-950 border-amber-200 font-bold"
		case "COMPLETED":
			return "bg-emerald-400 text-white border-emerald-300 font-bold"
		default:
			return "bg-white/20 text-white border-white/30"
	}
})

const locationModalTitle = computed(() => {
	switch (locationModalContext.value) {
		case "site":
			return "GPS Required for Site Visit"
		case "end":
			return "GPS Required to Finish Trip"
		default:
			return "Location Access Required"
	}
})

const locationModalDescription = computed(() => {
	switch (locationModalContext.value) {
		case "site":
			return "Precise GPS coordinates are mandatory to log each customer site visit and record accurate stop locations."
		case "end":
			return "GPS Location is required to finish your travel day and record return odometer coordinates."
		default:
			return "GPS Location is mandatory to start your travel day and record departure coordinates."
	}
})

// Clock Formatting
const liveTimeFormatted = computed(() => {
	return currentTime.value.toLocaleTimeString([], {
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
	})
})

const liveDateFormatted = computed(() => {
	return currentTime.value.toLocaleDateString([], {
		weekday: "short",
		day: "numeric",
		month: "short",
		year: "numeric",
	})
})

// Geolocation helper
function getCurrentLocation() {
	return new Promise((resolve) => {
		if (!navigator.geolocation) {
			locationStatusText.value = "📍 GPS not supported"
			resolve(null)
			return
		}
		navigator.geolocation.getCurrentPosition(
			(position) => {
				const coords = {
					latitude: position.coords.latitude,
					longitude: position.coords.longitude,
				}
				locationCoords.value = coords
				locationStatusText.value = `📍 GPS: ${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)}`
				resolve(coords)
			},
			(err) => {
				console.warn("GPS error:", err.message)
				locationStatusText.value = "📍 GPS not enabled"
				resolve(null)
			},
			{ enableHighAccuracy: true, timeout: 6000, maximumAge: 5000 }
		)
	})
}

// Navigation & Modal triggers
function goBack() {
	router.push("/")
}

function goToHomeProfile() {
	router.push("/?openProfile=1")
}

function goToHomeCheckin() {
	showCheckinRequiredModal.value = false
	router.push("/")
}

async function retryAcquireLocation() {
	isAcquiringLocation.value = true
	const coords = await getCurrentLocation()
	isAcquiringLocation.value = false

	if (coords && (coords.latitude || coords.longitude)) {
		showLocationModal.value = false
	} else {
		alert("GPS location could not be acquired. Please verify that Location / GPS is turned ON and location permission is granted in your browser settings.")
	}
}

function refreshData() {
	todayEemResource.fetch()
	checkinStatusResource.fetch()
	customersResource.fetch()
	expenseTypesResource.fetch()
}

function openHistoryModal() {
	showHistoryModal.value = true
	eemHistoryResource.fetch()
}

async function openSiteVisitModal() {
	siteVisitForm.value = {
		customer: "",
		site: "",
		actual_distance: "",
		remarks: "",
	}
	customersResource.fetch()
	getCurrentLocation()
	showSiteVisitModal.value = true
}

function openExpenseModal() {
	expenseForm.value = {
		expense_type: expenseTypesList.value[0]?.name || expenseTypesList.value[0] || "",
		amount: "",
		description: "",
	}
	expenseTypesResource.fetch()
	showExpenseModal.value = true
}

function openEndTripModal() {
	endForm.value = {
		end_odometerkm: "",
		actual_end_distance: "",
		end_narration: "",
		submit_doc: true,
	}
	getCurrentLocation()
	showEndTripModal.value = true
}

// Action Handlers
async function submitStartTrip() {
	if (!startForm.value.vehicle_type) {
		alert("Please select a vehicle type.")
		return
	}
	if (!startForm.value.start_odometerkm && startForm.value.start_odometerkm !== 0) {
		alert("Please enter the starting odometer reading in KM.")
		return
	}

	isSubmittingStart.value = true
	const coords = await getCurrentLocation()
	if (!coords || (!coords.latitude && !coords.longitude)) {
		locationModalContext.value = "start"
		showLocationModal.value = true
		isSubmittingStart.value = false
		return
	}

	try {
		await startTripResource.submit({
			vehicle_type: startForm.value.vehicle_type,
			start_odometerkm: Number(startForm.value.start_odometerkm),
			start_lat: coords.latitude,
			start_long: coords.longitude,
		})

		await todayEemResource.fetch()
	} catch (err) {
		console.error("Error starting trip:", err)
		alert(err.messages?.[0] || err.message || "Failed to start trip.")
	} finally {
		isSubmittingStart.value = false
	}
}

async function submitSiteVisit() {
	if (!siteVisitForm.value.customer && !siteVisitForm.value.site) {
		alert("Please select a customer or specify a site location.")
		return
	}

	isSubmittingSiteVisit.value = true
	const coords = await getCurrentLocation()
	if (!coords || (!coords.latitude && !coords.longitude)) {
		locationModalContext.value = "site"
		showLocationModal.value = true
		isSubmittingSiteVisit.value = false
		return
	}

	try {
		await addEemSiteVisitResource.submit({
			customer: siteVisitForm.value.customer,
			site: siteVisitForm.value.site,
			remarks: siteVisitForm.value.remarks,
			actual_distance: Number(siteVisitForm.value.actual_distance) || 0,
			latitude: coords.latitude,
			longitude: coords.longitude,
		})

		showSiteVisitModal.value = false
		await todayEemResource.fetch()
	} catch (err) {
		console.error("Error adding site visit:", err)
		alert(err.messages?.[0] || err.message || "Failed to log site visit.")
	} finally {
		isSubmittingSiteVisit.value = false
	}
}

async function submitExpense() {
	if (!expenseForm.value.expense_type) {
		alert("Please select an expense type.")
		return
	}
	if (!expenseForm.value.amount || Number(expenseForm.value.amount) <= 0) {
		alert("Please enter a valid expense amount.")
		return
	}

	isSubmittingExpense.value = true
	try {
		await addEemExpenseResource.submit({
			expense_type: expenseForm.value.expense_type,
			amount: Number(expenseForm.value.amount),
			description: expenseForm.value.description,
		})

		showExpenseModal.value = false
		await todayEemResource.fetch()
	} catch (err) {
		console.error("Error adding expense:", err)
		alert(err.messages?.[0] || err.message || "Failed to add expense.")
	} finally {
		isSubmittingExpense.value = false
	}
}

async function submitEndTrip() {
	const endOdo = Number(endForm.value.end_odometerkm)
	const startOdo = Number(eemDoc.value?.start_odometerkm) || 0

	if (!endForm.value.end_odometerkm && endForm.value.end_odometerkm !== 0) {
		alert("Please enter the end odometer reading in KM.")
		return
	}

	if (endOdo < startOdo) {
		alert(`End odometer (${endOdo}) cannot be less than start odometer (${startOdo}).`)
		return
	}

	isSubmittingEnd.value = true
	const coords = await getCurrentLocation()
	if (!coords || (!coords.latitude && !coords.longitude)) {
		locationModalContext.value = "end"
		showLocationModal.value = true
		isSubmittingEnd.value = false
		return
	}

	try {
		await endTripResource.submit({
			end_odometerkm: endOdo,
			actual_end_distance: Number(endForm.value.actual_end_distance) || 0,
			end_narration: endForm.value.end_narration,
			submit_doc: endForm.value.submit_doc ? 1 : 0,
			end_lat: coords.latitude,
			end_long: coords.longitude,
		})

		showEndTripModal.value = false
		await todayEemResource.fetch()
	} catch (err) {
		console.error("Error ending trip:", err)
		alert(err.messages?.[0] || err.message || "Failed to end trip.")
	} finally {
		isSubmittingEnd.value = false
	}
}

// Formatters
function formatAmount(val) {
	const num = Number(val) || 0
	return num.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatLogTime(timeStr) {
	if (!timeStr) return "-"
	const d = new Date(timeStr)
	if (isNaN(d.getTime())) return timeStr
	return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

function formatDate(dateStr) {
	if (!dateStr) return "-"
	const d = new Date(dateStr)
	if (isNaN(d.getTime())) return dateStr
	return d.toLocaleDateString([], { day: "2-digit", month: "short", year: "numeric" })
}

onMounted(async () => {
	if (!employeeResource.data && !employeeResource.loading) {
		await employeeResource.fetch()
	}
	if (employeeResource.data && !employeeResource.data.is_sales_person) {
		router.replace("/")
		return
	}

	clockTimer = setInterval(() => {
		currentTime.value = new Date()
	}, 1000)

	getCurrentLocation()
	todayEemResource.fetch()
	checkinStatusResource.fetch()
})

onUnmounted(() => {
	if (clockTimer) clearInterval(clockTimer)
})
</script>
