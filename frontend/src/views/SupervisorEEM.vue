<template>
	<div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-start items-center p-0 sm:p-4 font-sans selection:bg-teal-500 selection:text-white relative overflow-x-hidden pb-24">
		<!-- Background ambient soft gradients -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-emerald-200/20 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full sm:max-w-md bg-[#f8fafc] min-h-screen sm:min-h-[720px] sm:rounded-3xl sm:shadow-2xl sm:border sm:border-slate-200/80 flex flex-col justify-between relative z-10 overflow-hidden pb-6">
			
			<!-- Mobile Top Header (Fixed at top) -->
			<header class="fixed top-0 inset-x-0 z-40 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 shadow-[0_2px_16px_rgba(0,0,0,0.04)] px-4 py-3 sm:px-5 transition-all">
				<div class="max-w-md mx-auto">
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
									<span>Supervisor EEM</span>
									<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-teal-100 text-teal-800">
										Team
									</span>
								</h1>
								<p class="text-[10px] font-medium text-slate-500 leading-none flex items-center gap-1 mt-0.5">
									<span v-if="employee?.company_name" class="font-semibold text-teal-700">{{ employee.company_name }} •</span>
									<span>Subordinate Field Tracking</span>
								</p>
							</div>
						</div>

						<!-- Header Actions -->
						<div class="flex items-center space-x-1.5">
							<!-- Date Picker Quick Trigger -->
							<button
								@click="isDatePickerOpen = !isDatePickerOpen"
								class="p-2 rounded-2xl text-slate-600 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer flex items-center gap-1 text-xs font-semibold"
								:class="{ 'bg-teal-50 text-teal-700 ring-1 ring-teal-300': isCustomDate }"
								title="Select Date"
							>
								<svg class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
								</svg>
							</button>

							<!-- Refresh Button -->
							<button
								@click="fetchDashboardData"
								:disabled="isLoading"
								class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
								title="Refresh dashboard"
							>
								<svg
									class="w-4 h-4"
									:class="{ 'animate-spin text-teal-600': isLoading }"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
								</svg>
							</button>
						</div>
					</div>
				</div>
			</header>

			<!-- Main Content Body (With top padding for fixed header) -->
			<main class="w-full flex-1 flex flex-col pt-16 px-4 sm:px-5 space-y-4">
				
				<!-- Date Selector Bar -->
				<div class="bg-white rounded-2xl p-2.5 shadow-sm border border-slate-200/80 flex items-center justify-between gap-2">
					<div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
						<button
							@click="setDate('today')"
							class="px-2.5 py-1 text-xs font-semibold rounded-xl transition cursor-pointer whitespace-nowrap"
							:class="selectedDateMode === 'today' ? 'bg-teal-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
						>
							Today
						</button>
						<button
							@click="setDate('yesterday')"
							class="px-2.5 py-1 text-xs font-semibold rounded-xl transition cursor-pointer whitespace-nowrap"
							:class="selectedDateMode === 'yesterday' ? 'bg-teal-600 text-white shadow-sm' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
						>
							Yesterday
						</button>
						<input
							type="date"
							v-model="targetDate"
							@change="onCustomDateChange"
							class="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2 py-1 font-medium text-slate-700 outline-none focus:ring-1 focus:ring-teal-500 cursor-pointer"
						/>
					</div>

					<div class="text-[11px] font-bold text-slate-500 shrink-0">
						{{ formattedDateDisplay }}
					</div>
				</div>

				<!-- Not a Supervisor Notice -->
				<div
					v-if="!isLoading && !dashboardData?.is_supervisor"
					class="bg-amber-50 border border-amber-200 rounded-2xl p-5 text-center my-6 space-y-3"
				>
					<div class="w-12 h-12 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center mx-auto">
						<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
					<h3 class="text-sm font-bold text-slate-800">Supervisor Access Required</h3>
					<p class="text-xs text-slate-600 leading-relaxed">
						You do not have any subordinate sales executives or employees assigned under your profile in ERPNext.
					</p>
					<button
						@click="router.push('/eem')"
						class="px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold rounded-xl transition"
					>
						Go to My Personal EEM
					</button>
				</div>

				<template v-else>
					<!-- Team Metrics Summary Grid -->
					<div class="grid grid-cols-2 gap-2.5">
						<!-- Active Live Trips Card -->
						<div class="bg-white rounded-2xl p-3.5 shadow-sm border border-slate-200/80 flex flex-col justify-between">
							<div class="flex items-center justify-between">
								<span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
									<span>{{ isToday ? 'Live On Trip' : 'Active Trips' }}</span>
									<span v-if="isToday && dashboardData?.summary?.active_now_count > 0" class="flex h-2 w-2 relative">
										<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
										<span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
									</span>
								</span>
								<span class="w-6 h-6 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center text-xs">
									🟢
								</span>
							</div>
							<div class="mt-2 flex items-baseline gap-1.5">
								<span class="text-2xl font-black text-emerald-700">{{ dashboardData?.summary?.active_now_count || 0 }}</span>
								<span class="text-xs text-slate-500 font-medium">/ {{ dashboardData?.summary?.total_executives || 0 }} Reps</span>
							</div>
							<div class="text-[10px] text-slate-400 font-medium mt-0.5">
								{{ dashboardData?.summary?.completed_count || 0 }} completed {{ isToday ? 'today' : (isYesterday ? 'yesterday' : 'on date') }}
							</div>
						</div>

						<!-- Team Total Distance -->
						<div class="bg-white rounded-2xl p-3.5 shadow-sm border border-slate-200/80 flex flex-col justify-between">
							<div class="flex items-center justify-between">
								<span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Team Travel</span>
								<span class="w-6 h-6 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center text-xs">
									🚗
								</span>
							</div>
							<div class="mt-2 flex items-baseline gap-1">
								<span class="text-2xl font-black text-slate-800">{{ formatNumber(dashboardData?.summary?.total_distance_km || 0) }}</span>
								<span class="text-xs text-slate-500 font-semibold">KM</span>
							</div>
							<div class="text-[10px] text-teal-600 font-bold mt-0.5 flex items-center gap-1">
								<span>📍 {{ dashboardData?.summary?.total_site_visits || 0 }} customer visits</span>
							</div>
						</div>

						<!-- Team Total Claims -->
						<div class="bg-white rounded-2xl p-3.5 shadow-sm border border-slate-200/80 flex flex-col justify-between">
							<div class="flex items-center justify-between">
								<span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total Claims</span>
								<span class="w-6 h-6 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center text-xs">
									₹
								</span>
							</div>
							<div class="mt-2 flex items-baseline gap-1">
								<span class="text-xl font-black text-slate-800">₹{{ formatCurrency(dashboardData?.summary?.total_claims_amount || 0) }}</span>
							</div>
							<div class="text-[10px] text-slate-400 font-medium mt-0.5">
								Travel & Daily allowances
							</div>
						</div>

						<!-- Not Started / Idle -->
						<div class="bg-white rounded-2xl p-3.5 shadow-sm border border-slate-200/80 flex flex-col justify-between">
							<div class="flex items-center justify-between">
								<span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{{ isToday ? 'Not Started' : 'No Travel' }}</span>
								<span class="w-6 h-6 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center text-xs">
									⏱
								</span>
							</div>
							<div class="mt-2 flex items-baseline gap-1">
								<span class="text-xl font-black text-slate-700">{{ dashboardData?.summary?.not_started_count || 0 }}</span>
								<span class="text-xs text-slate-400 font-medium">{{ isToday ? 'pending' : 'no trips' }}</span>
							</div>
							<div class="text-[10px] text-slate-400 font-medium mt-0.5">
								{{ isToday ? 'No trip started yet' : 'No travel recorded' }}
							</div>
						</div>
					</div>

					<!-- Subordinates Team Member Dropdown Selector (Optimized for 20+ members) -->
					<div class="space-y-1.5 relative">
						<div class="flex items-center justify-between px-1">
							<span class="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Select Team Member</span>
							<span class="text-[10px] font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200">
								{{ teamMembers.length }} subordinates
							</span>
						</div>

						<!-- Dropdown Trigger Button -->
						<button
							@click="isMemberDropdownOpen = !isMemberDropdownOpen"
							class="w-full bg-white rounded-2xl p-3 border border-slate-200 shadow-xs hover:border-teal-500 transition-all flex items-center justify-between gap-2.5 cursor-pointer text-left"
							:class="{ 'ring-2 ring-teal-500/30 border-teal-500': isMemberDropdownOpen }"
						>
							<div class="flex items-center gap-2.5 min-w-0">
								<!-- Selected Avatar / Icon -->
								<div class="relative shrink-0">
									<div
										v-if="selectedSalesPerson === 'all'"
										class="w-8 h-8 rounded-full bg-teal-50 text-teal-700 font-bold flex items-center justify-center text-sm border border-teal-200"
									>
										👥
									</div>
									<template v-else>
										<img
											v-if="selectedMemberObj?.image"
											:src="selectedMemberObj.image"
											class="w-8 h-8 rounded-full object-cover ring-1 ring-slate-200"
										/>
										<div
											v-else
											class="w-8 h-8 rounded-full bg-gradient-to-br from-teal-600 to-teal-400 text-white font-bold text-xs flex items-center justify-center uppercase shadow-2xs"
										>
											{{ selectedMemberObj?.sales_person_name?.charAt(0) || 'S' }}
										</div>
										<span
											class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full ring-2 ring-white"
											:class="getStatusDotClass(selectedMemberObj?.today_trip_status)"
										></span>
									</template>
								</div>

								<!-- Selected Name Details -->
								<div class="min-w-0 flex-1">
									<div class="text-xs font-bold text-slate-900 truncate">
										{{ selectedSalesPerson === 'all' ? 'All Team Members (' + teamMembers.length + ')' : selectedMemberObj?.sales_person_name }}
									</div>
									<div class="text-[10px] text-slate-500 truncate">
										{{ selectedSalesPerson === 'all' ? 'Showing trips for all subordinates' : (selectedMemberObj?.designation || 'Sales Executive') }}
									</div>
								</div>
							</div>

							<!-- Actions / Chevron -->
							<div class="flex items-center gap-1.5 shrink-0">
								<span
									v-if="selectedSalesPerson !== 'all'"
									@click.stop="selectMemberAndClose('all')"
									class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-slate-100 hover:bg-slate-200 text-slate-600 transition cursor-pointer"
								>
									✕ All
								</span>
								<div class="p-1 rounded-lg text-slate-400">
									<svg
										class="w-4 h-4 transition-transform duration-200"
										:class="{ 'rotate-180 text-teal-700': isMemberDropdownOpen }"
										fill="none"
										viewBox="0 0 24 24"
										stroke="currentColor"
									>
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
									</svg>
								</div>
							</div>
						</button>

						<!-- Dropdown Backdrop for Dismissal -->
						<div
							v-if="isMemberDropdownOpen"
							class="fixed inset-0 z-20"
							@click="isMemberDropdownOpen = false"
						></div>

						<!-- Dropdown Options Popup Menu -->
						<div
							v-if="isMemberDropdownOpen"
							class="absolute left-0 right-0 top-full mt-1.5 z-30 bg-white rounded-2xl shadow-xl border border-slate-200 p-2 space-y-2 max-h-80 flex flex-col animate-in fade-in zoom-in-95 duration-150"
						>
							<!-- Live Search Bar inside Dropdown -->
							<div class="relative px-1 pt-1">
								<input
									type="text"
									v-model="memberSearchQuery"
									placeholder="Search by name, ID or role..."
									class="w-full pl-8 pr-7 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:ring-1 focus:ring-teal-500 focus:bg-white outline-none font-medium text-slate-800"
									autofocus
								/>
								<svg class="w-4 h-4 text-slate-400 absolute left-3 top-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
								<button
									v-if="memberSearchQuery"
									@click="memberSearchQuery = ''"
									class="absolute right-3 top-3 text-slate-400 hover:text-slate-600 text-xs cursor-pointer font-bold"
								>
									✕
								</button>
							</div>

							<!-- Members Scrollable List (Handles 20+ Members smoothly) -->
							<div class="overflow-y-auto space-y-1 flex-1 pr-0.5 divide-y divide-slate-50">
								<!-- Option 1: All Members -->
								<button
									@click="selectMemberAndClose('all')"
									class="w-full flex items-center justify-between p-2 rounded-xl text-left transition cursor-pointer"
									:class="selectedSalesPerson === 'all' ? 'bg-teal-50 text-teal-800 font-bold' : 'hover:bg-slate-50 text-slate-700'"
								>
									<div class="flex items-center gap-2">
										<span class="w-7 h-7 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-xs font-bold">
											👥
										</span>
										<div>
											<div class="text-xs font-bold">All Team Members</div>
											<div class="text-[10px] text-slate-400">{{ teamMembers.length }} subordinates</div>
										</div>
									</div>
									<span v-if="selectedSalesPerson === 'all'" class="text-teal-700 font-bold text-xs">✓</span>
								</button>

								<!-- Subordinate Options -->
								<button
									v-for="sub in filteredTeamMembers"
									:key="sub.sales_person"
									@click="selectMemberAndClose(sub.sales_person)"
									class="w-full flex items-center justify-between p-2 rounded-xl text-left transition cursor-pointer"
									:class="selectedSalesPerson === sub.sales_person ? 'bg-teal-50 text-teal-800 font-bold' : 'hover:bg-slate-50 text-slate-700'"
								>
									<div class="flex items-center gap-2.5 min-w-0">
										<div class="relative shrink-0">
											<img
												v-if="sub.image"
												:src="sub.image"
												class="w-7 h-7 rounded-full object-cover"
											/>
											<div
												v-else
												class="w-7 h-7 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center uppercase"
											>
												{{ sub.sales_person_name?.charAt(0) || 'S' }}
											</div>
											<span
												class="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full ring-1 ring-white"
												:class="getStatusDotClass(sub.today_trip_status)"
											></span>
										</div>

										<div class="min-w-0">
											<div class="text-xs font-bold truncate">{{ sub.sales_person_name }}</div>
											<div class="text-[10px] text-slate-400 truncate">
												{{ sub.designation || 'Sales Rep' }}
												<span v-if="sub.employee" class="text-slate-300">• {{ sub.employee }}</span>
											</div>
										</div>
									</div>

									<!-- Status Badge & Checkmark -->
									<div class="flex items-center gap-1.5 shrink-0">
										<span
											class="text-[9px] font-bold px-1.5 py-0.5 rounded-full"
											:class="getStatusBadgeClass(sub.today_trip_status)"
										>
											{{ getStatusLabel(sub.today_trip_status) }}
										</span>
										<span v-if="selectedSalesPerson === sub.sales_person" class="text-teal-700 font-bold text-xs">✓</span>
									</div>
								</button>

								<!-- Empty Search Result -->
								<div v-if="filteredTeamMembers.length === 0" class="py-4 text-center text-xs text-slate-400">
									No team member matches "{{ memberSearchQuery }}"
								</div>
							</div>
						</div>
					</div>

					<!-- Status Filter Tabs -->
					<div class="flex items-center bg-slate-200/80 p-1 rounded-2xl text-xs font-semibold">
						<button
							@click="filterByStatus('all')"
							class="flex-1 py-1.5 text-center rounded-xl transition cursor-pointer"
							:class="selectedStatus === 'all' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'"
						>
							All ({{ tripsList.length }})
						</button>
						<button
							@click="filterByStatus('ACTIVE')"
							class="flex-1 py-1.5 text-center rounded-xl transition cursor-pointer flex items-center justify-center gap-1"
							:class="selectedStatus === 'ACTIVE' ? 'bg-white text-emerald-700 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'"
						>
							<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
							Active
						</button>
						<button
							@click="filterByStatus('COMPLETED')"
							class="flex-1 py-1.5 text-center rounded-xl transition cursor-pointer"
							:class="selectedStatus === 'COMPLETED' ? 'bg-white text-blue-700 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'"
						>
							Completed
						</button>
						<button
							@click="filterByStatus('NOT_STARTED')"
							class="flex-1 py-1.5 text-center rounded-xl transition cursor-pointer"
							:class="selectedStatus === 'NOT_STARTED' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'"
						>
							{{ isToday ? 'Pending' : 'No Travel' }}
						</button>
					</div>

					<!-- Trips / Executives Card List -->
					<div class="space-y-3">
						<!-- Loading Skeleton -->
						<div v-if="isLoading" class="space-y-3 py-2">
							<div v-for="i in 3" :key="i" class="bg-white rounded-3xl p-4 border border-slate-200/80 space-y-3 animate-pulse">
								<div class="flex items-center gap-3">
									<div class="w-10 h-10 rounded-full bg-slate-200"></div>
									<div class="flex-1 space-y-1.5">
										<div class="h-3.5 bg-slate-200 rounded w-1/2"></div>
										<div class="h-2.5 bg-slate-100 rounded w-1/3"></div>
									</div>
								</div>
								<div class="h-14 bg-slate-50 rounded-2xl"></div>
							</div>
						</div>

						<!-- Empty State -->
						<div
							v-else-if="filteredTrips.length === 0"
							class="bg-white rounded-3xl p-8 border border-slate-200/80 text-center space-y-3 my-2"
						>
							<div class="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto text-xl">
								🔍
							</div>
							<h4 class="text-sm font-bold text-slate-800">No Records Found</h4>
							<p class="text-xs text-slate-500 max-w-xs mx-auto">
								No field trips found matching the selected filters for {{ formattedDateDisplay }}.
							</p>
						</div>

						<!-- Trip Card Item -->
						<div
							v-else
							v-for="trip in filteredTrips"
							:key="trip.sales_person + (trip.eem_name || 'none')"
							class="bg-white rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all overflow-hidden flex flex-col"
						>
							<!-- Executive Header Bar -->
							<div class="p-4 pb-3 flex items-start justify-between gap-3 border-b border-slate-100 bg-slate-50/50">
								<div class="flex items-center gap-3">
									<!-- Avatar -->
									<div class="relative shrink-0">
										<img
											v-if="trip.image"
											:src="trip.image"
											class="w-11 h-11 rounded-full object-cover ring-2 ring-slate-100"
										/>
										<div
											v-else
											class="w-11 h-11 rounded-full bg-gradient-to-br from-teal-600 to-teal-400 text-white font-bold text-sm flex items-center justify-center uppercase shadow-sm"
										>
											{{ trip.sales_person_name?.charAt(0) || 'S' }}
										</div>
										<span
											class="absolute bottom-0 right-0 w-3 h-3 rounded-full ring-2 ring-white"
											:class="getStatusDotClass(trip.trip_status)"
										></span>
									</div>

									<div>
										<h3 class="text-sm font-bold text-slate-900 leading-tight">
											{{ trip.sales_person_name }}
										</h3>
										<p class="text-[11px] text-slate-500 font-medium">
											{{ trip.designation || 'Sales Executive' }}
											<span v-if="trip.employee" class="text-slate-400">• {{ trip.employee }}</span>
										</p>
									</div>
								</div>

								<!-- Direct Actions (Call / WhatsApp) -->
								<div class="flex items-center gap-1 shrink-0">
									<a
										v-if="trip.cell_number"
										:href="'tel:' + trip.cell_number"
										class="p-2 rounded-xl bg-teal-50 text-teal-700 hover:bg-teal-100 active:scale-95 transition"
										title="Call Executive"
									>
										<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
										</svg>
									</a>

									<!-- Status Badge -->
									<div
										class="px-2.5 py-1 rounded-full text-[10px] font-bold inline-flex items-center gap-1 shadow-2xs"
										:class="getStatusBadgeClass(trip.trip_status)"
									>
										<span v-if="trip.trip_status === 'IN_PROGRESS'" class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
										<span>{{ getStatusLabel(trip.trip_status) }}</span>
									</div>
								</div>
							</div>

							<!-- Trip Details Section (If Trip Exists) -->
							<div v-if="trip.eem_name" class="p-4 space-y-3">
								<!-- Trip Numbers Summary Row -->
								<div class="grid grid-cols-3 gap-2 bg-slate-50/80 p-2.5 rounded-2xl border border-slate-100 text-center">
									<div>
										<div class="text-[10px] font-semibold text-slate-400 uppercase">Distance</div>
										<div class="text-xs font-black text-slate-800 mt-0.5">
											{{ formatNumber(trip.total_distance) }} <span class="text-[10px] font-normal text-slate-500">KM</span>
										</div>
									</div>
									<div class="border-x border-slate-200">
										<div class="text-[10px] font-semibold text-slate-400 uppercase">Visits</div>
										<div class="text-xs font-black text-teal-700 mt-0.5">
											{{ trip.site_visits_count }} <span class="text-[10px] font-normal text-slate-500">sites</span>
										</div>
									</div>
									<div>
										<div class="text-[10px] font-semibold text-slate-400 uppercase">Claim</div>
										<div class="text-xs font-black text-slate-800 mt-0.5">
											₹{{ formatCurrency(trip.total_expense) }}
										</div>
									</div>
								</div>

								<!-- Odometer & Time Details -->
								<div class="flex items-center justify-between text-xs text-slate-600 px-1 font-medium">
									<div class="flex items-center gap-1.5">
										<span class="text-slate-400">⏱ Time:</span>
										<span class="font-bold text-slate-800">{{ formatTimeOnly(trip.start_time) }}</span>
										<span v-if="trip.end_time && trip.trip_status !== 'IN_PROGRESS'" class="text-slate-400">➔ {{ formatTimeOnly(trip.end_time) }}</span>
										<span v-else class="text-emerald-600 font-bold">(Ongoing)</span>
									</div>
									<div class="flex items-center gap-1">
										<span class="text-slate-400">Odo:</span>
										<span class="font-semibold text-slate-700">{{ trip.start_odometerkm || 0 }} ➔ {{ trip.end_odometerkm && trip.trip_status !== 'IN_PROGRESS' ? trip.end_odometerkm : '-' }}</span>
									</div>
								</div>

								<!-- Recent Site Visits Chips -->
								<div v-if="trip.site_visits && trip.site_visits.length > 0" class="space-y-1.5">
									<div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Recent Customer Visits:</div>
									<div class="flex flex-wrap gap-1.5">
										<div
											v-for="sv in trip.site_visits.slice(0, 3)"
											:key="sv.name"
											class="bg-teal-50/70 border border-teal-100 rounded-xl px-2 py-1 text-[11px] text-teal-900 flex items-center gap-1 font-medium"
										>
											<span class="text-[9px] text-teal-600 font-bold">{{ formatTimeOnly(sv.visit_time) }}</span>
											<span class="truncate max-w-[140px] font-semibold">{{ sv.customer }}</span>
										</div>
										<span v-if="trip.site_visits.length > 3" class="text-[10px] font-bold text-slate-400 self-center">
											+{{ trip.site_visits.length - 3 }} more
										</span>
									</div>
								</div>

								<!-- Card Action Buttons -->
								<div class="flex items-center gap-2 pt-1">
									<button
										@click="viewTripDetail(trip.eem_name)"
										class="flex-1 py-2.5 px-3 bg-teal-700 hover:bg-teal-800 text-white rounded-xl text-xs font-bold active:scale-98 transition flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
									>
										<span>View Trip Breakdown</span>
										<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
										</svg>
									</button>

									<!-- Open Live GPS Location if Available -->
									<a
										v-if="trip.start_lat && trip.start_long"
										:href="getMapUrl(trip.start_lat, trip.start_long)"
										target="_blank"
										class="p-2 bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-xl transition cursor-pointer"
										title="View Start Location in Google Maps"
									>
										<svg class="w-4 h-4 text-teal-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
										</svg>
									</a>
								</div>
							</div>

							<!-- Not Started / No Travel State in Card -->
							<div v-else class="p-4 text-center py-5 space-y-2 bg-white">
								<p class="text-xs text-slate-400 font-medium">
									{{ isToday ? "Executive has not initiated today's travel yet." : ("No travel logged for " + (isYesterday ? 'yesterday' : formattedDateDisplay) + ".") }}
								</p>
								<div v-if="trip.cell_number" class="pt-1">
									<a
										:href="'tel:' + trip.cell_number"
										class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition"
									>
										<svg class="w-3.5 h-3.5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
										</svg>
										<span>Call {{ getFirstName(trip.sales_person_name) }}</span>
									</a>
								</div>
							</div>
						</div>
					</div>
				</template>

			</main>

			<!-- Trip Detail Full Modal Sheet -->
			<div
				v-if="selectedDetailTrip"
				class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-900/60 backdrop-blur-xs transition-opacity"
				@click.self="selectedDetailTrip = null"
			>
				<div class="w-full sm:max-w-lg bg-white rounded-t-3xl sm:rounded-3xl shadow-2xl border border-slate-200 max-h-[90vh] flex flex-col overflow-hidden animate-in slide-in-from-bottom duration-200">
					
					<!-- Modal Header -->
					<div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
						<div>
							<div class="flex items-center gap-2">
								<h3 class="text-sm font-bold text-slate-900">
									{{ selectedDetailTrip.employee_name || selectedDetailTrip.employee }}
								</h3>
								<span
									class="px-2 py-0.5 rounded-full text-[10px] font-bold"
									:class="getStatusBadgeClass(selectedDetailTrip.trip_status)"
								>
									{{ getStatusLabel(selectedDetailTrip.trip_status) }}
								</span>
							</div>
							<p class="text-[11px] text-slate-500 mt-0.5">
								{{ selectedDetailTrip.name }} • {{ selectedDetailTrip.date }}
							</p>
						</div>

						<button
							@click="selectedDetailTrip = null"
							class="p-2 rounded-full hover:bg-slate-200 text-slate-500 transition cursor-pointer"
						>
							<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</div>

					<!-- Modal Scrollable Body -->
					<div class="p-5 overflow-y-auto space-y-4 text-xs">
						
						<!-- Key Metrics Grid -->
						<div class="grid grid-cols-2 gap-2.5">
							<div class="bg-slate-50 p-3 rounded-2xl border border-slate-200/80">
								<span class="text-[10px] font-semibold text-slate-400 uppercase">Travel Distance</span>
								<div class="text-base font-black text-slate-800 mt-1">
									{{ formatNumber(selectedDetailTrip.total_distance) }} KM
								</div>
								<div class="text-[10px] text-slate-500 mt-0.5">
									Odo: {{ selectedDetailTrip.start_odometerkm }} ➔ {{ selectedDetailTrip.end_odometerkm || '-' }}
								</div>
							</div>

							<div class="bg-slate-50 p-3 rounded-2xl border border-slate-200/80">
								<span class="text-[10px] font-semibold text-slate-400 uppercase">Total Claim</span>
								<div class="text-base font-black text-teal-700 mt-1">
									₹{{ formatCurrency(selectedDetailTrip.total_expense) }}
								</div>
								<div class="text-[10px] text-slate-500 mt-0.5">
									Vehicle: {{ selectedDetailTrip.vehicle_type || '2 Wheeler' }}
								</div>
							</div>
						</div>

						<!-- Time & Remarks -->
						<div class="bg-slate-50 p-3.5 rounded-2xl border border-slate-200/80 space-y-2">
							<div class="flex justify-between items-center text-slate-600">
								<span class="font-semibold text-slate-500">Trip Timing:</span>
								<span class="font-bold text-slate-800">
									{{ formatTimeOnly(selectedDetailTrip.start_time) }}
									<span v-if="selectedDetailTrip.end_time && selectedDetailTrip.trip_status !== 'IN_PROGRESS'" class="text-slate-400"> ➔ {{ formatTimeOnly(selectedDetailTrip.end_time) }}</span>
									<span v-else class="text-emerald-600 font-bold ml-1">(Ongoing)</span>
								</span>
							</div>
							<div v-if="selectedDetailTrip.remarks" class="text-slate-600 border-t border-slate-200 pt-2">
								<span class="font-semibold text-slate-500">Start Remarks:</span>
								<p class="text-slate-700 mt-0.5">{{ selectedDetailTrip.remarks }}</p>
							</div>
							<div v-if="selectedDetailTrip.end_narration" class="text-slate-600 border-t border-slate-200 pt-2">
								<span class="font-semibold text-slate-500">End Narration:</span>
								<p class="text-slate-700 mt-0.5">{{ selectedDetailTrip.end_narration }}</p>
							</div>
						</div>

						<!-- Customer Site Visits Timeline -->
						<div class="space-y-2">
							<div class="flex items-center justify-between">
								<h4 class="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
									<span>Customer Visits Timeline</span>
									<span class="px-2 py-0.5 rounded-full bg-teal-100 text-teal-800 text-[10px] font-bold">
										{{ selectedDetailTrip.employee_site_tracking?.length || 0 }}
									</span>
								</h4>
							</div>

							<div
								v-if="!selectedDetailTrip.employee_site_tracking || selectedDetailTrip.employee_site_tracking.length === 0"
								class="text-center py-4 bg-slate-50 rounded-2xl border border-slate-200 text-slate-400"
							>
								No site visits logged during this trip.
							</div>

							<div v-else class="space-y-2.5">
								<div
									v-for="(st, idx) in selectedDetailTrip.employee_site_tracking"
									:key="st.name || idx"
									class="bg-white border border-slate-200/90 rounded-2xl p-3 shadow-2xs space-y-1.5"
								>
									<div class="flex items-start justify-between gap-2">
										<div class="flex items-center gap-2">
											<span class="w-5 h-5 rounded-full bg-teal-600 text-white text-[10px] font-black flex items-center justify-center shrink-0">
												{{ idx + 1 }}
											</span>
											<div>
												<h5 class="text-xs font-bold text-slate-900">{{ st.customer }}</h5>
												<div class="flex items-center gap-1.5 mt-0.5">
													<span v-if="st.category" class="px-1.5 py-0.2 rounded bg-teal-50 text-teal-800 font-bold text-[9px] border border-teal-200">
														{{ st.category }}
													</span>
													<p v-if="st.site" class="text-[10px] text-slate-500 font-medium truncate max-w-[150px]">{{ st.site }}</p>
												</div>
											</div>
										</div>

										<div class="text-right shrink-0 space-y-0.5">
											<span class="text-[10px] font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded-lg block">
												{{ formatTimeOnly(st.checkin_time) }}
											</span>
											<div class="flex flex-col items-end gap-0.5 mt-0.5">
												<span
													v-if="st.actual_distance !== undefined && st.actual_distance !== null"
													class="text-[9.5px] font-mono font-bold text-teal-800 bg-teal-50 px-1.5 py-0.2 rounded border border-teal-200 block"
													title="Actual Distance entered by Salesperson"
												>
													<span class="text-[8px] text-teal-600 font-semibold uppercase">Act: </span>{{ st.actual_distance }} km
												</span>
												<span
													v-if="st.distance_travelled !== undefined && st.distance_travelled !== null"
													class="text-[9px] font-mono font-medium text-slate-600 bg-slate-100 px-1.5 py-0.2 rounded border border-slate-200 block"
													title="GPS Distance calculated by server"
												>
													<span class="text-[8px] text-slate-400 uppercase">GPS: </span>{{ st.distance_travelled }} km
												</span>
											</div>
										</div>
									</div>

									<div v-if="st.contact_number || st.address" class="space-y-0.5 text-[10px] pl-7">
										<div v-if="st.contact_number" class="flex items-center space-x-1 text-slate-700 font-mono">
											<span>📞</span>
											<a :href="'tel:' + st.contact_number" class="text-teal-700 font-bold hover:underline">{{ st.contact_number }}</a>
										</div>
										<div v-if="st.address" class="flex items-start space-x-1 text-slate-500">
											<span>📍</span>
											<span class="truncate">{{ st.address }}</span>
										</div>
									</div>

									<p v-if="st.remarks" class="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-xl border border-slate-100">
										{{ st.remarks }}
									</p>

									<div v-if="st.site_lat && st.site_long" class="flex items-center justify-between pt-1">
										<span class="inline-flex items-center space-x-1 text-[9px] font-bold bg-teal-50 text-teal-700 px-2 py-0.5 rounded-md border border-teal-200/80">
											<span>📍</span>
											<span>Location Captured</span>
										</span>
										<a
											:href="getMapUrl(st.site_lat, st.site_long)"
											target="_blank"
											class="text-[10px] font-bold text-teal-600 hover:underline flex items-center gap-0.5"
										>
											<span>Google Maps ↗</span>
										</a>
									</div>
								</div>
							</div>
						</div>

						<!-- Expense Claim Breakdown -->
						<div class="space-y-2">
							<div class="flex items-center justify-between">
								<h4 class="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
									<span>Expense Claim Breakdown</span>
								</h4>
								<span class="text-xs font-black text-teal-800 bg-teal-50 px-2 py-0.5 rounded-lg border border-teal-200">
									Total: ₹{{ formatCurrency(selectedDetailTrip.total_expense) }}
								</span>
							</div>

							<div class="bg-white border border-slate-200 rounded-2xl p-3 shadow-2xs space-y-2.5">
								<!-- 1. Travel Distance Calculation Item -->
								<div class="flex items-start justify-between gap-2 pb-2 border-b border-slate-100">
									<div>
										<div class="text-xs font-bold text-slate-800 flex items-center gap-1">
											<span>🚗 Travel Allowance</span>
											<span class="text-[10px] font-semibold text-slate-400">({{ selectedDetailTrip.vehicle_type || '2 Wheeler' }})</span>
										</div>
										<div class="text-[10px] text-slate-500 mt-0.5">
											{{ formatNumber(selectedDetailTrip.total_distance) }} KM × ₹{{ formatCurrency(selectedDetailTrip.rate_per_km || 0) }}/km
										</div>
									</div>
									<div class="text-xs font-black text-slate-800 shrink-0">
										₹{{ formatCurrency(selectedDetailTrip.total_travel_expense || (selectedDetailTrip.total_distance * (selectedDetailTrip.rate_per_km || 0))) }}
									</div>
								</div>

								<!-- 2. Other Itemized Expenses if any -->
								<template v-if="selectedDetailTrip.employee_expense_tracking && selectedDetailTrip.employee_expense_tracking.length > 0">
									<div
										v-for="(exp, expIdx) in selectedDetailTrip.employee_expense_tracking"
										:key="exp.name || expIdx"
										class="flex items-start justify-between gap-2 pt-0.5"
									>
										<div>
											<div class="text-xs font-bold text-slate-800 flex items-center gap-1">
												<span>💳 {{ exp.expense_type }}</span>
											</div>
											<div v-if="exp.description" class="text-[10px] text-slate-400 mt-0.5">
												{{ exp.description }}
											</div>
										</div>
										<div class="text-xs font-black text-slate-800 shrink-0">
											₹{{ formatCurrency(exp.amount) }}
										</div>
									</div>
								</template>

								<!-- 3. Summary Total Row -->
								<div class="flex items-center justify-between pt-2 border-t border-slate-100 bg-slate-50 -mx-3 -mb-3 p-3 rounded-b-2xl">
									<span class="text-xs font-bold text-slate-700">Total Claimable Amount</span>
									<span class="text-sm font-black text-teal-800">₹{{ formatCurrency(selectedDetailTrip.total_expense) }}</span>
								</div>
							</div>
						</div>

					</div>

					<!-- Modal Footer -->
					<div class="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
						<button
							@click="selectedDetailTrip = null"
							class="w-full py-2.5 bg-teal-700 hover:bg-teal-800 text-white rounded-xl font-bold text-xs transition cursor-pointer shadow-xs"
						>
							Close
						</button>
					</div>

				</div>
			</div>

		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { employeeResource } from "@/data/employee"
import { supervisorEemDashboardResource, supervisorTeamTripDetailResource } from "@/data/eem"

const router = useRouter()
const employee = computed(() => employeeResource.data)

// State
const targetDate = ref(getTodayISO())
const selectedDateMode = ref("today")
const selectedSalesPerson = ref("all")
const selectedStatus = ref("all")
const isDatePickerOpen = ref(false)
const isMemberDropdownOpen = ref(false)
const memberSearchQuery = ref("")
const selectedDetailTrip = ref(null)

const isLoading = computed(() => supervisorEemDashboardResource.loading)
const dashboardData = computed(() => supervisorEemDashboardResource.data)

const teamMembers = computed(() => dashboardData.value?.team_members || [])
const tripsList = computed(() => dashboardData.value?.trips || [])

const selectedMemberObj = computed(() => {
	if (selectedSalesPerson.value === "all") return null
	return teamMembers.value.find(
		(m) => m.sales_person === selectedSalesPerson.value || m.employee === selectedSalesPerson.value
	)
})

const filteredTeamMembers = computed(() => {
	const list = teamMembers.value || []
	const q = memberSearchQuery.value.toLowerCase().trim()
	if (!q) return list
	return list.filter((m) => {
		const name = (m.sales_person_name || "").toLowerCase()
		const empName = (m.employee_name || "").toLowerCase()
		const empId = (m.employee || "").toLowerCase()
		const desig = (m.designation || "").toLowerCase()
		return name.includes(q) || empName.includes(q) || empId.includes(q) || desig.includes(q)
	})
})

function selectMemberAndClose(sp) {
	selectedSalesPerson.value = sp
	isMemberDropdownOpen.value = false
	memberSearchQuery.value = ""
	fetchDashboardData()
}

const isCustomDate = computed(() => {
	return targetDate.value !== getTodayISO()
})

const isToday = computed(() => targetDate.value === getTodayISO())
const isYesterday = computed(() => targetDate.value === getYesterdayISO())

const formattedDateDisplay = computed(() => {
	if (!targetDate.value) return ""
	const d = new Date(targetDate.value)
	return d.toLocaleDateString("en-IN", {
		weekday: "short",
		month: "short",
		day: "numeric",
		year: "numeric",
	})
})

const filteredTrips = computed(() => {
	let list = tripsList.value || []
	if (selectedStatus.value !== "all") {
		if (selectedStatus.value === "ACTIVE") {
			list = list.filter((t) => t.trip_status === "IN_PROGRESS")
		} else if (selectedStatus.value === "COMPLETED") {
			list = list.filter((t) => t.trip_status === "COMPLETED" || t.trip_status === "READY_TO_SUBMIT")
		} else if (selectedStatus.value === "NOT_STARTED") {
			list = list.filter((t) => t.trip_status === "NOT_STARTED")
		}
	}
	return list
})

function getTodayISO() {
	const now = new Date()
	const year = now.getFullYear()
	const month = String(now.getMonth() + 1).padStart(2, "0")
	const day = String(now.getDate()).padStart(2, "0")
	return `${year}-${month}-${day}`
}

function getYesterdayISO() {
	const now = new Date()
	now.setDate(now.getDate() - 1)
	const year = now.getFullYear()
	const month = String(now.getMonth() + 1).padStart(2, "0")
	const day = String(now.getDate()).padStart(2, "0")
	return `${year}-${month}-${day}`
}

function setDate(mode) {
	selectedDateMode.value = mode
	if (mode === "today") {
		targetDate.value = getTodayISO()
	} else if (mode === "yesterday") {
		targetDate.value = getYesterdayISO()
	}
	fetchDashboardData()
}

function onCustomDateChange() {
	if (targetDate.value === getTodayISO()) {
		selectedDateMode.value = "today"
	} else if (targetDate.value === getYesterdayISO()) {
		selectedDateMode.value = "yesterday"
	} else {
		selectedDateMode.value = "custom"
	}
	fetchDashboardData()
}

function filterBySalesPerson(sp) {
	selectedSalesPerson.value = sp
	fetchDashboardData()
}

function filterByStatus(status) {
	selectedStatus.value = status
}

function fetchDashboardData() {
	supervisorEemDashboardResource.fetch({
		date: targetDate.value,
		sales_person: selectedSalesPerson.value !== "all" ? selectedSalesPerson.value : null,
	})
}

async function viewTripDetail(eemName) {
	if (!eemName) return
	try {
		const res = await supervisorTeamTripDetailResource.fetch({
			eem_name: eemName,
		})
		selectedDetailTrip.value = res
	} catch (e) {
		console.error("Failed to fetch trip detail:", e)
	}
}

function goBack() {
	if (window.history.length > 1) {
		router.back()
	} else {
		router.push("/eem")
	}
}

function getFirstName(fullName) {
	if (!fullName) return "Rep"
	return fullName.split(" ")[0]
}

function formatNumber(val) {
	if (val === null || val === undefined) return "0"
	return Number(val).toLocaleString("en-IN", { maximumFractionDigits: 1 })
}

function formatCurrency(val) {
	if (val === null || val === undefined) return "0"
	return Number(val).toLocaleString("en-IN", { maximumFractionDigits: 2 })
}

function formatTimeOnly(timeStr) {
	if (!timeStr) return "-"
	try {
		const d = new Date(timeStr)
		if (isNaN(d.getTime())) {
			return timeStr.slice(0, 5)
		}
		return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })
	} catch (e) {
		return timeStr
	}
}

