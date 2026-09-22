<template>
	<div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-start items-center p-0 sm:p-4 font-sans selection:bg-teal-500 selection:text-white relative overflow-x-hidden pb-24">
		<!-- Background ambient soft gradients for desktop container -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-emerald-200/20 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full sm:max-w-md bg-[#f8fafc] min-h-screen sm:min-h-[720px] sm:rounded-3xl sm:shadow-2xl sm:border sm:border-slate-200/80 flex flex-col justify-between relative z-10 overflow-hidden pb-6">
			
			<!-- Mobile Top Header (Fixed at top like BottomNavBar) -->
			<header class="fixed top-0 inset-x-0 z-40 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 shadow-[0_2px_16px_rgba(0,0,0,0.04)] px-3 py-2.5 sm:px-4 transition-all">
				<div class="max-w-md mx-auto flex items-center justify-between">
					<!-- Back Navigation & Title -->
					<div class="flex items-center space-x-2.5 min-w-0 flex-1 mr-2">
						<button
							@click="goBack"
							class="p-2 -ml-1 rounded-2xl text-slate-600 hover:text-teal-700 hover:bg-teal-50/80 active:scale-95 transition cursor-pointer flex-shrink-0"
							title="Back to Dashboard"
						>
							<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
							</svg>
						</button>
						<div class="min-w-0 flex-1">
							<h1 class="text-sm font-bold text-slate-900 leading-tight truncate">Expense Manager</h1>
							<p class="text-[10px] font-medium text-slate-500 leading-none flex items-center gap-1 mt-0.5 truncate">
								<span v-if="employee?.company_name" class="font-semibold text-teal-700">{{ employee.company_name }} •</span>
								<span class="truncate">Daily Travel & Site Tracking</span>
							</p>
						</div>
					</div>

					<!-- Header Actions -->
					<div class="flex items-center space-x-1.5 flex-shrink-0">
						<!-- Supervisor Team Button (Visible if supervisor) -->
						<button
							v-if="employee?.is_supervisor"
							@click="router.push('/eem/team')"
							class="p-2 rounded-2xl text-teal-700 bg-teal-50 hover:bg-teal-100 active:scale-95 transition cursor-pointer relative"
							title="View Team Trips (Supervisor)"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
							</svg>
						</button>

						<!-- History Button -->
						<button
							@click="openHistoryModal"
							class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
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
							class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
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
			<main class="flex-1 w-full px-4 pt-16 sm:pt-16 pb-4 space-y-4">
				<!-- Loading State -->
				<div v-if="todayEemResource.loading && !eemDoc && !tripStatus" class="p-8 text-center bg-white rounded-3xl shadow-sm border border-slate-100 my-6">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent mb-3"></div>
					<h3 class="text-sm font-bold text-slate-900">Loading Trip Details...</h3>
					<p class="text-xs text-slate-500 mt-0.5">Fetching today's expense manager status</p>
				</div>

				<div v-else class="space-y-4">
					<!-- Date & Trip Status Hero Banner (Bright Turquoise Theme #40E0D0) -->
					<div class="relative overflow-hidden rounded-3xl bg-gradient-to-tr from-teal-600 via-teal-500 to-teal-400 text-white p-5 shadow-lg shadow-teal-600/20">
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
									class="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-100 space-y-2 text-xs relative"
								>
									<div class="flex items-start justify-between">
										<div class="flex items-center space-x-2 min-w-0">
											<span class="w-5 h-5 rounded-full bg-teal-100 text-teal-800 font-bold text-[10px] flex items-center justify-center shrink-0">
												{{ idx + 1 }}
											</span>
											<div class="min-w-0">
												<h4 class="font-bold text-slate-900 truncate max-w-[180px]">
													{{ visit.customer || visit.site || 'Site Location' }}
												</h4>
												<div class="flex items-center gap-1.5 mt-0.5">
													<span
														v-if="visit.category"
														class="px-1.5 py-0.2 rounded-md bg-teal-50 text-teal-800 font-bold text-[9px] border border-teal-200"
													>
														{{ visit.category }}
													</span>
													<span class="text-[10px] text-slate-500 truncate max-w-[160px]">{{ visit.site || visit.location_name }}</span>
												</div>
											</div>
										</div>
										<div class="text-right shrink-0">
											<span class="text-[10px] text-slate-500 font-mono block">{{ formatLogTime(visit.checkin_time) }}</span>
											<span v-if="visit.actual_distance" class="text-teal-700 font-bold font-mono text-[10px] bg-teal-50 px-1.5 py-0.2 rounded border border-teal-100 inline-block mt-0.5">
												+{{ visit.actual_distance }} km
											</span>
										</div>
									</div>

									<!-- Contact & Address Details -->
									<div v-if="visit.contact_number || visit.address" class="pl-7 space-y-1 text-[11px] text-slate-600">
										<div v-if="visit.contact_number" class="flex items-center space-x-1.5 font-mono text-[10px] text-slate-700">
											<svg class="w-3 h-3 text-teal-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
											</svg>
											<a :href="'tel:' + visit.contact_number" class="text-teal-700 hover:underline font-bold">{{ visit.contact_number }}</a>
										</div>
										<div v-if="visit.address" class="flex items-start space-x-1.5 text-[10px] text-slate-500">
											<svg class="w-3 h-3 text-slate-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
											</svg>
											<span class="truncate">{{ visit.address }}</span>
										</div>
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
					<!-- Customer Selection (Searchable) -->
					<div>
						<div class="flex items-center justify-between mb-1">
							<label class="block text-xs font-bold text-slate-700">Customer / Client</label>
							<div class="flex items-center space-x-1.5 text-[10px]">
								<span
									v-if="employee?.is_sales_person"
									class="px-1.5 py-0.2 rounded font-semibold text-[9px]"
									:class="employee?.view_all_customers ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-teal-50 text-teal-700 border border-teal-200'"
								>
									{{ employee?.view_all_customers ? 'All Customers' : 'My Customers' }}
								</span>
								<span class="font-medium flex items-center gap-1" :class="locationCoords?.latitude ? 'text-emerald-700' : 'text-slate-400'">
									<span v-if="locationCoords?.latitude" class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
									{{ locationCoords?.latitude ? 'Nearby' : 'Top 20' }}
								</span>
							</div>
						</div>

						<!-- Selected Customer Card -->
						<div
							v-if="siteVisitForm.customer && !isCustomerSearchOpen"
							class="p-2.5 bg-teal-50/70 border border-teal-200/90 rounded-2xl flex items-center justify-between transition-all shadow-xs"
						>
							<div class="flex items-center space-x-2.5 min-w-0">
								<div class="w-8 h-8 rounded-xl bg-teal-500 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
									</svg>
								</div>
								<div class="min-w-0 truncate">
									<div class="flex items-center space-x-1.5">
										<p class="text-xs font-bold text-slate-900 truncate">
											{{ selectedCustomerObj?.customer_name || siteVisitForm.customer }}
										</p>
										<span
											v-if="selectedCustomerObj?.distance_km !== undefined && selectedCustomerObj?.distance_km !== null"
											class="px-1.5 py-0.2 rounded-md bg-emerald-100 text-emerald-800 font-bold text-[9px] font-mono flex-shrink-0 border border-emerald-300/80"
										>
											📍 {{ formatDistance(selectedCustomerObj.distance_km) }}
										</span>
									</div>
									<p class="text-[10px] text-teal-700 font-medium truncate mt-0.5">
										<span class="font-mono">{{ selectedCustomerObj?.name || siteVisitForm.customer }}</span>
										<span v-if="selectedCustomerObj?.territory"> • {{ selectedCustomerObj.territory }}</span>
										<span v-else-if="selectedCustomerObj?.customer_group"> • {{ selectedCustomerObj.customer_group }}</span>
									</p>
								</div>
							</div>
							<div class="flex items-center space-x-1.5 flex-shrink-0 ml-2">
								<button
									type="button"
									@click="isCustomerSearchOpen = true"
									class="px-2.5 py-1 text-[11px] font-semibold text-teal-700 bg-white border border-teal-200 rounded-xl hover:bg-teal-50 active:scale-95 transition-all shadow-xs"
								>
									Change
								</button>
								<button
									type="button"
									@click="clearCustomer"
									class="p-1 text-slate-400 hover:text-rose-500 rounded-lg transition-colors"
									title="Remove customer"
								>
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
									</svg>
								</button>
							</div>
						</div>

						<!-- Searchable Input & Dropdown -->
						<div v-else class="space-y-1.5">
							<!-- Locating GPS indicator if resolving location for modal -->
							<div v-if="isLocatingForModal" class="p-2 rounded-xl bg-teal-50 border border-teal-200/70 flex items-center space-x-2 text-[11px] text-teal-800 animate-pulse">
								<svg class="w-3.5 h-3.5 animate-spin text-teal-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								<span>Acquiring GPS location to sort nearby customers...</span>
							</div>

							<div class="relative">
								<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
									<svg v-if="!customersResource.loading" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
									</svg>
									<svg v-else class="w-4 h-4 animate-spin text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
								</div>
								<input
									type="text"
									v-model="customerSearchQuery"
									@input="onCustomerSearchInput"
									@focus="isCustomerSearchOpen = true"
									placeholder="Search customer name, code, territory, phone..."
									class="w-full pl-9 pr-8 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 font-medium placeholder:text-slate-400 shadow-xs"
								/>
								<button
									v-if="customerSearchQuery"
									type="button"
									@click="customerSearchQuery = ''; onCustomerSearchInput()"
									class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
								>
									<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
									</svg>
								</button>
							</div>

							<!-- Search Results List -->
							<div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden animate-fadeIn">
								<div class="px-3 py-1.5 bg-slate-50 border-b border-slate-100 flex items-center justify-between text-[10px] text-slate-500 font-medium">
									<div class="flex items-center space-x-1.5 min-w-0 truncate">
										<span v-if="locationCoords?.latitude" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse flex-shrink-0"></span>
										<span class="truncate">
											<template v-if="customerSearchQuery">
												{{ filteredCustomersList.length }} result{{ filteredCustomersList.length === 1 ? '' : 's' }}
												for "{{ customerSearchQuery }}"
												<span v-if="locationCoords?.latitude" class="text-teal-700 font-semibold">(nearest first)</span>
											</template>
											<template v-else-if="locationCoords?.latitude">
												Nearest {{ filteredCustomersList.length }} {{ employee?.is_sales_person && !employee?.view_all_customers ? 'assigned' : '' }} customers
											</template>
											<template v-else>
												Showing {{ filteredCustomersList.length }} {{ employee?.is_sales_person && !employee?.view_all_customers ? 'assigned' : '' }} customers
											</template>
										</span>
									</div>
									<button
										v-if="siteVisitForm.customer"
										type="button"
										@click="isCustomerSearchOpen = false"
										class="text-teal-600 hover:underline font-bold ml-2 flex-shrink-0"
									>
										Cancel
									</button>
								</div>
								<div class="max-h-48 overflow-y-auto divide-y divide-slate-100 overscroll-contain">
									<!-- Option to proceed without customer -->
									<button
										type="button"
										@click="clearCustomer(); isCustomerSearchOpen = false"
										class="w-full px-3 py-2 text-left flex items-center justify-between hover:bg-slate-50 text-[11px] text-slate-600 group transition-colors"
									>
										<div class="flex items-center space-x-2">
											<span class="w-5 h-5 rounded-lg bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-teal-50 group-hover:text-teal-600 font-mono text-[10px]">
												✕
											</span>
											<span class="font-medium italic">No Customer (Custom Location Only)</span>
										</div>
										<span class="text-[9px] text-slate-400">Skip</span>
									</button>

									<!-- Customer Items -->
									<button
										v-for="c in filteredCustomersList"
										:key="c.name"
										type="button"
										@click="selectCustomer(c)"
										:class="[
											'w-full px-3 py-2.5 text-left flex items-center justify-between transition-colors text-xs',
											siteVisitForm.customer === c.name ? 'bg-teal-50/80 text-teal-900 font-bold' : 'hover:bg-slate-50 text-slate-800'
										]"
									>
										<div class="min-w-0 pr-2">
											<div class="flex items-center space-x-1.5">
												<p class="truncate font-semibold text-slate-900 leading-tight">
													{{ c.customer_name || c.name }}
												</p>
												<!-- Distance Badge -->
												<span
													v-if="c.distance_km !== null && c.distance_km !== undefined"
													class="flex-shrink-0 px-1.5 py-0.2 rounded-md text-[9px] font-bold font-mono"
													:class="Number(c.distance_km) <= 5 ? 'bg-emerald-100 text-emerald-800 border border-emerald-300/80' : 'bg-slate-100 text-slate-600 border border-slate-200'"
												>
													📍 {{ formatDistance(c.distance_km) }}
												</span>
											</div>
											<div class="flex items-center space-x-1.5 text-[10px] text-slate-400 mt-0.5 truncate">
												<span class="font-mono bg-slate-100 text-slate-600 px-1 py-0.2 rounded text-[9px]">{{ c.name }}</span>
												<span v-if="c.territory">• {{ c.territory }}</span>
												<span v-else-if="c.customer_group">• {{ c.customer_group }}</span>
												<span v-if="c.mobile_no">• 📞 {{ c.mobile_no }}</span>
											</div>
										</div>
										<svg
											v-if="siteVisitForm.customer === c.name"
											class="w-4 h-4 text-teal-600 flex-shrink-0"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
										>
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
										</svg>
									</button>

									<!-- Empty State / Use as Custom Site -->
									<div v-if="filteredCustomersList.length === 0" class="p-3 text-center">
										<p class="text-[11px] text-slate-500 mb-1.5">No customer found matching "{{ customerSearchQuery }}"</p>
										<button
											type="button"
											@click="useQueryAsCustomSite"
											class="px-2.5 py-1 text-[10px] font-bold text-teal-700 bg-teal-50 border border-teal-200 rounded-xl hover:bg-teal-100 active:scale-95 transition-all"
										>
											Use "{{ customerSearchQuery }}" as Site Location
										</button>
									</div>
								</div>
							</div>
						</div>
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

					<!-- Category (Chips & Input) -->
					<div>
						<div class="flex items-center justify-between mb-1.5">
							<label class="block text-xs font-bold text-slate-700">Visit Category</label>
							<span class="text-[10px] text-teal-700 font-semibold">{{ siteVisitForm.category || 'Select' }}</span>
						</div>
						<div class="flex flex-wrap gap-1.5 mb-2">
							<button
								type="button"
								v-for="cat in siteVisitCategories"
								:key="cat"
								@click="siteVisitForm.category = cat"
								class="px-2.5 py-1 rounded-xl text-[11px] font-semibold transition-all cursor-pointer"
								:class="siteVisitForm.category === cat ? 'bg-teal-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
							>
								{{ cat }}
							</button>
						</div>
						<input
							type="text"
							v-model="siteVisitForm.category"
							placeholder="Or type custom category..."
							class="w-full px-3.5 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 text-slate-900"
						/>
					</div>

					<!-- Contact Number -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Contact Number</label>
						<div class="relative">
							<div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
								<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
								</svg>
							</div>
							<input
								type="tel"
								v-model="siteVisitForm.contact_number"
								placeholder="e.g. +91 98765 43210"
								class="w-full pl-9 pr-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 font-mono"
							/>
						</div>
					</div>

					<!-- Address / Location Details -->
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1">Address / Location Details</label>
						<div class="relative">
							<div class="absolute top-2.5 left-3 pointer-events-none text-slate-400">
								<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
								</svg>
							</div>
							<textarea
								v-model="siteVisitForm.address"
								rows="2"
								placeholder="Door / Building No, Street, Landmark, Area..."
								class="w-full pl-9 pr-3.5 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900"
							></textarea>
						</div>
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

		<!-- GPS Location Acquiring Radar Overlay -->
		<div
			v-if="isAcquiringGps"
			class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 transition-all duration-300"
		>
			<div class="bg-white rounded-3xl p-6 shadow-2xl max-w-xs w-full text-center space-y-4 border border-teal-100">
				<!-- Pulsing Radar Animation -->
				<div class="relative w-20 h-20 mx-auto flex items-center justify-center">
					<div class="absolute inset-0 rounded-full bg-teal-500/20 animate-ping"></div>
					<div class="absolute inset-2 rounded-full bg-teal-500/30 animate-pulse"></div>
					<div class="relative w-12 h-12 rounded-full bg-gradient-to-tr from-teal-600 to-emerald-500 flex items-center justify-center text-white shadow-lg shadow-teal-600/30">
						<svg class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					</div>
				</div>

				<div class="space-y-1">
					<h3 class="text-sm font-bold text-slate-900">
						{{ gpsLoadingTitle || 'Acquiring GPS Location...' }}
					</h3>
					<p class="text-[11px] text-slate-500 leading-relaxed">
						{{ gpsLoadingSubtitle || 'Locking high-accuracy satellite coordinates. Please hold on for a moment...' }}
					</p>
				</div>

				<div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
					<div class="bg-teal-600 h-1.5 rounded-full w-2/3 animate-[pulse_1s_ease-in-out_infinite]"></div>
				</div>
			</div>
		</div>

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
import { ref, computed, watch, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter } from "vue-router"
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
import { toast } from "@/utils/toast"

const route = useRoute()
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
const isAcquiringGps = ref(false)
const gpsLoadingTitle = ref("Acquiring GPS Location...")
const gpsLoadingSubtitle = ref("Locking high-accuracy satellite coordinates. Please hold on...")
const isLocatingForModal = ref(false)
const locationModalContext = ref("start") // 'start' | 'site' | 'end'
const pendingPrefillCustomer = ref(null)

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

const siteVisitCategories = [
	"Client Meeting",
	"Site Inspection",
	"Payment Follow-up",
	"Product Demo",
	"Service / Maintenance",
	"Delivery / Pick-up",
	"Other",
]

const siteVisitForm = ref({
	customer: "",
	site: "",
	category: "Client Meeting",
	contact_number: "",
	address: "",
	actual_distance: "",
	remarks: "",
})

// Customer Search & Filtering State
const customerSearchQuery = ref("")
const isCustomerSearchOpen = ref(false)

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
const employee = computed(() => employeeResource.data)
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

const selectedCustomerDetails = ref(null)

function formatDistance(dist) {
	if (dist === null || dist === undefined || isNaN(dist)) return null
	const num = Number(dist)
	if (num < 1) {
		return `${Math.round(num * 1000)} m`
	}
	return `${num.toFixed(1)} km`
}

function fetchCustomersList({ search_term = "", limit = 20 } = {}) {
	const params = { limit }
	if (search_term && search_term.trim()) {
		params.search_term = search_term.trim()
	}
	if (locationCoords.value && locationCoords.value.latitude && locationCoords.value.longitude) {
		params.latitude = locationCoords.value.latitude
		params.longitude = locationCoords.value.longitude
	}
	customersResource.fetch(params)
}

const selectedCustomerObj = computed(() => {
	if (!siteVisitForm.value.customer) return null
	if (selectedCustomerDetails.value && selectedCustomerDetails.value.name === siteVisitForm.value.customer) {
		return selectedCustomerDetails.value
	}
	return customersList.value.find((c) => c.name === siteVisitForm.value.customer) || {
		name: siteVisitForm.value.customer,
		customer_name: siteVisitForm.value.customer,
	}
})

let searchDebounceTimer = null
function onCustomerSearchInput() {
	isCustomerSearchOpen.value = true
	const q = customerSearchQuery.value.trim()
	if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
	searchDebounceTimer = setTimeout(() => {
		fetchCustomersList({ search_term: q, limit: 20 })
	}, 250)
}

const filteredCustomersList = computed(() => {
	const list = customersList.value || []
	const q = customerSearchQuery.value.trim().toLowerCase()
	if (!q) return list
	return list.filter((c) => {
		const name = (c.customer_name || "").toLowerCase()
		const id = (c.name || "").toLowerCase()
		const territory = (c.territory || "").toLowerCase()
		const group = (c.customer_group || "").toLowerCase()
		const phone = (c.mobile_no || "").toLowerCase()
		return (
			name.includes(q) ||
			id.includes(q) ||
			territory.includes(q) ||
			group.includes(q) ||
			phone.includes(q)
		)
	})
})

function selectCustomer(c) {
	siteVisitForm.value.customer = c.name
	selectedCustomerDetails.value = c
	if (!siteVisitForm.value.site && c.customer_name) {
		siteVisitForm.value.site = c.customer_name
	}
	if (c.mobile_no) {
		siteVisitForm.value.contact_number = c.mobile_no
	}
	if (c.address_text || c.primary_address || c.territory) {
		siteVisitForm.value.address = c.address_text || c.primary_address || c.territory || ""
	}
	if ((!siteVisitForm.value.latitude || !siteVisitForm.value.longitude) && c.latitude && c.longitude && c.latitude != 0) {
		siteVisitForm.value.latitude = c.latitude
		siteVisitForm.value.longitude = c.longitude
	}
	isCustomerSearchOpen.value = false
	customerSearchQuery.value = ""
}

function clearCustomer() {
	siteVisitForm.value.customer = ""
	selectedCustomerDetails.value = null
	customerSearchQuery.value = ""
	isCustomerSearchOpen.value = true
	fetchCustomersList({ search_term: "", limit: 20 })
}

function useQueryAsCustomSite() {
	siteVisitForm.value.customer = ""
	if (customerSearchQuery.value) {
		siteVisitForm.value.site = customerSearchQuery.value.trim()
	}
	isCustomerSearchOpen.value = false
	customerSearchQuery.value = ""
}

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
	isAcquiringGps.value = true
	gpsLoadingTitle.value = "Connecting to GPS Satellites..."
	gpsLoadingSubtitle.value = "Calibrating real-time coordinates from your device..."

	try {
		const coords = await getCurrentLocation()
		if (coords && (coords.latitude || coords.longitude)) {
			showLocationModal.value = false
			toast.success("GPS location acquired successfully!", "Location Ready")
		} else {
			toast.warning(
				"GPS location could not be acquired. Please verify that Location / GPS is turned ON and location permission is granted in your browser settings.",
				"GPS Location Required"
			)
		}
	} finally {
		isAcquiringLocation.value = false
		isAcquiringGps.value = false
	}
}

