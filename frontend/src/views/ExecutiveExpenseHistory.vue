<template>
	<div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-start items-center p-0 sm:p-4 font-sans selection:bg-teal-500 selection:text-white relative overflow-x-hidden pb-24">
		<!-- Background ambient soft gradients for desktop container -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-emerald-200/20 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full sm:max-w-md bg-[#f8fafc] min-h-screen sm:min-h-[720px] sm:rounded-3xl sm:shadow-2xl sm:border sm:border-slate-200/80 flex flex-col justify-between relative z-10 overflow-hidden pb-6">
			
			<!-- Mobile Top Header (Sticky at top, natural flow, no content overlap) -->
			<header class="sticky top-0 z-30 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 shadow-2xs px-4 pt-3 pb-3 sm:px-5">
				<div class="max-w-md mx-auto space-y-2.5">
					<div class="flex items-center justify-between">
						<!-- Back Navigation & Title -->
						<div class="flex items-center space-x-2.5">
							<button
								@click="goBack"
								class="p-2 -ml-1 rounded-2xl text-slate-600 hover:text-teal-700 hover:bg-teal-50/80 active:scale-95 transition cursor-pointer"
								title="Back"
							>
								<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
								</svg>
							</button>
							<div>
								<h1 class="text-sm font-bold text-slate-900 leading-tight flex items-center gap-1.5">
									<span>EEM Travel History</span>
									<span class="w-1.5 h-1.5 rounded-full bg-teal-500 inline-block"></span>
								</h1>
								<p class="text-[10px] font-medium text-slate-500 leading-none flex items-center gap-1 mt-0.5">
									<span v-if="employee?.company_name" class="font-semibold text-teal-700">{{ employee.company_name }} •</span>
									<span>Past Field Trips & Expenses</span>
								</p>
							</div>
						</div>

						<!-- Header Actions -->
						<div class="flex items-center space-x-1.5">
							<!-- Toggle Filter Panel Button -->
							<button
								@click="isFilterDrawerOpen = !isFilterDrawerOpen"
								class="px-2.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition active:scale-95 cursor-pointer"
								:class="hasActiveFilters || isFilterDrawerOpen ? 'bg-teal-50 text-teal-700 border border-teal-200 shadow-2xs ring-2 ring-teal-500/20' : 'bg-slate-100 text-slate-600 hover:bg-slate-200/80'"
								title="Toggle Advanced Filters"
							>
								<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
								</svg>
								<span class="text-[11px] font-medium">Filters</span>
								<span
									v-if="hasActiveFilters"
									class="w-1.5 h-1.5 rounded-full bg-teal-600"
								></span>
							</button>

							<!-- Refresh Button -->
							<button
								@click="fetchHistory"
								:disabled="isLoadingHistory"
								class="p-2 rounded-xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
								title="Refresh trip history"
							>
								<svg
									class="w-4 h-4"
									:class="{ 'animate-spin text-teal-600': isLoadingHistory }"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Modern Segmented Status Tabs Bar -->
					<div class="grid grid-cols-4 gap-1 p-1 bg-slate-100/90 rounded-2xl border border-slate-200/70">
						<button
							v-for="filter in statusFilters"
							:key="filter.value"
							@click="selectedStatus = filter.value"
							:class="[
								'py-1.5 px-1 rounded-xl text-[11px] font-bold transition-all flex items-center justify-center gap-1 cursor-pointer truncate',
								selectedStatus === filter.value
									? 'bg-white text-teal-800 shadow-xs border border-slate-200/60'
									: 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
							]"
						>
							<span class="truncate">{{ filter.label }}</span>
							<span
								v-if="filter.count !== undefined"
								:class="[
									'text-[9px] px-1.5 py-0.2 rounded-full font-mono font-bold shrink-0',
									selectedStatus === filter.value
										? 'bg-teal-100 text-teal-900'
										: 'bg-slate-200/80 text-slate-600'
								]"
							>
								{{ filter.count }}
							</span>
						</button>
					</div>

					<!-- Quick Filter Dropdowns Row: Period & Vehicle -->
					<div class="flex items-center gap-2">
						<!-- Date Preset Dropdown -->
						<div class="relative flex-1">
							<select
								:value="selectedDatePreset"
								@change="setDatePreset($event.target.value)"
								class="w-full pl-7 pr-6 py-1.5 bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-[11px] font-semibold text-slate-700 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition cursor-pointer appearance-none truncate"
							>
								<option value="all">📅 All Time</option>
								<option value="this_month">📅 This Month</option>
								<option value="last_month">📅 Last Month</option>
								<option value="last_3_months">📅 Last 3 Months</option>
								<option value="this_year">📅 This Year</option>
								<option value="custom">📅 Custom Range...</option>
							</select>
							<div class="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none text-slate-400">
								<span class="text-xs">📅</span>
							</div>
							<div class="absolute inset-y-0 right-0 pr-2 flex items-center pointer-events-none text-slate-400">
								<svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
								</svg>
							</div>
						</div>

						<!-- Vehicle Filter Dropdown -->
						<div class="relative flex-1">
							<select
								v-model="selectedVehicle"
								class="w-full pl-7 pr-6 py-1.5 bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-[11px] font-semibold text-slate-700 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 transition cursor-pointer appearance-none truncate"
							>
								<option value="all">🚗 All Vehicles</option>
								<option value="Two Wheeler">🛵 Two Wheeler</option>
								<option value="Four Wheeler">🚗 Four Wheeler</option>
							</select>
							<div class="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none text-slate-400">
								<span class="text-xs">🚗</span>
							</div>
							<div class="absolute inset-y-0 right-0 pr-2 flex items-center pointer-events-none text-slate-400">
								<svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
								</svg>
							</div>
						</div>
					</div>

					<!-- Expandable Filter / Refine Drawer -->
					<transition
						enter-active-class="transition duration-150 ease-out"
						enter-from-class="transform opacity-0 -translate-y-2"
						enter-to-class="transform opacity-100 translate-y-0"
						leave-active-class="transition duration-100 ease-in"
						leave-from-class="transform opacity-100 translate-y-0"
						leave-to-class="transform opacity-0 -translate-y-2"
					>
						<div
							v-if="isFilterDrawerOpen"
							class="p-3.5 bg-slate-50 rounded-2xl border border-slate-200/90 space-y-3 text-xs"
						>
							<!-- Filter Header with Reset -->
							<div class="flex items-center justify-between">
								<span class="font-bold text-slate-800 flex items-center gap-1.5">
									<svg class="w-3.5 h-3.5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
									</svg>
									<span>Advanced Filters</span>
								</span>
								<button
									v-if="hasActiveFilters"
									@click="resetAllFilters"
									class="text-[10px] text-teal-700 font-bold hover:underline cursor-pointer"
								>
									Reset All
								</button>
							</div>

							<!-- Custom Date Range -->
							<div class="grid grid-cols-2 gap-2">
								<div>
									<label class="text-[10px] font-bold text-slate-500 block mb-1">From Date</label>
									<input
										type="date"
										v-model="customFromDate"
										@change="selectedDatePreset = 'custom'"
										class="w-full px-2.5 py-1.5 bg-white rounded-xl border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
									/>
								</div>
								<div>
									<label class="text-[10px] font-bold text-slate-500 block mb-1">To Date</label>
									<input
										type="date"
										v-model="customToDate"
										@change="selectedDatePreset = 'custom'"
										class="w-full px-2.5 py-1.5 bg-white rounded-xl border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
									/>
								</div>
							</div>

							<!-- Specific Month & Sorting Filters -->
							<div class="grid grid-cols-2 gap-2">
								<div>
									<label class="text-[10px] font-bold text-slate-500 block mb-1">Specific Month</label>
									<select
										v-model="selectedMonth"
										class="w-full px-2.5 py-1.5 bg-white rounded-xl border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
									>
										<option value="all">All Months</option>
										<option v-for="m in availableMonths" :key="m.key" :value="m.key">
											{{ m.label }} ({{ m.count }})
										</option>
									</select>
								</div>

								<div>
									<label class="text-[10px] font-bold text-slate-500 block mb-1">Sort Order</label>
									<select
										v-model="selectedSort"
										class="w-full px-2.5 py-1.5 bg-white rounded-xl border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
									>
										<option value="date_desc">📅 Newest First</option>
										<option value="date_asc">📅 Oldest First</option>
										<option value="claim_desc">💰 Highest Claim</option>
										<option value="dist_desc">🛣️ Longest Distance</option>
									</select>
								</div>
							</div>

							<!-- View Layout Mode Switcher -->
							<div class="pt-1 flex items-center justify-between border-t border-slate-200/70">
								<span class="text-[11px] text-slate-600 font-medium">Group by Month:</span>
								<button
									@click="isGroupedByMonth = !isGroupedByMonth"
									class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition flex items-center gap-1 cursor-pointer"
									:class="isGroupedByMonth ? 'bg-teal-600 text-white' : 'bg-slate-200 text-slate-700'"
								>
									<span>{{ isGroupedByMonth ? 'Enabled' : 'Disabled' }}</span>
								</button>
							</div>
						</div>
					</transition>
				</div>
			</header>

			<!-- Main Scrollable Content -->
			<main class="flex-1 px-4 sm:px-5 pt-3.5 pb-4 space-y-4">
				
				<!-- Cumulative Stats Banner (Bright Turquoise Theme #40E0D0) -->
				<div class="bg-gradient-to-br from-teal-600 via-teal-500 to-teal-400 rounded-3xl p-4 text-white shadow-md shadow-teal-600/20 relative overflow-hidden">
					<div class="absolute -right-8 -bottom-8 w-32 h-32 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>
					<div class="relative z-10">
						<div class="flex items-center justify-between text-xs text-teal-200/80 mb-3">
							<div class="flex items-center space-x-1.5 font-medium">
								<svg class="w-3.5 h-3.5 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
								</svg>
								<span>Filtered Period Summary</span>
							</div>
							<span class="text-[11px] font-mono text-teal-300 font-bold">{{ filteredRecords.length }} {{ filteredRecords.length === 1 ? 'Trip' : 'Trips' }}</span>
						</div>

						<div class="grid grid-cols-3 gap-2 text-center">
							<div class="bg-white/10 rounded-2xl p-2.5 backdrop-blur-xs">
								<p class="text-[10px] text-teal-200/80 font-medium">Total Dist.</p>
								<p class="text-sm font-black font-mono mt-0.5 text-white">{{ statsTotalDistance.toFixed(1) }} <span class="text-[10px] font-normal text-teal-300">km</span></p>
							</div>
							<div class="bg-white/10 rounded-2xl p-2.5 backdrop-blur-xs">
								<p class="text-[10px] text-teal-200/80 font-medium">Total Claim</p>
								<p class="text-sm font-black font-mono mt-0.5 text-teal-300">₹{{ Math.round(statsTotalExpense).toLocaleString('en-IN') }}</p>
							</div>
							<div class="bg-white/10 rounded-2xl p-2.5 backdrop-blur-xs">
								<p class="text-[10px] text-teal-200/80 font-medium">Site Visits</p>
								<p class="text-sm font-black font-mono mt-0.5 text-white">{{ statsTotalSites }}</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Search Input -->
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
						</svg>
					</div>
					<input
						v-model="searchQuery"
						type="text"
						placeholder="Search by date, site, vehicle, or notes..."
						class="w-full pl-9 pr-8 py-2.5 bg-white rounded-2xl border border-slate-200/80 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition shadow-xs"
					/>
					<button
						v-if="searchQuery"
						@click="searchQuery = ''"
						class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
					>
						<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>

				<!-- Active Filter Chips (If Any Filter Active) -->
				<div v-if="hasActiveFilters" class="flex flex-wrap items-center gap-1.5 text-[10px]">
					<span class="text-slate-400 font-semibold">Active Filters:</span>
					<span
						v-if="selectedDatePreset !== 'all'"
						class="px-2 py-0.5 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 flex items-center gap-1 font-medium"
					>
						<span>Date: {{ selectedDatePresetLabel }}</span>
						<button @click="setDatePreset('all')" class="hover:text-teal-950 font-bold">&times;</button>
					</span>
					<span
						v-if="selectedMonth !== 'all'"
						class="px-2 py-0.5 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 flex items-center gap-1 font-medium"
					>
						<span>Month: {{ selectedMonthLabel }}</span>
						<button @click="selectedMonth = 'all'" class="hover:text-teal-950 font-bold">&times;</button>
					</span>
					<span
						v-if="selectedVehicle !== 'all'"
						class="px-2 py-0.5 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 flex items-center gap-1 font-medium"
					>
						<span>Vehicle: {{ selectedVehicle }}</span>
						<button @click="selectedVehicle = 'all'" class="hover:text-teal-950 font-bold">&times;</button>
					</span>
					<span
						v-if="selectedStatus !== 'all'"
						class="px-2 py-0.5 rounded-lg bg-teal-50 text-teal-800 border border-teal-200 flex items-center gap-1 font-medium"
					>
						<span>Status: {{ selectedStatus }}</span>
						<button @click="selectedStatus = 'all'" class="hover:text-teal-950 font-bold">&times;</button>
					</span>
					<button
						@click="resetAllFilters"
						class="text-[10px] text-rose-600 hover:text-rose-800 font-bold ml-1"
					>
						Clear all
					</button>
				</div>

				<!-- Loading State -->
				<div v-if="isLoadingHistory && rawHistoryRecords.length === 0" class="py-12 text-center space-y-3">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent"></div>
					<h3 class="text-sm font-bold text-slate-900">Loading Travel Records...</h3>
					<p class="text-xs text-slate-500">Fetching your field trip history</p>
				</div>

				<!-- Empty State -->
				<div
					v-else-if="filteredRecords.length === 0"
					class="py-12 bg-white rounded-3xl border border-dashed border-slate-200 text-center p-6 space-y-3"
				>
					<div class="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center mx-auto">
						<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
						</svg>
					</div>
					<h3 class="text-sm font-bold text-slate-800">No Trip Records Found</h3>
					<p class="text-xs text-slate-500 max-w-xs mx-auto">
						{{ hasActiveFilters || searchQuery ? 'No records match your selected filters.' : 'No executive expense manager records have been logged yet.' }}
					</p>
					<div class="pt-2 flex justify-center gap-2">
						<button
							v-if="hasActiveFilters || searchQuery"
							@click="resetAllFilters"
							class="px-3.5 py-2 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition"
						>
							Clear Filters
						</button>
						<button
							@click="goToEem"
							class="inline-flex items-center space-x-1.5 px-4 py-2 rounded-2xl bg-teal-600 text-white text-xs font-semibold shadow-xs hover:bg-teal-700 transition"
						>
							<span>Start Today's Travel</span>
						</button>
					</div>
				</div>

				<!-- GROUPED BY MONTH VIEW -->
				<div v-else-if="isGroupedByMonth" class="space-y-5">
					<div
						v-for="group in groupedRecords"
						:key="group.monthKey"
						class="space-y-3"
					>
						<!-- Month Group Header Card -->
						<div class="sticky top-[106px] z-20 bg-slate-100/95 backdrop-blur-md py-1.5 px-3 rounded-2xl border border-slate-200/80 flex items-center justify-between text-xs shadow-xs">
							<div class="flex items-center space-x-2">
								<span class="font-bold text-slate-900">{{ group.monthLabel }}</span>
								<span class="px-1.5 py-0.2 bg-teal-50 text-teal-800 font-bold rounded-md text-[10px] font-mono border border-teal-200">
									{{ group.records.length }} trips
								</span>
							</div>
							<div class="flex items-center space-x-2 text-[11px] font-mono">
								<span class="text-slate-600 font-semibold">{{ group.totalDistance.toFixed(1) }} km</span>
								<span class="text-slate-300">•</span>
								<span class="text-teal-700 font-bold">₹{{ Math.round(group.totalExpense).toLocaleString('en-IN') }}</span>
							</div>
						</div>

						<!-- List of Cards in this month -->
						<div class="space-y-3">
							<div
								v-for="rec in group.records"
								:key="rec.name"
								@click="viewTripDetail(rec)"
								:class="[
									'rounded-2xl p-4 transition-all active:scale-[0.99] cursor-pointer relative overflow-hidden',
									isTripInProgress(rec)
										? 'bg-gradient-to-br from-emerald-50/90 via-teal-50/40 to-white border-2 border-teal-500 shadow-md ring-4 ring-teal-500/10'
										: 'bg-white border border-slate-200/80 shadow-xs hover:border-teal-300 hover:shadow-sm'
								]"
							>
								<!-- Render Single Trip Card -->
								<div class="flex items-start justify-between">
									<div class="space-y-0.5">
										<div class="flex items-center space-x-2">
											<h4 class="text-sm font-bold text-slate-900">
												{{ formatDisplayDate(rec.date) }}
											</h4>
											<span
												v-if="isTripInProgress(rec)"
												class="px-2 py-0.5 text-[9px] font-black rounded-full bg-emerald-600 text-white uppercase tracking-wider shadow-xs"
											>
												Today • Active
											</span>
											<span
												v-else-if="isToday(rec.date)"
												class="px-1.5 py-0.5 text-[9px] font-bold rounded bg-slate-200 text-slate-700 uppercase tracking-wider"
											>
												Today
											</span>
										</div>
										<p class="text-[11px] font-mono text-slate-400">{{ rec.name }}</p>
									</div>

									<!-- Claim / Approval Status Badge -->
									<div class="flex flex-col items-end space-y-1">
										<span
											:class="[
												'px-2.5 py-1 rounded-full text-[10px] tracking-wide uppercase flex items-center font-bold',
												getStatusBadgeClass(rec)
											]"
										>
											<span
												v-if="isTripInProgress(rec)"
												class="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-ping mr-1.5 inline-block"
											></span>
											<span>{{ getStatusBadgeLabel(rec) }}</span>
										</span>
									</div>
								</div>

								<!-- Card Middle Row: Metrics Grid -->
								<div class="mt-3.5 grid grid-cols-3 gap-2 py-2.5 px-3 rounded-xl bg-slate-50 border border-slate-100/80 text-xs">
									<div>
										<span class="text-[10px] text-slate-500 font-medium block">Vehicle</span>
										<div class="flex items-center space-x-1 font-semibold text-slate-800 mt-0.5 truncate">
											<span>{{ rec.vehicle_type === 'Two Wheeler' ? '🛵' : '🚗' }}</span>
											<span class="truncate">{{ rec.vehicle_type || 'Vehicle' }}</span>
										</div>
									</div>

									<div class="text-center">
										<span class="text-[10px] text-slate-500 font-medium block">Distance</span>
										<span class="font-bold font-mono text-slate-900 mt-0.5 block">
											{{ (rec.total_distance || 0).toFixed(1) }} km
										</span>
									</div>

									<div class="text-right">
										<span class="text-[10px] text-slate-500 font-medium block">Total Claim</span>
										<span class="font-bold font-mono text-teal-700 mt-0.5 block">
											₹{{ Math.round(rec.total_expense || 0).toLocaleString('en-IN') }}
										</span>
									</div>
								</div>

								<!-- Card Bottom Row: Sites & Timings Breakdown -->
								<div class="mt-2.5 flex items-center justify-between text-[11px] text-slate-500">
									<div class="flex items-center space-x-2">
										<span class="inline-flex items-center space-x-1 font-medium text-slate-700">
											<svg class="w-3.5 h-3.5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
											</svg>
											<span>{{ rec.sites_count || 0 }} {{ rec.sites_count === 1 ? 'Site Visit' : 'Site Visits' }}</span>
										</span>

										<span v-if="rec.expenses_count" class="text-slate-300">•</span>

										<span v-if="rec.expenses_count" class="text-slate-600">
											{{ rec.expenses_count }} {{ rec.expenses_count === 1 ? 'expense' : 'expenses' }}
										</span>
									</div>

									<div class="flex items-center space-x-1 text-teal-600 font-semibold">
										<span>Details</span>
										<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
										</svg>
									</div>
								</div>

								<!-- Today In-Progress Direct Action Bar -->
								<div
									v-if="isTripInProgress(rec)"
									class="mt-3 pt-2.5 border-t border-teal-200/80 flex items-center justify-between"
								>
									<span class="text-[11px] font-bold text-teal-900">Trip is actively ongoing</span>
									<button
										@click.stop="goToEem"
										class="px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-[11px] font-bold shadow-xs transition flex items-center space-x-1"
									>
										<span>Manage Today's Trip</span>
										<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
										</svg>
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- FLAT LIST OF TRIP CARDS -->
				<div v-else class="space-y-3">
					<div
						v-for="rec in filteredRecords"
						:key="rec.name"
						@click="viewTripDetail(rec)"
						:class="[
							'rounded-2xl p-4 transition-all active:scale-[0.99] cursor-pointer relative overflow-hidden',
							isTripInProgress(rec)
								? 'bg-gradient-to-br from-emerald-50/90 via-teal-50/40 to-white border-2 border-teal-500 shadow-md ring-4 ring-teal-500/10'
								: 'bg-white border border-slate-200/80 shadow-xs hover:border-teal-300 hover:shadow-sm'
						]"
					>
						<!-- Card Top Row: Date & Status Badge -->
						<div class="flex items-start justify-between">
							<div class="space-y-0.5">
								<div class="flex items-center space-x-2">
									<h4 class="text-sm font-bold text-slate-900">
										{{ formatDisplayDate(rec.date) }}
									</h4>
									<span
										v-if="isTripInProgress(rec)"
										class="px-2 py-0.5 text-[9px] font-black rounded-full bg-emerald-600 text-white uppercase tracking-wider shadow-xs"
									>
										Today • Active
									</span>
									<span
										v-else-if="isToday(rec.date)"
										class="px-1.5 py-0.5 text-[9px] font-bold rounded bg-slate-200 text-slate-700 uppercase tracking-wider"
									>
										Today
									</span>
								</div>
								<p class="text-[11px] font-mono text-slate-400">{{ rec.name }}</p>
							</div>

							<!-- Claim / Approval Status Badge -->
							<div class="flex flex-col items-end space-y-1">
								<span
									:class="[
										'px-2.5 py-1 rounded-full text-[10px] tracking-wide uppercase flex items-center font-bold',
										getStatusBadgeClass(rec)
									]"
								>
									<span
										v-if="isTripInProgress(rec)"
										class="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-ping mr-1.5 inline-block"
									></span>
									<span>{{ getStatusBadgeLabel(rec) }}</span>
								</span>
							</div>
						</div>

						<!-- Card Middle Row: Metrics Grid -->
						<div class="mt-3.5 grid grid-cols-3 gap-2 py-2.5 px-3 rounded-xl bg-slate-50 border border-slate-100/80 text-xs">
							<div>
								<span class="text-[10px] text-slate-500 font-medium block">Vehicle</span>
								<div class="flex items-center space-x-1 font-semibold text-slate-800 mt-0.5 truncate">
									<span>{{ rec.vehicle_type === 'Two Wheeler' ? '🛵' : '🚗' }}</span>
									<span class="truncate">{{ rec.vehicle_type || 'Vehicle' }}</span>
								</div>
							</div>

							<div class="text-center">
								<span class="text-[10px] text-slate-500 font-medium block">Distance</span>
								<span class="font-bold font-mono text-slate-900 mt-0.5 block">
									{{ (rec.total_distance || 0).toFixed(1) }} km
								</span>
							</div>

							<div class="text-right">
								<span class="text-[10px] text-slate-500 font-medium block">Total Claim</span>
								<span class="font-bold font-mono text-teal-700 mt-0.5 block">
									₹{{ Math.round(rec.total_expense || 0).toLocaleString('en-IN') }}
								</span>
							</div>
						</div>

						<!-- Card Bottom Row: Sites & Timings Breakdown -->
						<div class="mt-2.5 flex items-center justify-between text-[11px] text-slate-500">
							<div class="flex items-center space-x-2">
								<span class="inline-flex items-center space-x-1 font-medium text-slate-700">
									<svg class="w-3.5 h-3.5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
									</svg>
									<span>{{ rec.sites_count || 0 }} {{ rec.sites_count === 1 ? 'Site Visit' : 'Site Visits' }}</span>
								</span>

								<span v-if="rec.expenses_count" class="text-slate-300">•</span>

								<span v-if="rec.expenses_count" class="text-slate-600">
									{{ rec.expenses_count }} {{ rec.expenses_count === 1 ? 'expense' : 'expenses' }}
								</span>
							</div>

							<div class="flex items-center space-x-1 text-teal-600 font-semibold">
								<span>Details</span>
								<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
								</svg>
							</div>
						</div>

						<!-- Today In-Progress Direct Action Bar -->
						<div
							v-if="isTripInProgress(rec)"
							class="mt-3 pt-2.5 border-t border-teal-200/80 flex items-center justify-between"
						>
							<span class="text-[11px] font-bold text-teal-900">Trip is actively ongoing</span>
							<button
								@click.stop="goToEem"
								class="px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-[11px] font-bold shadow-xs transition flex items-center space-x-1"
							>
								<span>Manage Today's Trip</span>
								<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
								</svg>
							</button>
						</div>
					</div>
				</div>

				<!-- View More Trips Button -->
				<div v-if="hasMore && !isLoadingHistory && filteredRecords.length > 0" class="pt-4 pb-2 text-center">
					<button
						@click="loadMoreHistory"
						:disabled="isLoadingMore"
						class="w-full py-3 px-4 text-xs font-bold text-teal-800 bg-white hover:bg-teal-50/80 active:bg-teal-100 border border-teal-200/80 rounded-2xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-xs hover:border-teal-300 cursor-pointer"
					>
						<svg v-if="isLoadingMore" class="w-4 h-4 animate-spin text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						<span>{{ isLoadingMore ? 'Loading older trips...' : `View More Trips (Showing ${rawHistoryRecords.length})` }}</span>
					</button>
				</div>
			</main>

			<!-- Quick Bottom Navigation Back to EEM -->
			<footer class="sticky bottom-0 z-20 bg-white/95 backdrop-blur-md border-t border-slate-200/80 px-4 py-3 flex items-center justify-between">
				<button
					@click="goBack"
					class="w-1/2 mr-2 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition flex items-center justify-center space-x-1.5"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
					</svg>
					<span>Dashboard</span>
				</button>

				<button
					@click="goToEem"
					class="w-1/2 ml-2 py-2.5 rounded-2xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition shadow-xs shadow-teal-600/20 flex items-center justify-center space-x-1.5"
				>
					<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
					</svg>
					<span>EEM Travel View</span>
				</button>
			</footer>

		</div>

		<!-- MODAL / DRAWER: DETAILED DAY VIEW -->
		<Dialog v-model="showDetailModal">
			<template #body-title>
				<div class="flex items-center justify-between w-full pr-6 text-left">
					<div class="space-y-0.5">
						<div class="flex items-center space-x-2">
							<h3 class="text-base font-bold text-slate-900 leading-tight">
								{{ currentDetailDoc ? formatDisplayDate(currentDetailDoc.date) : 'Trip Details' }}
							</h3>
							<span
								v-if="currentDetailDoc"
								:class="[
									'px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider',
									getStatusBadgeClass(currentDetailDoc)
								]"
							>
								{{ getStatusBadgeLabel(currentDetailDoc) }}
							</span>
						</div>
						<p class="text-xs font-mono text-slate-400">{{ currentDetailDoc?.name }}</p>
					</div>
				</div>
			</template>

			<template #body-content>
				<div class="space-y-4 max-h-[75vh] overflow-y-auto pr-1 no-scrollbar text-left mt-1">
					<div v-if="eemDetailResource.loading" class="py-12 text-center text-xs text-slate-500">
						<div class="inline-block animate-spin text-teal-600 mb-2">
							<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
						</div>
						<p>Loading complete day breakdown...</p>
					</div>

					<div v-else-if="currentDetailDoc" class="space-y-4 text-xs">
						
						<!-- Financial Breakdown Card -->
						<div class="bg-gradient-to-r from-teal-50 to-emerald-50 rounded-2xl p-3.5 border border-teal-100 space-y-2">
							<div class="flex items-center justify-between text-teal-900 font-bold">
								<span>Total Claim for the Day</span>
								<span class="text-sm font-mono font-black text-teal-800">₹{{ (currentDetailDoc.total_expense || 0).toLocaleString('en-IN') }}</span>
							</div>
							<div class="grid grid-cols-2 gap-2 text-[11px] pt-1 border-t border-teal-200/50">
								<div>
									<span class="text-slate-500">Travel Allowance:</span>
									<p class="font-bold text-slate-800 font-mono">₹{{ (currentDetailDoc.total_travel_expense || 0).toLocaleString('en-IN') }} ({{ currentDetailDoc.total_distance || 0 }} km)</p>
								</div>
								<div>
									<span class="text-slate-500">Other Expenses:</span>
									<p class="font-bold text-slate-800 font-mono">₹{{ (currentDetailDoc.total_other_expenses || 0).toLocaleString('en-IN') }}</p>
								</div>
							</div>
						</div>

						<!-- Linked Expense Claim status info if any -->
						<div
							v-if="linkedExpenseClaim"
							class="p-3 bg-amber-50/70 border border-amber-200/80 rounded-2xl space-y-1 text-[11px]"
						>
							<div class="flex items-center justify-between">
								<span class="font-bold text-amber-900">Linked Expense Claim:</span>
								<span class="font-mono font-bold text-amber-900">{{ linkedExpenseClaim.name }}</span>
							</div>
							<div class="flex items-center justify-between text-slate-600">
								<span>Claim Status:</span>
								<span class="font-semibold text-amber-800">{{ linkedExpenseClaim.status || linkedExpenseClaim.approval_status }}</span>
							</div>
						</div>

						<!-- Trip Odometer & Timing Section -->
						<div class="bg-white rounded-2xl p-3.5 border border-slate-200 space-y-2.5">
							<h4 class="font-bold text-slate-900 flex items-center space-x-1.5">
								<svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
								</svg>
								<span>Vehicle & Odometer Log</span>
							</h4>

							<div class="grid grid-cols-2 gap-2.5 text-[11px]">
								<div class="p-2 rounded-xl bg-slate-50 border border-slate-100">
									<span class="text-slate-400 font-medium block">Vehicle Type</span>
									<span class="font-bold text-slate-800">{{ currentDetailDoc.vehicle_type }} (₹{{ currentDetailDoc.rate_per_km || 0 }}/km)</span>
								</div>

								<div class="p-2 rounded-xl bg-slate-50 border border-slate-100">
									<span class="text-slate-400 font-medium block">Total Recorded Dist.</span>
									<span class="font-bold font-mono text-teal-800">{{ currentDetailDoc.total_distance || 0 }} km</span>
								</div>

								<div class="p-2 rounded-xl bg-slate-50 border border-slate-100">
									<span class="text-slate-400 font-medium block">Start Odometer</span>
									<span class="font-bold font-mono text-slate-800">{{ currentDetailDoc.start_odometerkm ? `${currentDetailDoc.start_odometerkm} km` : 'Not recorded' }}</span>
									<span v-if="currentDetailDoc.start_time" class="text-[10px] text-slate-400 block">{{ formatTime(currentDetailDoc.start_time) }}</span>
								</div>

								<div class="p-2 rounded-xl bg-slate-50 border border-slate-100">
									<span class="text-slate-400 font-medium block">End Odometer</span>
									<span class="font-bold font-mono text-slate-800">{{ currentDetailDoc.end_odometerkm ? `${currentDetailDoc.end_odometerkm} km` : 'Not recorded' }}</span>
									<span v-if="currentDetailDoc.end_time" class="text-[10px] text-slate-400 block">{{ formatTime(currentDetailDoc.end_time) }}</span>
								</div>
							</div>

							<div v-if="currentDetailDoc.start_narration" class="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-xl">
								<span class="font-semibold text-slate-700">Start Note:</span> {{ currentDetailDoc.start_narration }}
							</div>
							<div v-if="currentDetailDoc.end_narration" class="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-xl">
								<span class="font-semibold text-slate-700">End Note:</span> {{ currentDetailDoc.end_narration }}
							</div>
						</div>

						<!-- Site Visits Timeline Section -->
						<div class="bg-white rounded-2xl p-3.5 border border-slate-200 space-y-3">
							<div class="flex items-center justify-between">
								<h4 class="font-bold text-slate-900 flex items-center space-x-1.5">
									<svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
									</svg>
									<span>Site Visits Logged ({{ detailSiteTracking.length }})</span>
								</h4>
							</div>

							<div v-if="detailSiteTracking.length === 0" class="text-center py-4 text-slate-400 text-xs italic">
								No site visits logged for this day.
							</div>

							<div v-else class="space-y-2.5 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-teal-100">
								<div
									v-for="(site, idx) in detailSiteTracking"
									:key="site.name || idx"
									class="relative flex items-start space-x-3 pl-1 text-xs"
								>
									<!-- Bullet Badge -->
									<div class="w-6 h-6 rounded-full bg-teal-600 text-white font-bold text-[10px] flex items-center justify-center shrink-0 shadow-xs relative z-10">
										{{ idx + 1 }}
									</div>

									<!-- Visit Details -->
									<div class="flex-1 bg-slate-50 p-2.5 rounded-xl border border-slate-100/80 space-y-1.5">
										<div class="flex items-start justify-between">
											<div>
												<span class="font-bold text-slate-900 block">{{ site.customer || site.location_name || site.site || 'Site Location' }}</span>
												<div class="flex items-center gap-1.5 mt-0.5">
													<span v-if="site.category" class="px-1.5 py-0.2 rounded bg-teal-50 text-teal-800 font-bold text-[9px] border border-teal-200">
														{{ site.category }}
													</span>
													<span v-if="site.site" class="text-[10px] text-slate-500 truncate max-w-[150px]">{{ site.site }}</span>
												</div>
											</div>
											<span v-if="site.actual_distance" class="text-[10px] font-mono font-bold text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded border border-teal-100 shrink-0">
												+{{ site.actual_distance }} km
											</span>
										</div>

										<div v-if="site.contact_number || site.address" class="space-y-0.5 text-[10px]">
											<div v-if="site.contact_number" class="flex items-center space-x-1 text-slate-700 font-mono">
												<span>📞</span>
												<a :href="'tel:' + site.contact_number" class="text-teal-700 font-bold hover:underline">{{ site.contact_number }}</a>
											</div>
											<div v-if="site.address" class="flex items-start space-x-1 text-slate-500">
												<span>📍</span>
												<span class="truncate">{{ site.address }}</span>
											</div>
										</div>

										<div class="flex items-center space-x-2 text-[10px] text-slate-400">
											<span v-if="site.checkin_time">Time: {{ formatTime(site.checkin_time) }}</span>
											<span v-if="site.site_lat && site.site_long" class="truncate font-mono">({{ Number(site.site_lat).toFixed(4) }}, {{ Number(site.site_long).toFixed(4) }})</span>
										</div>

										<p v-if="site.remarks" class="text-[11px] text-slate-600 italic bg-white p-1.5 rounded-lg border border-slate-100">
											"{{ site.remarks }}"
										</p>
									</div>
								</div>
							</div>
						</div>

						<!-- Additional Expenses Section -->
						<div class="bg-white rounded-2xl p-3.5 border border-slate-200 space-y-3">
							<h4 class="font-bold text-slate-900 flex items-center space-x-1.5">
								<svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<span>Other Expenses ({{ detailExpenseTracking.length }})</span>
							</h4>

							<div v-if="detailExpenseTracking.length === 0" class="text-center py-3 text-slate-400 text-xs italic">
								No additional expenses logged for this day.
							</div>

							<div v-else class="space-y-1.5">
								<div
									v-for="(exp, idx) in detailExpenseTracking"
									:key="exp.name || idx"
									class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs"
								>
									<div class="space-y-0.5 min-w-0 pr-2">
										<div class="flex items-center space-x-1.5 flex-wrap">
											<span class="font-bold text-slate-800">{{ exp.expense_type || 'Expense' }}</span>
											<button
												v-if="exp.attachment"
												type="button"
												@click="viewReceipt(exp.attachment, `${exp.expense_type} Bill - ₹${(exp.amount || 0).toLocaleString('en-IN')}`)"
												class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 text-[10px] font-bold cursor-pointer transition shadow-2xs"
												title="View Bill Receipt"
											>
												<span>📎</span>
												<span>Bill</span>
											</button>
										</div>
										<p v-if="exp.description" class="text-[10px] text-slate-500 truncate">{{ exp.description }}</p>
									</div>
									<span class="font-mono font-bold text-slate-900 shrink-0">₹{{ (exp.amount || 0).toLocaleString('en-IN') }}</span>
								</div>
							</div>
						</div>

					</div>
				</div>
			</template>

			<template #actions>
				<div class="w-full flex justify-end space-x-2">
					<Button
						variant="subtle"
						@click="showDetailModal = false"
					>
						Close
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- ========================================================= -->
		<!-- MODAL: RECEIPT VIEWER LIGHTBOX (Teleported Standalone)   -->
		<!-- ========================================================= -->
		<Teleport to="body">
			<Transition
				enter-active-class="transition duration-200 ease-out"
				enter-from-class="opacity-0"
				enter-to-class="opacity-100"
				leave-active-class="transition duration-150 ease-in"
				leave-from-class="opacity-100"
				leave-to-class="opacity-0"
			>
				<div
					v-if="showReceiptModal"
					class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xs"
					@click.self="showReceiptModal = false"
				>
					<div class="bg-white rounded-3xl max-w-sm w-full p-4 shadow-2xl space-y-3 overflow-hidden border border-slate-200 relative animate-scaleUp">
						<!-- Header -->
						<div class="flex items-center justify-between pb-2.5 border-b border-slate-100">
							<div class="flex items-center space-x-2 min-w-0 pr-2">
								<span class="text-base">🧾</span>
								<h3 class="font-bold text-slate-900 text-xs truncate">{{ previewReceiptTitle || 'Expense Receipt' }}</h3>
							</div>
							<button
								type="button"
								@click="showReceiptModal = false"
								class="w-7 h-7 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition cursor-pointer font-bold text-xs"
							>
								✕
							</button>
						</div>

						<!-- Content Preview -->
						<div class="space-y-3">
							<div v-if="isImageFile(previewReceiptUrl)" class="flex justify-center bg-slate-100/60 p-2 rounded-2xl border border-slate-200/80 max-h-80 overflow-auto">
								<img
									:src="previewReceiptUrl"
									class="max-h-72 w-auto rounded-xl object-contain shadow-sm"
									alt="Receipt"
								/>
							</div>
							<div v-else class="p-6 text-center bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
								<div class="text-4xl">📄</div>
								<p class="text-xs font-semibold text-slate-700">PDF Document Attached</p>
								<a
									:href="previewReceiptUrl"
									target="_blank"
									class="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold shadow-sm transition"
								>
									<span>Open PDF in New Tab</span>
									<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
									</svg>
								</a>
							</div>
						</div>

						<!-- Footer Actions -->
						<div class="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
							<a
								:href="previewReceiptUrl"
								target="_blank"
								download
								class="font-bold text-teal-700 hover:underline inline-flex items-center space-x-1 text-[11px]"
							>
								<span>Open Full Size ↗</span>
							</a>
							<button
								type="button"
								@click="showReceiptModal = false"
								class="px-4 py-2 text-xs font-bold text-white bg-slate-800 hover:bg-slate-700 rounded-xl cursor-pointer"
							>
								Close Preview
							</button>
						</div>
					</div>
				</div>
			</Transition>
		</Teleport>

	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { Dialog, Button, call } from "frappe-ui"