function formatDateTime(timeStr) {
	if (!timeStr) return "-"
	try {
		const d = new Date(timeStr)
		if (isNaN(d.getTime())) return timeStr
		return d.toLocaleString("en-IN", {
			month: "short",
			day: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		})
	} catch (e) {
		return timeStr
	}
}

function getStatusLabel(status) {
	switch (status) {
		case "IN_PROGRESS":
			return isToday.value ? "On Trip" : "Active"
		case "COMPLETED":
			return "Done"
		case "READY_TO_SUBMIT":
			return "Trip Ended"
		case "NOT_STARTED":
			return isToday.value ? "Pending" : "No Travel"
		default:
			return status || "Unknown"
	}
}

function getStatusBadgeClass(status) {
	switch (status) {
		case "IN_PROGRESS":
			return "bg-emerald-100 text-emerald-800 border border-emerald-200"
		case "COMPLETED":
			return "bg-blue-100 text-blue-800 border border-blue-200"
		case "READY_TO_SUBMIT":
			return "bg-amber-100 text-amber-800 border border-amber-200"
		case "NOT_STARTED":
			return "bg-slate-100 text-slate-600 border border-slate-200"
		default:
			return "bg-slate-100 text-slate-600"
	}
}

function getStatusDotClass(status) {
	switch (status) {
		case "IN_PROGRESS":
			return "bg-emerald-500"
		case "COMPLETED":
			return "bg-blue-500"
		case "READY_TO_SUBMIT":
			return "bg-amber-500"
		case "NOT_STARTED":
			return "bg-slate-300"
		default:
			return "bg-slate-300"
	}
}

function getMapUrl(lat, lng) {
	return `https://www.google.com/maps?q=${lat},${lng}`
}

onMounted(() => {
	fetchDashboardData()
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