function refreshData() {
	todayEemResource.fetch()
	checkinStatusResource.fetch()
	customersResource.fetch()
	expenseTypesResource.fetch()
}

function openHistoryModal() {
	router.push("/eem/history")
}

async function openSiteVisitModal(prefillData = null) {
	siteVisitForm.value = {
		customer: prefillData?.customer || "",
		site: prefillData?.site || prefillData?.customer_name || "",
		latitude: prefillData?.latitude || "",
		longitude: prefillData?.longitude || "",
		category: prefillData?.category || "Client Meeting",
		contact_number: prefillData?.contact_number || prefillData?.mobile_no || "",
		address: prefillData?.address || prefillData?.address_text || "",
		actual_distance: "",
		remarks: prefillData?.remarks || "",
	}
	customerSearchQuery.value = ""
	if (prefillData?.customer) {
		selectedCustomerDetails.value = {
			name: prefillData.customer,
			customer_name: prefillData.customer_name || prefillData.site || prefillData.customer,
			latitude: prefillData.latitude,
			longitude: prefillData.longitude,
			mobile_no: prefillData.contact_number || prefillData.mobile_no,
			address_text: prefillData.address || prefillData.address_text,
		}
		isCustomerSearchOpen.value = false
	} else {
		selectedCustomerDetails.value = null
		isCustomerSearchOpen.value = false
	}
	showSiteVisitModal.value = true

	// If locationCoords already available, fetch immediately
	if (locationCoords.value && locationCoords.value.latitude) {
		fetchCustomersList({ search_term: "", limit: 20 })
	} else {
		fetchCustomersList({ search_term: "", limit: 20 })
		isLocatingForModal.value = true
		getCurrentLocation().then((coords) => {
			if (coords && coords.latitude) {
				fetchCustomersList({ search_term: customerSearchQuery.value, limit: 20 })
			}
		}).finally(() => {
			isLocatingForModal.value = false
		})
	}
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
		toast.warning("Please select a vehicle type (2-Wheeler, 4-Wheeler, or Other) before starting your trip.", "Vehicle Required")
		return
	}
	if (!startForm.value.start_odometerkm && startForm.value.start_odometerkm !== 0) {
		toast.warning("Please enter the starting odometer reading in KM.", "Odometer Required")
		return
	}

	isSubmittingStart.value = true
	isAcquiringGps.value = true
	gpsLoadingTitle.value = "Acquiring GPS to Start Trip..."
	gpsLoadingSubtitle.value = "Locking your starting origin coordinates..."

	try {
		const coords = await getCurrentLocation()
		if (!coords || (!coords.latitude && !coords.longitude)) {
			locationModalContext.value = "start"
			showLocationModal.value = true
			return
		}

		await startTripResource.submit({
			vehicle_type: startForm.value.vehicle_type,
			start_odometerkm: Number(startForm.value.start_odometerkm),
			start_lat: coords.latitude,
			start_long: coords.longitude,
		})

		toast.success("Today's Travel Day started! Drive safely.", "Trip Started")
		await todayEemResource.fetch()

		if (pendingPrefillCustomer.value) {
			const prefill = { ...pendingPrefillCustomer.value }
			pendingPrefillCustomer.value = null
			openSiteVisitModal(prefill)
			toast.info(`Recording site visit for customer "${prefill.customer_name || prefill.customer}".`, "Customer Ready")
		}
	} catch (err) {
		console.error("Error starting trip:", err)
		toast.error(err.messages?.[0] || err.message || "Failed to start trip.", "Trip Error")
	} finally {
		isAcquiringGps.value = false
		isSubmittingStart.value = false
	}
}