import { eemDetailResource } from "@/data/eem"

const router = useRouter()

// Filters state
const searchQuery = ref("")
const selectedStatus = ref("in_progress")
const selectedDatePreset = ref("all")
const selectedMonth = ref("all")
const selectedVehicle = ref("all")
const selectedSort = ref("date_desc")
const isGroupedByMonth = ref(false)
const isFilterDrawerOpen = ref(false)
const customFromDate = ref("")
const customToDate = ref("")

// Pagination state
const rawHistoryRecords = ref([])
const isLoadingHistory = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(false)

// Modal State
const showDetailModal = ref(false)
const currentDetailDoc = ref(null)
const linkedExpenseClaim = ref(null)

const showReceiptModal = ref(false)
const previewReceiptUrl = ref("")
const previewReceiptTitle = ref("")

function isImageFile(url) {
	if (!url) return false
	return /\.(jpg|jpeg|png|webp|gif|svg|avif)($|\?)/i.test(url)
}

function viewReceipt(url, title = "Expense Receipt") {
	if (!url) return
	previewReceiptUrl.value = url
	previewReceiptTitle.value = title
	showReceiptModal.value = true
}

const datePresets = [
	{ label: "All Time", value: "all" },
	{ label: "This Month", value: "this_month" },
	{ label: "Last Month", value: "last_month" },
	{ label: "Last 3 Months", value: "last_3_months" },
	{ label: "This Year", value: "this_year" },
	{ label: "Custom", value: "custom" },
]

