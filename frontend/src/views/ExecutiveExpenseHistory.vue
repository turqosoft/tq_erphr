<template>
	<div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-start items-center p-0 sm:p-4 font-sans selection:bg-teal-500 selection:text-white relative overflow-x-hidden pb-24">
		<!-- Background ambient soft gradients for desktop container -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-emerald-200/20 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full sm:max-w-md bg-[#f8fafc] min-h-screen sm:min-h-[720px] sm:rounded-3xl sm:shadow-2xl sm:border sm:border-slate-200/80 flex flex-col justify-between relative z-10 overflow-hidden pb-6">
			
			<!-- Mobile Top Header -->
			<header class="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/70 px-4 py-3.5 sm:px-5 transition-all shadow-xs">
				<div class="flex items-center justify-between">
					<!-- Back Navigation & Title -->
					<div class="flex items-center space-x-2.5">
						<button
							@click="goBack"
							class="p-2 -ml-1 rounded-2xl text-slate-600 hover:text-teal-700 hover:bg-teal-50/80 active:scale-95 transition"
							title="Back"
						>
							<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
							</svg>
						</button>
						<div>
							<h1 class="text-sm font-bold text-slate-900 leading-tight">EEM Travel History</h1>
							<p class="text-[10px] font-medium text-slate-500 leading-none">Past Field Trips & Expenses</p>
						</div>
					</div>

					<!-- Header Actions -->
					<div class="flex items-center space-x-1.5">
						<!-- Refresh Button -->
						<button
							@click="fetchHistory"
							:disabled="eemHistoryResource.loading"
							class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition"
							title="Refresh trip history"
						>
							<svg
								class="w-4 h-4"
								:class="{ 'animate-spin text-teal-600': eemHistoryResource.loading }"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
						</button>
					</div>
				</div>

				<!-- Quick Filter Bar (Month & Status) -->
				<div class="mt-3 flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
					<button
						v-for="filter in statusFilters"
						:key="filter.value"
						@click="selectedStatus = filter.value"
						:class="[
							'px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all flex items-center space-x-1.5',
							selectedStatus === filter.value
								? 'bg-teal-700 text-white shadow-xs shadow-teal-700/20'
								: 'bg-slate-100 text-slate-600 hover:bg-slate-200/80 hover:text-slate-800'
						]"
					>
						<span>{{ filter.label }}</span>
						<span
							v-if="filter.count > 0"
							:class="[
								'text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold',
								selectedStatus === filter.value
									? 'bg-teal-800 text-teal-100'
									: 'bg-slate-200 text-slate-700'
							]"
						>
							{{ filter.count }}
						</span>
					</button>
				</div>
			</header>

			<!-- Main Scrollable Content -->
			<main class="flex-1 px-4 sm:px-5 py-4 space-y-4">
				
				<!-- Cumulative Stats Banner -->
				<div class="bg-gradient-to-br from-teal-800 via-teal-900 to-slate-900 rounded-3xl p-4 text-white shadow-md relative overflow-hidden">
					<div class="absolute -right-8 -bottom-8 w-32 h-32 bg-teal-500/10 rounded-full blur-2xl pointer-events-none"></div>
					<div class="relative z-10">
						<div class="flex items-center justify-between text-xs text-teal-200/80 mb-3">
							<div class="flex items-center space-x-1.5 font-medium">
								<svg class="w-3.5 h-3.5 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
								</svg>
								<span>Filtered Period Summary</span>
							</div>
							<span class="text-[11px] font-mono text-teal-300">{{ filteredRecords.length }} Trips</span>
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
						placeholder="Search by date, trip ID, or notes..."
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

				<!-- Loading State -->
				<div v-if="eemHistoryResource.loading" class="py-12 text-center space-y-3">
					<div class="inline-block animate-spin text-teal-600">
						<svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
					</div>
					<p class="text-xs text-slate-500 font-medium">Loading your field travel history...</p>
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
						{{ searchQuery ? 'No records match your search criteria.' : 'No executive expense manager records have been logged yet.' }}
					</p>
					<button
						@click="goToEem"
						class="mt-2 inline-flex items-center space-x-1.5 px-4 py-2 rounded-2xl bg-teal-600 text-white text-xs font-semibold shadow-xs hover:bg-teal-700 transition"
					>
						<span>Start Today's Travel</span>
					</button>
				</div>

				<!-- List of Trip Cards -->
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
										'px-2.5 py-1 rounded-full text-[10px] tracking-wide uppercase flex items-center',
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
									{{ rec.expenses_count }} {{ rec.expenses_count === 1 ? 'expense item' : 'expense items' }}
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

		<!-- MODAL / DRAWER: DETAILED DAY VIEW                                     -->
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
									<div class="flex-1 bg-slate-50 p-2.5 rounded-xl border border-slate-100/80 space-y-1">
										<div class="flex items-start justify-between">
											<span class="font-bold text-slate-900">{{ site.customer || site.location_name || site.site || 'Site Location' }}</span>
											<span v-if="site.actual_distance" class="text-[10px] font-mono font-bold text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded">
												+{{ site.actual_distance }} km
											</span>
										</div>

										<div class="flex items-center space-x-2 text-[10px] text-slate-400">
											<span v-if="site.checkin_time">Time: {{ formatTime(site.checkin_time) }}</span>
											<span v-if="site.site_lat && site.site_long" class="truncate font-mono">({{ site.site_lat.toFixed(4) }}, {{ site.site_long.toFixed(4) }})</span>
										</div>

										<p v-if="site.remarks" class="text-[11px] text-slate-600 italic">
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
									class="flex items-center justify-between p-2 rounded-xl bg-slate-50 border border-slate-100 text-xs"
								>
									<div>
										<span class="font-bold text-slate-800">{{ exp.expense_type || 'Expense' }}</span>
										<p v-if="exp.description" class="text-[10px] text-slate-500">{{ exp.description }}</p>
									</div>
									<span class="font-mono font-bold text-slate-900">₹{{ (exp.amount || 0).toLocaleString('en-IN') }}</span>
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

	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { Dialog, Button } from "frappe-ui"