async function submitSiteVisit() {
	if (!siteVisitForm.value.customer && !siteVisitForm.value.site) {
		toast.warning("Please select a customer or specify a site branch location.", "Location Required")
		return
	}

	isSubmittingSiteVisit.value = true
	isAcquiringGps.value = true
	gpsLoadingTitle.value = "Acquiring GPS for Site Visit..."
	gpsLoadingSubtitle.value = "Locking satellite coordinates for this site location..."

	try {
		const coords = await getCurrentLocation()
		if (!coords || (!coords.latitude && !coords.longitude)) {
			locationModalContext.value = "site"
			showLocationModal.value = true
			return
		}

		await addEemSiteVisitResource.submit({
			customer: siteVisitForm.value.customer,
			site: siteVisitForm.value.site,
			category: siteVisitForm.value.category,
			contact_number: siteVisitForm.value.contact_number,
			address: siteVisitForm.value.address,
			remarks: siteVisitForm.value.remarks,
			actual_distance: Number(siteVisitForm.value.actual_distance) || 0,
			latitude: coords.latitude,
			longitude: coords.longitude,
		})

		showSiteVisitModal.value = false
		toast.success("Site visit recorded successfully!", "Visit Logged")
		await todayEemResource.fetch()
	} catch (err) {
		console.error("Error adding site visit:", err)
		toast.error(err.messages?.[0] || err.message || "Failed to log site visit.", "Visit Error")
	} finally {
		isAcquiringGps.value = false
		isSubmittingSiteVisit.value = false
	}
}