function setDatePreset(val) {
	selectedDatePreset.value = val
	if (val !== "custom") {
		customFromDate.value = ""
		customToDate.value = ""
	} else {
		isFilterDrawerOpen.value = true
	}
}

const hasActiveFilters = computed(() => {
	return (
		selectedDatePreset.value !== "all" ||
		selectedMonth.value !== "all" ||
		selectedVehicle.value !== "all" ||
		selectedStatus.value !== "in_progress" ||
		(searchQuery.value && searchQuery.value.trim().length > 0)
	)
})

function resetAllFilters() {
	searchQuery.value = ""
	selectedStatus.value = "in_progress"
	selectedDatePreset.value = "all"
	selectedMonth.value = "all"
	selectedVehicle.value = "all"
	selectedSort.value = "date_desc"
	customFromDate.value = ""
	customToDate.value = ""
}

// Available months dynamically extracted from loaded history
const availableMonths = computed(() => {
	const records = (rawHistoryRecords.value || []).filter(r => r.docstatus !== 2 && r.expense_claim_status !== "Cancelled")
	const monthMap = {}
	for (const r of records) {
		if (!r.date) continue
		const d = new Date(r.date)
		if (isNaN(d.getTime())) continue
		const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
		const label = d.toLocaleDateString("en-US", { month: "short", year: "numeric" })
		if (!monthMap[key]) {
			monthMap[key] = { key, label, count: 0 }
		}
		monthMap[key].count++
	}
	return Object.values(monthMap).sort((a, b) => b.key.localeCompare(a.key))
})