import { eemHistoryResource, eemDetailResource } from "@/data/eem"

const router = useRouter()

const searchQuery = ref("")
const selectedStatus = ref("all")
const showDetailModal = ref(false)
const currentDetailDoc = ref(null)
const linkedExpenseClaim = ref(null)

const statusFilters = computed(() => {
	const all = (eemHistoryResource.data || []).filter(r => r.docstatus !== 2 && r.expense_claim_status !== 'Cancelled')
	const submitted = all.filter(r => r.docstatus === 1 || r.expense_claim_status === 'Submitted' || r.expense_claim_status === 'Approved' || r.expense_claim_status === 'Paid').length
	const draft = all.filter(r => r.docstatus === 0).length

	return [
		{ label: "All Trips", value: "all", count: all.length },
		{ label: "Submitted / Claimed", value: "submitted", count: submitted },
		{ label: "Draft Trips", value: "draft", count: draft },
	]
})

const filteredRecords = computed(() => {
	let list = (eemHistoryResource.data || []).filter(r => r.docstatus !== 2 && r.expense_claim_status !== 'Cancelled')

	if (selectedStatus.value === "submitted") {
		list = list.filter(r => r.docstatus === 1 || r.expense_claim_status === 'Submitted' || r.expense_claim_status === 'Approved' || r.expense_claim_status === 'Paid')
	} else if (selectedStatus.value === "draft") {
		list = list.filter(r => r.docstatus === 0)
	}

	if (searchQuery.value && searchQuery.value.trim()) {
		const q = searchQuery.value.toLowerCase().trim()
		list = list.filter(r => {
			return (
				(r.name && r.name.toLowerCase().includes(q)) ||
				(r.date && r.date.toLowerCase().includes(q)) ||
				(r.vehicle_type && r.vehicle_type.toLowerCase().includes(q)) ||
				(r.remarks && r.remarks.toLowerCase().includes(q)) ||
				(r.end_narration && r.end_narration.toLowerCase().includes(q))
			)
		})
	}

	return list
})

function isTripInProgress(rec) {
	if (!rec) return false
	return isToday(rec.date) && rec.docstatus === 0
}

// Summary metrics
const statsTotalDistance = computed(() => {
	return filteredRecords.value.reduce((sum, r) => sum + (r.total_distance || 0), 0)
})

const statsTotalExpense = computed(() => {
	return filteredRecords.value.reduce((sum, r) => sum + (r.total_expense || 0), 0)
})

const statsTotalSites = computed(() => {
	return filteredRecords.value.reduce((sum, r) => sum + (r.sites_count || 0), 0)
})

const detailSiteTracking = computed(() => {
	return currentDetailDoc.value?.employee_site_tracking || []
})

const detailExpenseTracking = computed(() => {
	return currentDetailDoc.value?.employee_expense_tracking || []
})

function fetchHistory() {
	eemHistoryResource.fetch({ limit: 100 })
}

async function viewTripDetail(rec) {
	currentDetailDoc.value = rec
	linkedExpenseClaim.value = null
	showDetailModal.value = true

	try {
		const res = await eemDetailResource.fetch({ eem_name: rec.name })
		if (res && res.doc) {
			currentDetailDoc.value = res.doc
			linkedExpenseClaim.value = res.linked_expense_claim
		}
	} catch (err) {
		console.error("Failed to load trip details:", err)
	}
}

function getStatusBadgeLabel(rec) {
	if (!rec) return ""
	if (isTripInProgress(rec)) {
		return "In Progress"
	}
	if (rec.expense_claim_status && rec.expense_claim_status !== "Not Created") {
		return rec.expense_claim_status
	}
	if (rec.docstatus === 1) {
		return "Submitted"
	}
	return "Draft"
}

function getStatusBadgeClass(rec) {
	if (isTripInProgress(rec)) {
		return "bg-emerald-100 text-emerald-800 border border-emerald-300 font-black shadow-xs"
	}
	const status = getStatusBadgeLabel(rec)
	switch (status) {
		case "Paid":
		case "Approved":
			return "bg-emerald-100 text-emerald-800 border border-emerald-300"
		case "Submitted":
		case "Processing":
			return "bg-teal-100 text-teal-800 border border-teal-300"
		default:
			return "bg-amber-100 text-amber-800 border border-amber-300"
	}
}

function formatDisplayDate(dateStr) {
	if (!dateStr) return ""
	try {
		const d = new Date(dateStr)
		return d.toLocaleDateString("en-IN", {
			weekday: "short",
			day: "numeric",
			month: "short",
			year: "numeric"
		})
	} catch (e) {
		return dateStr
	}
}

function formatTime(timeStr) {
	if (!timeStr) return ""
	try {
		const parts = timeStr.split(":")
		if (parts.length >= 2) {
			let hours = parseInt(parts[0], 10)
			const minutes = parts[1]
			const ampm = hours >= 12 ? "PM" : "AM"
			hours = hours % 12 || 12
			return `${hours}:${minutes} ${ampm}`
		}
		return timeStr
	} catch (e) {
		return timeStr
	}
}

function isToday(dateStr) {
	if (!dateStr) return false
	const today = new Date().toISOString().split("T")[0]
	return dateStr === today
}

function goBack() {
	if (window.history.length > 1) {
		router.back()
	} else {
		router.push("/")
	}
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