async function submitExpense() {
	if (!expenseForm.value.expense_type) {
		toast.warning("Please select an expense category (Food, Fuel, Toll, Parking...).", "Category Required")
		return
	}
	if (!expenseForm.value.amount || Number(expenseForm.value.amount) <= 0) {
		toast.warning("Please enter a valid expense amount greater than 0.", "Invalid Amount")
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
		toast.success("Expense logged successfully!", "Expense Added")
		await todayEemResource.fetch()
	} catch (err) {
		console.error("Error adding expense:", err)
		toast.error(err.messages?.[0] || err.message || "Failed to add expense.", "Expense Error")
	} finally {
		isSubmittingExpense.value = false
	}
}

async function submitEndTrip() {
	const endOdo = Number(endForm.value.end_odometerkm)
	const startOdo = Number(eemDoc.value?.start_odometerkm) || 0

	if (!endForm.value.end_odometerkm && endForm.value.end_odometerkm !== 0) {
		toast.warning("Please enter the end odometer reading in KM.", "End Odometer Required")
		return
	}

	if (endOdo < startOdo) {
		toast.warning(`End odometer (${endOdo} KM) cannot be less than starting reading (${startOdo} KM).`, "Invalid Reading")
		return
	}

	isSubmittingEnd.value = true
	isAcquiringGps.value = true
	gpsLoadingTitle.value = "Acquiring GPS to End Trip..."
	gpsLoadingSubtitle.value = "Locking your destination coordinates..."

	try {
		const coords = await getCurrentLocation()
		if (!coords || (!coords.latitude && !coords.longitude)) {
			locationModalContext.value = "end"
			showLocationModal.value = true
			return
		}

		await endTripResource.submit({
			end_odometerkm: endOdo,
			actual_end_distance: Number(endForm.value.actual_end_distance) || 0,
			end_narration: endForm.value.end_narration,
			submit_doc: endForm.value.submit_doc ? 1 : 0,
			end_lat: coords.latitude,
			end_long: coords.longitude,
		})

		showEndTripModal.value = false
		toast.success("Travel Day summary submitted successfully!", "Trip Completed")
		await todayEemResource.fetch()
	} catch (err) {
		console.error("Error ending trip:", err)
		toast.error(err.messages?.[0] || err.message || "Failed to end trip.", "Trip Error")
	} finally {
		isAcquiringGps.value = false
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

async function handlePrefillFromQuery() {
	if (!route.query.prefillCustomer) return

	const customerCode = String(route.query.prefillCustomer)
	const customerTitle = String(route.query.prefillCustomerName || customerCode)
	const preLat = route.query.prefillLat ? Number(route.query.prefillLat) : null
	const preLng = route.query.prefillLng ? Number(route.query.prefillLng) : null
	const preMobile = route.query.prefillMobile ? String(route.query.prefillMobile) : ""
	const preAddress = route.query.prefillAddress ? String(route.query.prefillAddress) : ""

	const prefillData = {
		customer: customerCode,
		customer_name: customerTitle,
		site: customerTitle,
		latitude: preLat,
		longitude: preLng,
		contact_number: preMobile,
		address: preAddress,
		category: "Client Meeting",
	}

	if (!todayEemResource.data && !todayEemResource.loading) {
		await todayEemResource.fetch()
	}

	const tripStatusVal = tripStatus.value || todayEemResource.data?.trip_status

	if (tripStatusVal === "IN_PROGRESS") {
		pendingPrefillCustomer.value = null
		activeTab.value = "visits"
		openSiteVisitModal(prefillData)
		toast.info(`Recording site visit for customer "${customerTitle}".`, "Customer Selected")
	} else if (tripStatusVal === "NOT_STARTED") {
		pendingPrefillCustomer.value = prefillData
		toast.warning(`Please start your Travel Day first to log visit for "${customerTitle}".`, "Start Trip First")
	} else {
		toast.warning(`Today's travel is completed. You cannot log new visits for "${customerTitle}".`, "Trip Ended")
	}
}

watch(
	() => [route.query.prefillCustomer, route.query.t],
	() => {
		if (route.query.prefillCustomer) {
			handlePrefillFromQuery()
		}
	},
	{ immediate: false }
)

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
	await todayEemResource.fetch()
	checkinStatusResource.fetch()

	// If navigated from Customers page with a customer pre-selected
	if (route.query.prefillCustomer) {
		await handlePrefillFromQuery()
	}
})

onUnmounted(() => {
	if (clockTimer) clearInterval(clockTimer)
})
</script>