const selectedMonthLabel = computed(() => {
	const found = availableMonths.value.find(m => m.key === selectedMonth.value)
	return found ? found.label : selectedMonth.value
})

const selectedDatePresetLabel = computed(() => {
	const found = datePresets.find(p => p.value === selectedDatePreset.value)
	return found ? found.label : selectedDatePreset.value
})

const statusFilters = computed(() => {
	const all = (rawHistoryRecords.value || []).filter(r => r.docstatus !== 2 && r.expense_claim_status !== "Cancelled")
	const inProgress = all.filter(r => isTripInProgress(r)).length
	const submitted = all.filter(r => r.docstatus === 1 || r.expense_claim_status === "Submitted" || r.expense_claim_status === "Approved" || r.expense_claim_status === "Paid").length
	const draft = all.filter(r => r.docstatus === 0 && !isTripInProgress(r)).length

	return [
		{ label: "Active", value: "in_progress", count: inProgress },
		{ label: "All Trips", value: "all", count: all.length },
		{ label: "Submitted", value: "submitted", count: submitted },
		{ label: "Drafts", value: "draft", count: draft },
	]
})

const filteredRecords = computed(() => {
	let list = (rawHistoryRecords.value || []).filter(r => r.docstatus !== 2 && r.expense_claim_status !== "Cancelled")

	// Status Filter
	if (selectedStatus.value === "submitted") {
		list = list.filter(r => r.docstatus === 1 || r.expense_claim_status === "Submitted" || r.expense_claim_status === "Approved" || r.expense_claim_status === "Paid")
	} else if (selectedStatus.value === "draft") {
		list = list.filter(r => r.docstatus === 0 && !isTripInProgress(r))
	} else if (selectedStatus.value === "in_progress") {
		list = list.filter(r => isTripInProgress(r))
	}

	// Vehicle Filter
	if (selectedVehicle.value !== "all") {
		list = list.filter(r => r.vehicle_type === selectedVehicle.value)
	}

	// Specific Month Filter
	if (selectedMonth.value !== "all") {
		list = list.filter(r => {
			if (!r.date) return false
			const d = new Date(r.date)
			const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
			return key === selectedMonth.value
		})
	}

	// Date Range Presets
	const now = new Date()
	if (selectedDatePreset.value === "this_month") {
		const thisMonthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
		list = list.filter(r => {
			if (!r.date) return false
			const d = new Date(r.date)
			const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
			return key === thisMonthKey
		})
	} else if (selectedDatePreset.value === "last_month") {
		const lastMonthDate = new Date(now.getFullYear(), now.getMonth() - 1, 1)
		const lastMonthKey = `${lastMonthDate.getFullYear()}-${String(lastMonthDate.getMonth() + 1).padStart(2, "0")}`
		list = list.filter(r => {
			if (!r.date) return false
			const d = new Date(r.date)
			const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
			return key === lastMonthKey
		})
	} else if (selectedDatePreset.value === "last_3_months") {
		const pastDate = new Date()
		pastDate.setMonth(pastDate.getMonth() - 3)
		list = list.filter(r => {
			if (!r.date) return false
			return new Date(r.date) >= pastDate
		})
	} else if (selectedDatePreset.value === "this_year") {
		const thisYear = now.getFullYear()
		list = list.filter(r => {
			if (!r.date) return false
			return new Date(r.date).getFullYear() === thisYear
		})
	} else if (selectedDatePreset.value === "custom") {
		if (customFromDate.value) {
			list = list.filter(r => r.date >= customFromDate.value)
		}
		if (customToDate.value) {
			list = list.filter(r => r.date <= customToDate.value)
		}
	}

	// Search Query (ID, Date, Vehicle, Remarks, End Narration, Site Keywords)
	if (searchQuery.value && searchQuery.value.trim()) {
		const q = searchQuery.value.toLowerCase().trim()
		list = list.filter(r => {
			return (
				(r.name && r.name.toLowerCase().includes(q)) ||
				(r.date && r.date.toLowerCase().includes(q)) ||
				(r.vehicle_type && r.vehicle_type.toLowerCase().includes(q)) ||
				(r.remarks && r.remarks.toLowerCase().includes(q)) ||
				(r.end_narration && r.end_narration.toLowerCase().includes(q)) ||
				(r.site_keywords && r.site_keywords.toLowerCase().includes(q))
			)
		})
	}

	// Sorting
	return list.slice().sort((a, b) => {
		if (selectedSort.value === "date_asc") {
			return (a.date || "").localeCompare(b.date || "")
		} else if (selectedSort.value === "claim_desc") {
			return (b.total_expense || 0) - (a.total_expense || 0)
		} else if (selectedSort.value === "dist_desc") {
			return (b.total_distance || 0) - (a.total_distance || 0)
		} else {
			// date_desc
			return (b.date || "").localeCompare(a.date || "") || (b.creation || "").localeCompare(a.creation || "")
		}
	})
})

// Grouped by Month Data Structure
const groupedRecords = computed(() => {
	const groups = {}
	for (const rec of filteredRecords.value) {
		if (!rec.date) continue
		const d = new Date(rec.date)
		const monthKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
		const monthLabel = d.toLocaleDateString("en-US", { month: "long", year: "numeric" })
		if (!groups[monthKey]) {
			groups[monthKey] = {
				monthKey,
				monthLabel,
				totalDistance: 0,
				totalExpense: 0,
				totalSites: 0,
				records: [],
			}
		}
		groups[monthKey].records.push(rec)
		groups[monthKey].totalDistance += Number(rec.total_distance || 0)
		groups[monthKey].totalExpense += Number(rec.total_expense || 0)
		groups[monthKey].totalSites += Number(rec.sites_count || 0)
	}
	return Object.values(groups)
})

function isTripInProgress(rec) {
	if (!rec) return false
	return isToday(rec.date) && rec.docstatus === 0
}

function isToday(dateStr) {
	if (!dateStr) return false
	const todayStr = new Date().toISOString().split("T")[0]
	return dateStr === todayStr
}

// Summary Statistics for the active filter set
const statsTotalDistance = computed(() => {
	return filteredRecords.value.reduce((acc, r) => acc + (Number(r.total_distance) || 0), 0)
})

const statsTotalExpense = computed(() => {
	return filteredRecords.value.reduce((acc, r) => acc + (Number(r.total_expense) || 0), 0)
})

const statsTotalSites = computed(() => {
	return filteredRecords.value.reduce((acc, r) => acc + (Number(r.sites_count) || 0), 0)
})

const detailSiteTracking = computed(() => {
	return currentDetailDoc.value?.employee_site_tracking || []
})

const detailExpenseTracking = computed(() => {
	return currentDetailDoc.value?.employee_expense_tracking || []
})

function formatDisplayDate(dateStr) {
	if (!dateStr) return "-"
	const d = new Date(dateStr)
	if (isNaN(d.getTime())) return dateStr
	return d.toLocaleDateString("en-US", {
		weekday: "short",
		day: "numeric",
		month: "short",
		year: "numeric",
	})
}

function formatTime(timeStr) {
	if (!timeStr) return "-"
	if (timeStr.includes(":")) {
		const parts = timeStr.split(":")
		let hours = parseInt(parts[0], 10)
		const minutes = parts[1]
		const ampm = hours >= 12 ? "PM" : "AM"
		hours = hours % 12 || 12
		return `${hours}:${minutes} ${ampm}`
	}
	return timeStr
}

function getStatusBadgeLabel(rec) {
	if (!rec) return "-"
	if (isTripInProgress(rec)) return "In Progress"
	if (rec.docstatus === 1) return rec.expense_claim_status || "Submitted"
	if (rec.docstatus === 0) return "Draft"
	if (rec.docstatus === 2) return "Cancelled"
	return "Saved"
}

function getStatusBadgeClass(rec) {
	if (!rec) return "bg-slate-100 text-slate-600"
	if (isTripInProgress(rec)) return "bg-emerald-100 text-emerald-800 border border-emerald-300 shadow-xs"
	if (rec.docstatus === 1) {
		const st = (rec.expense_claim_status || "").toLowerCase()
		if (st === "paid" || st === "approved") {
			return "bg-emerald-50 text-emerald-700 border border-emerald-200"
		}
		return "bg-teal-50 text-teal-700 border border-teal-200"
	}
	if (rec.docstatus === 0) {
		return "bg-amber-50 text-amber-700 border border-amber-200"
	}
	return "bg-slate-100 text-slate-600 border border-slate-200"
}

async function viewTripDetail(rec) {
	currentDetailDoc.value = rec
	linkedExpenseClaim.value = null
	showDetailModal.value = true

	try {
		const res = await eemDetailResource.submit({ eem_name: rec.name })
		if (res && res.doc) {
			currentDetailDoc.value = res.doc
			linkedExpenseClaim.value = res.linked_expense_claim || null
		}
	} catch (err) {
		console.warn("Could not load full trip details, using cached card data:", err)
	}
}

async function fetchHistory() {
	isLoadingHistory.value = true
	try {
		const res = await call("tq_erphr.pwa_api.get_eem_history", {
			limit: 10,
			limit_start: 0,
		})
		rawHistoryRecords.value = res || []
		hasMore.value = (res || []).length === 10
	} catch (err) {
		console.error("Failed to fetch EEM history:", err)
	} finally {
		isLoadingHistory.value = false
	}
}

async function loadMoreHistory() {
	if (isLoadingMore.value || !hasMore.value) return
	isLoadingMore.value = true
	try {
		const res = await call("tq_erphr.pwa_api.get_eem_history", {
			limit: 10,
			limit_start: rawHistoryRecords.value.length,
		})
		const items = res || []
		rawHistoryRecords.value = [...rawHistoryRecords.value, ...items]
		if (items.length < 10) {
			hasMore.value = false
		}
	} catch (err) {
		console.error("Failed to load more EEM history:", err)
	} finally {
		isLoadingMore.value = false
	}
}

function goBack() {
	router.push("/")
}

function goToEem() {
	router.push("/eem")
}

onMounted(() => {
	fetchHistory()
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
	display: none;
}
.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
</style>
