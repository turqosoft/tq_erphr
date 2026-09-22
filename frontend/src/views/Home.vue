<template>
	<div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-start items-center p-0 sm:p-4 font-sans selection:bg-teal-500 selection:text-white relative overflow-x-hidden pb-24">
		<!-- Subtle Background ambient glow for desktop container view -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-emerald-200/20 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full sm:max-w-md bg-[#f8fafc] min-h-screen sm:min-h-[720px] sm:rounded-3xl sm:shadow-2xl sm:border sm:border-slate-200/80 flex flex-col justify-between relative z-10 overflow-hidden pb-6">
			
			<!-- Mobile Top App Header (Fixed at top like BottomNavBar) -->
			<header class="fixed top-0 inset-x-0 z-40 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 shadow-[0_2px_16px_rgba(0,0,0,0.04)] px-3 py-2.5 sm:px-4">
				<div class="max-w-md mx-auto flex items-center justify-between">
					<!-- Company Logo & Name -->
					<div class="flex items-center space-x-2.5 min-w-0 flex-1 mr-2">
						<div class="w-9 h-9 rounded-2xl bg-white p-1 flex items-center justify-center shadow-md shadow-teal-600/10 border border-slate-100 ring-2 ring-teal-50 overflow-hidden flex-shrink-0">
							<img
								v-if="employee?.company_logo || employee?.app_logo"
								:src="employee.company_logo || employee.app_logo"
								:alt="employee?.company_name || 'Company Logo'"
								class="w-full h-full object-contain"
							/>
							<img
								v-else
								:src="mobibizIcon"
								alt="MobiBiz"
								class="w-full h-full object-contain"
							/>
						</div>
						<div class="min-w-0 flex-1">
							<h1 class="text-sm font-bold text-slate-900 leading-tight flex items-center gap-1.5 truncate">
								<span class="truncate">{{ employee?.company_name || employee?.company || 'Total Quality' }}</span>
								<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse flex-shrink-0" title="Connected"></span>
							</h1>
							<p class="text-[10px] font-medium text-slate-500 leading-none truncate mt-0.5">MobiBiz Lite • Employee Portal</p>
						</div>
					</div>

					<!-- Header Actions -->
					<div class="flex items-center space-x-2">
						<!-- Refresh Button -->
						<button
							@click="refreshData"
							:disabled="employeeResource.loading || checkinStatusResource.loading || todayEemResource.loading"
							class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
							title="Refresh data"
						>
							<svg
								class="w-4 h-4"
								:class="{ 'animate-spin text-teal-600': employeeResource.loading || checkinStatusResource.loading || todayEemResource.loading }"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
							</svg>
						</button>

						<!-- Profile Dropdown Trigger -->
						<div class="relative" ref="profileDropdownRef">
							<button
								@click="toggleDropdown"
								class="flex items-center p-0.5 rounded-full hover:ring-2 hover:ring-teal-400/50 active:scale-95 transition focus:outline-none cursor-pointer"
								title="Account & Profile"
								aria-label="User profile menu"
							>
								<div class="w-8 h-8 rounded-full bg-gradient-to-tr from-teal-600 to-teal-400 text-white font-bold text-xs flex items-center justify-center shadow-sm overflow-hidden ring-2 ring-white">
									<img
										v-if="employee?.image"
										:src="employee.image"
										:alt="employee.employee_name"
										class="w-full h-full object-cover"
									/>
									<span v-else>{{ getInitials(employee?.employee_name || session.user) }}</span>
								</div>
							</button>

							<!-- Profile Dropdown Menu Card -->
							<transition
								enter-active-class="transition duration-150 ease-out"
								enter-from-class="transform scale-95 opacity-0"
								enter-to-class="transform scale-100 opacity-100"
								leave-active-class="transition duration-100 ease-in"
								leave-from-class="transform scale-100 opacity-100"
								leave-to-class="transform scale-95 opacity-0"
							>
								<div
									v-if="isDropdownOpen"
									class="absolute right-0 mt-2 w-64 bg-white rounded-3xl shadow-2xl border border-slate-200/90 py-1.5 z-50 overflow-hidden"
								>
									<!-- User Summary Header -->
									<div class="px-4 py-3.5 border-b border-slate-100 bg-slate-50/50">
										<div class="flex items-center space-x-2.5">
											<div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-teal-400 text-white font-bold text-xs flex items-center justify-center flex-shrink-0 shadow-sm overflow-hidden">
												<img
													v-if="employee?.image"
													:src="employee.image"
													:alt="employee.employee_name"
													class="w-full h-full object-cover"
												/>
												<span v-else>{{ getInitials(employee?.employee_name || session.user) }}</span>
											</div>
											<div class="min-w-0 flex-1">
												<p class="text-xs font-bold text-slate-900 truncate">
													{{ employee?.employee_name || session.user }}
												</p>
												<p class="text-[10px] text-slate-500 truncate">
													{{ employee?.company_email || employee?.user_id || session.user }}
												</p>
												<span class="inline-flex items-center px-1.5 py-0.2 mt-1 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
													{{ employee?.designation || 'Employee' }}
												</span>
											</div>
										</div>
									</div>

									<!-- Action Items -->
									<div class="px-1.5 py-1.5 space-y-0.5">
										<!-- View Profile Option -->
										<button
											@click="openProfileModal"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-teal-50 hover:text-teal-800 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
											</svg>
											<span>Profile Details</span>
										</button>

										<!-- Checkin History Option -->
										<button
											@click="openHistoryModal"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-teal-50 hover:text-teal-800 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											<span>Check-in Logs</span>
										</button>

										<!-- Expense Manager (EEM) Option (Visible only for Sales Persons) -->
										<button
											v-if="employee?.is_sales_person"
											@click="goToEem"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-teal-50 hover:text-teal-800 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
											</svg>
											<span>Expense Manager (EEM)</span>
										</button>

										<!-- EEM Trip History Option (Visible only for Sales Persons) -->
										<button
											v-if="employee?.is_sales_person"
											@click="goToEemHistory"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-teal-50 hover:text-teal-800 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
											</svg>
											<span>EEM Trip History</span>
										</button>

										<!-- Supervisor Team EEM Option (Visible only for Supervisors) -->
										<button
											v-if="employee?.is_supervisor"
											@click="goToSupervisorEem"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-semibold text-teal-800 bg-teal-50/70 hover:bg-teal-100 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-teal-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
											</svg>
											<span>Supervisor Team EEM</span>
										</button>

										<!-- Customers Directory Option -->
										<button
											@click="goToCustomers"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-teal-50 hover:text-teal-800 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
											</svg>
											<span>Customers Directory</span>
										</button>

										<!-- Stock & Inventory Option -->
										<button
											@click="goToStock"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-teal-50 hover:text-teal-800 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
											</svg>
											<span>Stock & Inventory</span>
										</button>

										<!-- Install MobiBiz App Option -->
										<button
											v-if="!pwaState.isInstalled"
											@click="handlePwaInstall"
											class="w-full flex items-center justify-between px-3 py-2 rounded-2xl text-xs font-semibold text-teal-800 bg-teal-50/90 hover:bg-teal-100 border border-teal-200/70 transition text-left active:scale-98 shadow-xs"
										>
											<div class="flex items-center space-x-2.5">
												<svg class="w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
												</svg>
												<span>Install MobiBiz App</span>
											</div>
											<span class="text-[9px] font-bold bg-teal-600 text-white px-1.5 py-0.5 rounded-full uppercase tracking-wider">Install</span>
										</button>

										<!-- Change Password Option -->
										<button
											@click="openChangePasswordModal"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-teal-50 hover:text-teal-800 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
											</svg>
											<span>Change Password</span>
										</button>

										<!-- Logout Option -->
										<button
											@click="promptLogout"
											class="w-full flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-rose-600 hover:bg-rose-50 hover:text-rose-700 transition text-left active:scale-98"
										>
											<svg class="w-4 h-4 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
											</svg>
											<span>Log out</span>
										</button>
									</div>
								</div>
							</transition>
						</div>
					</div>
				</div>
			</header>

			<!-- Main Content Scrollable Area -->
			<main class="flex-1 w-full px-4 pt-16 sm:pt-16 pb-4 space-y-4">
				<!-- Loading State -->
				<div v-if="employeeResource.loading && !employee" class="p-8 text-center bg-white rounded-3xl shadow-sm border border-slate-100 my-6">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent mb-3"></div>
					<h3 class="text-sm font-bold text-slate-900">Loading Profile...</h3>
					<p class="text-xs text-slate-500 mt-0.5">Fetching employee records</p>
				</div>

				<!-- Linked Employee Found: Mobile App View -->
				<div v-else-if="employee" class="space-y-4">
					<!-- ========================================== -->
					<!-- HERO GREETING CARD WITH STATS RIBBON       -->
					<!-- ========================================== -->
					<div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-teal-600 via-teal-500 to-teal-400 text-white p-5 shadow-lg shadow-teal-600/20">
						<!-- Ambient Glass Orbs -->
						<div class="absolute -right-10 -bottom-10 w-44 h-44 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>
						<div class="absolute top-0 right-1/4 w-28 h-28 bg-teal-400/20 rounded-full blur-xl pointer-events-none"></div>

						<div class="relative z-10 space-y-4">
							<!-- Profile & Greeting Header -->
							<div class="flex items-center space-x-3.5">
								<!-- Employee Avatar -->
								<div class="w-14 h-14 rounded-2xl bg-white/20 backdrop-blur-md ring-2 ring-white/30 flex items-center justify-center overflow-hidden flex-shrink-0 shadow-md">
									<img
										v-if="employee.image"
										:src="employee.image"
										:alt="employee.employee_name"
										class="w-full h-full object-cover"
									/>
									<span v-else class="text-xl font-black text-white">
										{{ getInitials(employee.employee_name) }}
									</span>
								</div>

								<!-- Greeting and Employee Name -->
								<div class="flex-1 min-w-0">
									<div class="flex items-center space-x-2">
										<span class="text-[10px] uppercase tracking-wider font-bold text-teal-100">
											{{ timeGreeting }}
										</span>
										<!-- Status Badge -->
										<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-400/20 text-emerald-100 border border-emerald-300/30">
											{{ employee.status || 'Active' }}
										</span>
									</div>
									<h2 class="text-lg font-black tracking-tight text-white mt-0.5 truncate">
										{{ employee.employee_name }}
									</h2>
									<p class="text-xs text-teal-100/90 font-medium truncate">
										{{ employee.designation || 'Team Member' }}
										<span v-if="employee.department"> • {{ employee.department }}</span>
									</p>
								</div>
							</div>

							<!-- Embedded Stats Ribbon (3-Column if Sales Person, 2-Column if non-sales) -->
							<div v-if="employee?.is_sales_person" class="grid grid-cols-3 gap-2 pt-3 border-t border-white/15 text-center">
								<!-- Stat 1: First Punch IN -->
								<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
									<span class="text-[9px] font-medium text-teal-100 uppercase tracking-wider block">First In</span>
									<span class="text-xs font-black text-white font-mono mt-0.5 block truncate">
										{{ firstPunchInTime }}
									</span>
								</div>

								<!-- Stat 2: Site Visits -->
								<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
									<span class="text-[9px] font-medium text-teal-100 uppercase tracking-wider block">Sites</span>
									<span class="text-xs font-black text-white font-mono mt-0.5 block truncate">
										{{ todayEemSiteVisitsCount }} {{ todayEemSiteVisitsCount === 1 ? 'Visit' : 'Visits' }}
									</span>
								</div>

								<!-- Stat 3: Today's Claim Expense -->
								<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
									<span class="text-[9px] font-medium text-teal-100 uppercase tracking-wider block">Claim</span>
									<span class="text-xs font-black text-white font-mono mt-0.5 block truncate">
										₹{{ formatAmount(todayEemDoc?.total_expense ?? todayEemExpensesSum ?? 0) }}
									</span>
								</div>
							</div>

							<div v-else class="grid grid-cols-2 gap-2 pt-3 border-t border-white/15 text-center">
								<!-- Stat 1: First Punch IN -->
								<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
									<span class="text-[9px] font-medium text-teal-100 uppercase tracking-wider block">First In</span>
									<span class="text-xs font-black text-white font-mono mt-0.5 block truncate">
										{{ firstPunchInTime }}
									</span>
								</div>

								<!-- Stat 2: Today's Punches -->
								<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
									<span class="text-[9px] font-medium text-teal-100 uppercase tracking-wider block">Today Logs</span>
									<span class="text-xs font-black text-white font-mono mt-0.5 block truncate">
										{{ todayCheckinLogs.length }} {{ todayCheckinLogs.length === 1 ? 'Punch' : 'Punches' }}
									</span>
								</div>
							</div>
						</div>
					</div>

					<!-- ========================================== -->
					<!-- CHECK-IN / CHECK-OUT INTERACTIVE CARD     -->
					<!-- ========================================== -->
					<div class="bg-white rounded-3xl p-4 sm:p-5 shadow-sm border border-slate-100 space-y-4 relative overflow-hidden">
						<!-- Card Top Header: Clock & Current Status -->
						<div class="flex items-start justify-between">
							<div>
								<div class="flex items-center space-x-1.5">
									<span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{{ liveDateFormatted }}</span>
								</div>
								<div class="text-2xl font-black tracking-tight text-slate-900 font-mono mt-0.5 flex items-baseline gap-1">
									<span>{{ liveTimeFormatted }}</span>
								</div>
							</div>

							<!-- Status Pill -->
							<div class="flex flex-col items-end">
								<span
									v-if="isCheckedIn"
									class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200/80 shadow-xs"
								>
									<span class="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
									Checked In
								</span>
								<span
									v-else
									class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600 border border-slate-200 shadow-xs"
								>
									<span class="w-2 h-2 rounded-full bg-slate-400 mr-1.5"></span>
									Checked Out
								</span>
								<span class="text-[10px] text-slate-400 mt-1 font-medium">
									{{ lastPunchSummary }}
								</span>
							</div>
						</div>

						<!-- Punch Action Button -->
						<div class="pt-1">
							<button
								@click="promptPunchConfirmation"
								:disabled="isSubmittingCheckin"
								class="w-full relative py-3.5 px-4 rounded-2xl font-bold text-sm flex items-center justify-center space-x-2.5 transition-all transform active:scale-[0.98] focus:outline-none shadow-md"
								:class="[
									nextAction === 'IN'
										? 'bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white shadow-teal-600/25'
										: 'bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white shadow-amber-500/25',
									isSubmittingCheckin ? 'opacity-80 cursor-wait' : ''
								]"
							>
								<!-- Spinner if submitting -->
								<svg
									v-if="isSubmittingCheckin"
									class="animate-spin h-5 w-5 text-white"
									fill="none"
									viewBox="0 0 24 24"
								>
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>

								<!-- Punch IN Icon -->
								<svg
									v-else-if="nextAction === 'IN'"
									class="w-5 h-5"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
								</svg>

								<!-- Punch OUT Icon -->
								<svg
									v-else
									class="w-5 h-5"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
								</svg>

								<span>
									{{ isSubmittingCheckin ? (nextAction === 'IN' ? 'Recording Check In...' : 'Recording Check Out...') : (nextAction === 'IN' ? 'Check In Now' : 'Check Out Now') }}
								</span>
							</button>

							<!-- Geolocation / Device Status Info -->
							<div class="mt-3 pt-2.5 border-t border-slate-100 flex flex-col space-y-1.5 text-[11px] text-slate-500">
								<!-- Device captured badge -->
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-1.5 truncate max-w-[240px]">
										<svg class="w-3.5 h-3.5 text-teal-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
										</svg>
										<span class="truncate font-medium text-slate-700">{{ deviceLabel }}</span>
									</div>
									<span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-slate-100 text-slate-600 uppercase">
										{{ detectedDevice?.appMode || 'Web' }}
									</span>
								</div>

								<!-- Geolocation & History Link -->
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-1.5 truncate max-w-[220px]">
										<svg class="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
										</svg>
										<span class="truncate">{{ locationStatusText }}</span>
									</div>

									<button
										type="button"
										@click="toggleTodayPunches"
										class="text-teal-700 hover:text-teal-800 font-bold hover:underline flex-shrink-0 flex items-center space-x-1 cursor-pointer"
									>
										<span>{{ isPunchesExpanded ? 'Hide Logs' : "Today's Logs" }}</span>
										<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': isPunchesExpanded }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
										</svg>
									</button>
								</div>
							</div>
						</div>

						<!-- Today's Punches Collapsible Timeline -->
						<div v-if="isPunchesExpanded" class="pt-2 border-t border-slate-100">
							<div class="flex items-center justify-between mb-2">
								<span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Today's Attendance</span>
								<span class="text-[10px] text-slate-400 font-medium">{{ todayCheckins.length }} {{ todayCheckins.length === 1 ? 'record' : 'records' }}</span>
							</div>

							<div v-if="todayCheckins.length > 0" class="space-y-1.5 max-h-36 overflow-y-auto pr-1">
								<div
									v-for="log in todayCheckins"
									:key="log.name"
									class="flex items-center justify-between px-3 py-2 rounded-2xl bg-slate-50 border border-slate-100 text-xs"
								>
									<div class="flex items-center space-x-2">
										<span
											class="px-2 py-0.5 rounded-lg text-[10px] font-bold"
											:class="log.log_type === 'IN' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
										>
											{{ log.log_type }}
										</span>
										<span class="font-bold text-slate-800">{{ formatLogTime(log.time) }}</span>
									</div>
									<span class="text-[10px] text-slate-400 font-mono">{{ log.device_id || 'PWA' }}</span>
								</div>
							</div>

							<!-- No checkins yet placeholder -->
							<div v-else class="text-center py-2 text-[11px] text-slate-400 italic">
								No check-in entries logged yet today.
							</div>
						</div>
					</div>

					<!-- ========================================== -->
					<!-- QUICK SERVICES & ACTIONS GRID              -->
					<!-- ========================================== -->
					<div class="space-y-2">
						<div class="flex items-center justify-between px-1">
							<span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Quick Services</span>
							<span class="text-[10px] text-teal-600 font-medium">Shortcuts</span>
						</div>

						<!-- Grid for Sales Persons (Site & Trip + Customers + Stock) -->
						<div v-if="employee?.is_sales_person" class="grid grid-cols-3 gap-2">
							<!-- Tile 1: Field Visits & Expenses -->
							<button
								@click="goToEem"
								class="bg-white p-3 rounded-3xl border border-slate-100 shadow-xs hover:border-teal-200 hover:shadow-sm transition-all active:scale-[0.98] text-left flex flex-col justify-between space-y-2.5 cursor-pointer"
							>
								<div class="w-8 h-8 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center border border-teal-100">
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
									</svg>
								</div>
								<div>
									<h4 class="text-xs font-bold text-slate-900 leading-tight">Site & Trip</h4>
									<p class="text-[9px] text-slate-500 mt-0.5 leading-tight truncate">Visits & Claims</p>
								</div>
							</button>

							<!-- Tile 2: Customers Directory -->
							<button
								@click="goToCustomers"
								class="bg-white p-3 rounded-3xl border border-slate-100 shadow-xs hover:border-teal-200 hover:shadow-sm transition-all active:scale-[0.98] text-left flex flex-col justify-between space-y-2.5 cursor-pointer"
							>
								<div class="w-8 h-8 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center border border-cyan-100">
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
									</svg>
								</div>
								<div>
									<h4 class="text-xs font-bold text-slate-900 leading-tight">Customers</h4>
									<p class="text-[9px] text-slate-500 mt-0.5 leading-tight truncate">Directory & GPS</p>
								</div>
							</button>

							<!-- Tile 3: Stock & Inventory -->
							<button
								@click="goToStock"
								class="bg-white p-3 rounded-3xl border border-slate-100 shadow-xs hover:border-teal-200 hover:shadow-sm transition-all active:scale-[0.98] text-left flex flex-col justify-between space-y-2.5 cursor-pointer"
							>
								<div class="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center border border-emerald-100">
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
									</svg>
								</div>
								<div>
									<h4 class="text-xs font-bold text-slate-900 leading-tight">Stock Details</h4>
									<p class="text-[9px] text-slate-500 mt-0.5 leading-tight truncate">Live Balances</p>
								</div>
							</button>
						</div>

						<!-- Grid for Non-Sales Staff (Customers + Stock) -->
						<div v-else class="grid grid-cols-2 gap-2.5">
							<!-- Tile 1: Customers Directory -->
							<button
								@click="goToCustomers"
								class="bg-white p-3.5 rounded-3xl border border-slate-100 shadow-xs hover:border-teal-200 hover:shadow-sm transition-all active:scale-[0.98] text-left flex flex-col justify-between space-y-3 cursor-pointer"
							>
								<div class="w-8 h-8 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center border border-cyan-100">
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
									</svg>
								</div>
								<div>
									<h4 class="text-xs font-bold text-slate-900">Customers</h4>
									<p class="text-[10px] text-slate-500 mt-0.5">Directory & Locations</p>
								</div>
							</button>

							<!-- Tile 2: Stock & Inventory -->
							<button
								@click="goToStock"
								class="bg-white p-3.5 rounded-3xl border border-slate-100 shadow-xs hover:border-teal-200 hover:shadow-sm transition-all active:scale-[0.98] text-left flex flex-col justify-between space-y-3 cursor-pointer"
							>
								<div class="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center border border-emerald-100">
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
									</svg>
								</div>
								<div>
									<h4 class="text-xs font-bold text-slate-900">Stock Details</h4>
									<p class="text-[10px] text-slate-500 mt-0.5">Live Balances</p>
								</div>
							</button>
						</div>
					</div>

					<!-- ======================================================= -->
					<!-- FIELD TRAVEL & EXPENSE MANAGER (EEM) CARD - SALES ONLY  -->
					<!-- ======================================================= -->
					<div v-if="employee?.is_sales_person" class="bg-white rounded-3xl p-4 sm:p-5 shadow-sm border border-slate-100 space-y-3.5 relative overflow-hidden">
						<!-- Card Header -->
						<div class="flex items-center justify-between pb-2.5 border-b border-slate-100">
							<div class="flex items-center space-x-2.5">
								<div class="p-2.5 rounded-2xl bg-teal-50 text-teal-700 border border-teal-100 shadow-xs">
									<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
									</svg>
								</div>
								<div>
									<h3 class="font-bold text-slate-900 text-xs">Field Travel & Expenses (EEM)</h3>
									<p class="text-[10px] text-slate-500">Site visits, odometer & claims</p>
								</div>
							</div>

							<!-- Trip Status Badge -->
							<span
								class="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold"
								:class="[
									eemTripStatus === 'IN_PROGRESS' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 animate-pulse' :
									eemTripStatus === 'COMPLETED' ? 'bg-teal-50 text-teal-700 border border-teal-200' :
									'bg-slate-100 text-slate-600 border border-slate-200'
								]"
							>
								{{ eemTripStatusLabel }}
							</span>
						</div>

						<!-- Trip Mini Details / Summary -->
						<div v-if="eemTripStatus === 'IN_PROGRESS'" class="p-3.5 rounded-2xl bg-teal-50/50 border border-teal-100/80 space-y-2 text-xs">
							<div class="flex justify-between items-center">
								<span class="text-slate-600 font-medium flex items-center gap-1.5">
									<span>🚗 Vehicle</span>
								</span>
								<span class="font-bold text-slate-900">{{ todayEemDoc?.vehicle_type }}</span>
							</div>
							<div class="flex justify-between items-center">
								<span class="text-slate-600 font-medium flex items-center gap-1.5">
									<span>📍 Site Visits</span>
								</span>
								<span class="font-bold text-teal-700 font-mono">{{ todayEemSiteVisitsCount }} logged</span>
							</div>
							<div class="flex justify-between items-center">
								<span class="text-slate-600 font-medium flex items-center gap-1.5">
									<span>💳 Day Expenses</span>
								</span>
								<span class="font-bold text-slate-900 font-mono">₹{{ formatAmount(todayEemExpensesSum || todayEemDoc?.total_other_expenses || 0) }}</span>
							</div>
						</div>

						<div v-else-if="eemTripStatus === 'COMPLETED' || eemTripStatus === 'READY_TO_SUBMIT'" class="p-3.5 rounded-2xl bg-emerald-50/60 border border-emerald-100 space-y-2 text-xs">
							<div class="flex justify-between items-center">
								<span class="text-emerald-900 font-medium">Total Distance:</span>
								<span class="font-bold text-emerald-950 font-mono">{{ todayEemDoc?.total_distance || 0 }} km</span>
							</div>
							<div class="flex justify-between items-center">
								<span class="text-emerald-900 font-medium">Grand Total Claim:</span>
								<span class="font-bold text-emerald-950 font-mono">₹{{ formatAmount(todayEemDoc?.total_expense ?? todayEemDoc?.total_claim_amount ?? 0) }}</span>
							</div>
						</div>

						<div v-else class="text-center py-2 text-[11px] text-slate-500">
							No field travel started yet today. Check-in and start your travel day to log visits and odometer.
						</div>

						<!-- Action Button to Open EEM Page -->
						<div class="pt-0.5">
							<button
								@click="goToEem"
								class="w-full py-3 px-4 rounded-2xl bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-sm active:scale-[0.98] transition cursor-pointer"
							>
								<span>{{ eemTripStatus === 'NOT_STARTED' ? 'Start Travel Day' : 'Manage Field Visits & Expenses' }}</span>
								<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
								</svg>
							</button>
						</div>
					</div>
				</div>

				<!-- Fallback Warning State -->
				<div v-else class="bg-white rounded-3xl p-6 shadow-sm border border-amber-200/80 text-center space-y-3 my-6">
					<div class="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-200">
						<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
					<h2 class="text-base font-bold text-slate-900">No Employee Master Linked</h2>
					<p class="text-xs text-slate-600">
						You are logged in as <span class="font-semibold font-mono text-slate-900">{{ session.user }}</span>, but no active Employee record is mapped to this User ID.
					</p>
					<p class="text-[11px] text-slate-500">
						Please contact your HR administrator to link your user ID with an Employee document.
					</p>
					<div class="pt-2 flex justify-center space-x-2.5">
						<button
							@click="refreshData"
							class="px-4 py-2 rounded-2xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-xs shadow-sm transition"
						>
							Check Again
						</button>
						<button
							@click="promptLogout"
							class="px-4 py-2 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 transition"
						>
							Sign out
						</button>
					</div>
				</div>
			</main>
		</div>

		<!-- ========================================== -->
		<!-- MODALS & POPUPS                            -->
		<!-- ========================================== -->

		<!-- Check-in History Modal -->
		<Dialog v-model="showHistoryModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
					</div>
					<h2 class="text-base font-bold text-slate-900">Attendance Check-in History</h2>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2 max-h-80 overflow-y-auto pr-1">
					<div v-if="isCheckinLoading && checkinLogs.length === 0" class="py-6 text-center text-xs text-slate-500">
						<div class="inline-block animate-spin rounded-full h-5 w-5 border-2 border-teal-500 border-t-transparent mb-2"></div>
						<p>Loading records...</p>
					</div>
					<div v-else-if="!isCheckinLoading && checkinLogs.length === 0" class="py-6 text-center text-xs text-slate-400">
						No check-in logs found.
					</div>
					<div
						v-else
						v-for="log in checkinLogs"
						:key="log.name"
						class="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-100 text-xs"
					>
						<div class="flex items-center space-x-3">
							<span
								class="px-2 py-1 rounded-lg text-[10px] font-bold"
								:class="log.log_type === 'IN' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
							>
								{{ log.log_type }}
							</span>
							<div>
								<p class="font-bold text-slate-900">{{ formatFullDateTime(log.time) }}</p>
								<p class="text-[10px] text-slate-400">Device: {{ log.device_id || 'PWA' }}</p>
							</div>
						</div>
						<div class="text-right">
							<span v-if="log.latitude && log.longitude" class="text-[10px] text-teal-600 font-mono block">
								📍 {{ Number(log.latitude).toFixed(2) }}, {{ Number(log.longitude).toFixed(2) }}
							</span>
							<span class="text-[10px] text-slate-400 font-mono">{{ log.name }}</span>
						</div>
					</div>

					<!-- View More Logs Button -->
					<div v-if="hasMoreCheckins" class="pt-2 pb-1 text-center">
						<button
							@click="loadMoreCheckins"
							:disabled="isLoadingMoreCheckins"
							class="w-full py-2.5 px-3 text-xs font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100 active:bg-teal-200 border border-teal-200/80 rounded-2xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-xs cursor-pointer"
						>
							<svg v-if="isLoadingMoreCheckins" class="w-4 h-4 animate-spin text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<span>{{ isLoadingMoreCheckins ? 'Loading older logs...' : `View More Logs (Showing ${checkinLogs.length})` }}</span>
						</button>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-between w-full pt-1">
					<Button
						variant="subtle"
						@click="refreshHistory"
						:loading="isCheckinLoading"
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

		<!-- Check-in / Check-out Confirmation Modal -->
		<Dialog v-model="showPunchConfirm">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div
						class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
						:class="nextAction === 'IN' ? 'bg-teal-50 text-teal-700 border border-teal-200' : 'bg-amber-50 text-amber-600 border border-amber-200'"
					>
						<svg v-if="nextAction === 'IN'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
						</svg>
						<svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">
							Confirm {{ nextAction === 'IN' ? 'Check In' : 'Check Out' }}
						</h2>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-3">
					<p class="text-xs text-slate-600 leading-relaxed">
						Are you sure you want to 
						<strong class="text-slate-900 font-bold">{{ nextAction === 'IN' ? 'Check In' : 'Check Out' }}</strong> 
						now?
					</p>

					<!-- Summary Preview Card -->
					<div class="bg-slate-50 rounded-2xl p-3.5 border border-slate-100 space-y-2 text-xs">
						<div class="flex justify-between items-center py-0.5 border-b border-slate-100">
							<span class="text-slate-500 font-medium">Punch Time</span>
							<span class="font-bold font-mono text-slate-900">{{ liveTimeFormatted }}</span>
						</div>
						<div class="flex justify-between items-center py-0.5 border-b border-slate-100">
							<span class="text-slate-500 font-medium">Date</span>
							<span class="font-bold text-slate-900">{{ liveDateFormatted }}</span>
						</div>
						<div class="flex justify-between items-center py-0.5 border-b border-slate-100">
							<span class="text-slate-500 font-medium">Device</span>
							<span class="font-bold text-slate-900 truncate max-w-[170px]">{{ deviceLabel }}</span>
						</div>
						<div class="flex justify-between items-center py-0.5">
							<span class="text-slate-500 font-medium">GPS Location</span>
							<span class="font-bold text-slate-900 truncate max-w-[170px]">{{ locationStatusText }}</span>
						</div>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						:disabled="isSubmittingCheckin"
						@click="showPunchConfirm = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Cancel
					</Button>
					<Button
						variant="solid"
						:loading="isSubmittingCheckin"
						@click="confirmPunch"
						class="px-4 py-2.5 text-xs font-bold text-white rounded-2xl shadow-sm"
						:class="nextAction === 'IN' ? 'bg-teal-600 hover:bg-teal-500' : 'bg-amber-600 hover:bg-amber-500'"
					>
						{{ nextAction === 'IN' ? 'Yes, Check In' : 'Yes, Check Out' }}
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- Location Permission Required Modal -->
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
						<h2 class="text-base font-bold text-slate-900">Location Access Required</h2>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2.5 text-xs text-slate-600 leading-relaxed">
					<p>
						GPS Location is <strong>mandatory</strong> to record attendance check-in and check-out.
					</p>
					<div class="p-3 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-amber-900 space-y-1">
						<p class="font-bold">Please check the following:</p>
						<ul class="list-disc list-inside space-y-0.5 text-[11px]">
							<li>Turn on <strong>Location / GPS</strong> on your mobile device.</li>
							<li>Allow <strong>Location Permission</strong> in your browser settings.</li>
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

		<!-- Check-in Required To Start Travel Modal -->
		<Dialog v-model="showCheckinRequiredModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">Check-In Required</h2>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2 text-xs text-slate-600 leading-relaxed">
					<p>
						You cannot start a travel day before completing your daily attendance <strong>Check-In</strong>.
					</p>
					<p class="text-[11px] text-slate-500">
						Please click <strong>Check In Now</strong> on your dashboard before beginning your field visits.
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
						@click="handleCheckinFromModal"
						class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl shadow-sm"
					>
						Check In Now
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- Active Travel Day In Progress Modal (Blocks Check-Out) -->
		<Dialog v-model="showActiveTripModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">Active Travel Day In Progress</h2>
					</div>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-2 text-xs text-slate-600 leading-relaxed">
					<p>
						You have an active travel day running. You cannot <strong>Check Out</strong> for attendance while travel tracking is in progress.
					</p>
					<div class="p-3 rounded-2xl bg-amber-50/70 border border-amber-200/80 text-amber-900 text-[11px]">
						Please open the <strong>Expense Manager</strong>, finish your final site visit and record your end odometer to complete your travel day first.
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						@click="showActiveTripModal = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Dismiss
					</Button>
					<Button
						variant="solid"
						@click="goToEemFromModal"
						class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl shadow-sm"
					>
						Go to Expense Manager
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- Logout Confirmation Modal -->
		<Dialog v-model="showLogoutConfirm">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-rose-50 border border-rose-200 text-rose-600 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
						</svg>
					</div>
					<h2 class="text-base font-bold text-slate-900">Confirm Logout</h2>
				</div>
			</template>
			<template #body-content>
				<p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
					Are you sure you want to log out of MobiBiz Lite? You will need to enter your credentials to log back in.
				</p>
			</template>
			<template #actions>
				<div class="flex items-center justify-end space-x-2 w-full pt-1">
					<Button
						variant="subtle"
						@click="showLogoutConfirm = false"
						class="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Cancel
					</Button>
					<Button
						variant="solid"
						@click="confirmLogout"
						class="px-4 py-2.5 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 rounded-2xl shadow-sm"
					>
						Log out
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- Profile Details Modal -->
		<Dialog v-model="showProfileModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
						</svg>
					</div>
					<h2 class="text-base font-bold text-slate-900">Profile Overview</h2>
				</div>
			</template>
			<template #body-content>
				<div class="mt-2 space-y-3">
					<div class="flex items-center space-x-3 p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
						<div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-teal-600 to-teal-400 text-white font-bold text-base flex items-center justify-center flex-shrink-0 shadow-sm overflow-hidden">
							<img
								v-if="employee?.image"
								:src="employee.image"
								:alt="employee.employee_name"
								class="w-full h-full object-cover"
							/>
							<span v-else>{{ getInitials(employee?.employee_name || session.user) }}</span>
						</div>
						<div class="min-w-0 flex-1">
							<h4 class="text-sm font-bold text-slate-900 truncate">{{ employee?.employee_name || session.user }}</h4>
							<p class="text-xs text-slate-500 truncate">{{ employee?.designation || 'Team Member' }}</p>
							<span class="inline-flex items-center px-2 py-0.2 mt-0.5 rounded text-[9px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
								Active Employee
							</span>
						</div>
					</div>

					<div class="grid grid-cols-2 gap-2 text-xs">
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Employee ID</span>
							<span class="font-bold text-slate-900 font-mono text-[11px]">{{ employee?.name || '-' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Designation</span>
							<span class="font-bold text-slate-900 truncate block">{{ employee?.designation || '-' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Department</span>
							<span class="font-bold text-slate-900 truncate block">{{ employee?.department || '-' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Company</span>
							<span class="font-bold text-slate-900 truncate block">{{ employee?.company || '-' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Reports To</span>
							<span class="font-bold text-slate-900 truncate block">{{ employee?.reports_to || 'None' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Joining Date</span>
							<span class="font-bold text-slate-900 font-mono text-[11px] block">{{ employee?.date_of_joining || '-' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Mobile Phone</span>
							<span class="font-bold text-slate-900 font-mono text-[11px] block">{{ employee?.cell_number || '-' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">User ID</span>
							<span class="font-bold text-slate-900 font-mono text-[10px] truncate block">{{ employee?.user_id || session.user }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100 col-span-2">
							<span class="text-[10px] text-slate-400 font-medium block">Email Address</span>
							<span class="font-bold text-slate-900 font-mono text-[11px] truncate block">{{ employee?.company_email || employee?.personal_email || employee?.user_id }}</span>
						</div>
					</div>

					<!-- View All Customers Setting (for Sales Persons) -->
					<div
						v-if="employee?.is_sales_person"
						class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between"
					>
						<div class="pr-3">
							<div class="flex items-center space-x-1.5">
								<span class="text-xs font-bold text-slate-800">View All Customers</span>
								<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-teal-50 text-teal-700 border border-teal-200">
									Sales Scope
								</span>
							</div>
							<p class="text-[10px] text-slate-500 mt-0.5 leading-snug">
								{{ employee?.view_all_customers ? 'Viewing all organization customers in site visit search.' : 'Restricted to only your assigned customers in the master.' }}
							</p>
						</div>
						<button
							type="button"
							@click="toggleViewAllCustomers"
							:disabled="isUpdatingCustomerViewPref"
							:class="[
								'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none',
								employee?.view_all_customers ? 'bg-teal-600' : 'bg-slate-300'
							]"
							role="switch"
							:aria-checked="Boolean(employee?.view_all_customers)"
						>
							<span
								:class="[
									'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out',
									employee?.view_all_customers ? 'translate-x-5' : 'translate-x-0'
								]"
							/>
						</button>
					</div>

					<!-- Change Password Trigger inside Profile -->
					<div class="pt-1">
						<button
							@click="openChangePasswordModal"
							class="w-full py-2.5 px-3 rounded-2xl bg-slate-50 hover:bg-teal-50 border border-slate-200/80 hover:border-teal-200 text-slate-700 hover:text-teal-800 text-xs font-semibold flex items-center justify-between transition active:scale-98"
						>
							<div class="flex items-center space-x-2.5">
								<div class="w-6 h-6 rounded-lg bg-teal-100/70 text-teal-700 flex items-center justify-center">
									<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
									</svg>
								</div>
								<span>Change Password</span>
							</div>
							<svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
						</button>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end w-full pt-1">
					<Button
						variant="solid"
						@click="showProfileModal = false"
						class="px-4 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl"
					>
						Close
					</Button>
				</div>
			</template>
		</Dialog>

		<!-- Change Password Modal -->
		<Dialog v-model="showChangePasswordModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900">Change Password</h2>
						<p class="text-[11px] text-slate-500 font-normal">Update your login credentials</p>
					</div>
				</div>
			</template>
			<template #body-content>
				<form @submit.prevent="submitChangePassword" class="mt-2 space-y-3">
					<!-- Security Notice -->
					<div class="p-3 rounded-2xl bg-amber-50/90 border border-amber-200 text-amber-900 text-xs flex items-start space-x-2.5">
						<svg class="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<p class="text-[11px] leading-relaxed text-amber-800">
							Changing your password will automatically <strong>log you out from all other devices and active sessions</strong>.
						</p>
					</div>

					<!-- Error Alert -->
					<div v-if="pwdError" class="p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start space-x-2">
						<svg class="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<span class="break-words font-medium">{{ pwdError }}</span>
					</div>

					<!-- Success Alert -->
					<div v-if="pwdSuccess" class="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-start space-x-2">
						<svg class="w-4 h-4 flex-shrink-0 mt-0.5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
						<span class="break-words font-medium">{{ pwdSuccess }}</span>
					</div>

					<!-- Current Password Field -->
					<div class="space-y-1">
						<label class="block text-xs font-bold text-slate-700">Current Password</label>
						<div class="relative">
							<input
								v-model="oldPassword"
								:type="showOldPassword ? 'text' : 'password'"
								required
								autocomplete="current-password"
								placeholder="Enter your current password"
								class="w-full pl-3.5 pr-10 py-2.5 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 focus:bg-white text-slate-900 placeholder-slate-400 text-xs font-medium focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition outline-none"
							/>
							<button
								type="button"
								@click="showOldPassword = !showOldPassword"
								class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
								aria-label="Toggle current password visibility"
							>
								<svg v-if="!showOldPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								</svg>
								<svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
								</svg>
							</button>
						</div>
					</div>

					<!-- New Password Field -->
					<div class="space-y-1">
						<label class="block text-xs font-bold text-slate-700">New Password</label>
						<div class="relative">
							<input
								v-model="newPassword"
								:type="showNewPassword ? 'text' : 'password'"
								required
								autocomplete="new-password"
								placeholder="Minimum 6 characters"
								class="w-full pl-3.5 pr-10 py-2.5 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 focus:bg-white text-slate-900 placeholder-slate-400 text-xs font-medium focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition outline-none"
							/>
							<button
								type="button"
								@click="showNewPassword = !showNewPassword"
								class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
								aria-label="Toggle new password visibility"
							>
								<svg v-if="!showNewPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								</svg>
								<svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Confirm Password Field -->
					<div class="space-y-1">
						<label class="block text-xs font-bold text-slate-700">Confirm New Password</label>
						<div class="relative">
							<input
								v-model="confirmPassword"
								:type="showConfirmPassword ? 'text' : 'password'"
								required
								autocomplete="new-password"
								placeholder="Re-enter your new password"
								class="w-full pl-3.5 pr-10 py-2.5 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 focus:bg-white text-slate-900 placeholder-slate-400 text-xs font-medium focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20 transition outline-none"
							/>
							<button
								type="button"
								@click="showConfirmPassword = !showConfirmPassword"
								class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
								aria-label="Toggle confirm password visibility"
							>
								<svg v-if="!showConfirmPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								</svg>
								<svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Actions -->
					<div class="flex items-center space-x-2 pt-2">
						<Button
							type="button"
							variant="subtle"
							@click="closeChangePasswordModal"
							class="flex-1 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-2xl"
						>
							Cancel
						</Button>
						<Button
							type="submit"
							variant="solid"
							:loading="isChangingPassword"
							class="flex-1 py-2.5 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl shadow-sm"
						>
							Update Password
						</Button>
					</div>
				</form>
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
			active-tab="home"
			:is-trip-active="eemTripStatus === 'IN_PROGRESS'"
			:show-eem="!!employee?.is_sales_person"
			@open-history="openHistoryModal"
			@open-profile="openProfileModal"
		/>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { Dialog, Button, call } from "frappe-ui"
import BottomNavBar from "@/components/BottomNavBar.vue"
import mobibizIcon from "@/assets/mobibiz_icon.png"
import { session } from "@/data/session"
import { employeeResource } from "@/data/employee"
import {
	checkinStatusResource,
	checkinHistoryResource,
	addCheckinResource,
} from "@/data/checkin"
import { todayEemResource } from "@/data/eem"
import { detectDeviceDetails } from "@/utils/device"
import { pwaState, promptPwaInstall } from "@/data/pwa"
import { toast } from "@/utils/toast"

const router = useRouter()
const route = useRoute()
const employee = computed(() => employeeResource.data)

// Dropdown & Modal States
const isDropdownOpen = ref(false)
const showLogoutConfirm = ref(false)
const showProfileModal = ref(false)
const showHistoryModal = ref(false)
const showPunchConfirm = ref(false)
const showChangePasswordModal = ref(false)
const profileDropdownRef = ref(null)
const isPunchesExpanded = ref(false)

// Check-in History Pagination States
const checkinLogs = ref([])
const isCheckinLoading = ref(false)
const isLoadingMoreCheckins = ref(false)
const hasMoreCheckins = ref(false)

function handlePwaInstall() {
	isDropdownOpen.value = false
	promptPwaInstall()
}

// Change Password States
const oldPassword = ref("")
const newPassword = ref("")
const confirmPassword = ref("")
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const isChangingPassword = ref(false)
const pwdError = ref("")
const pwdSuccess = ref("")

// Checkin & Location & Device States
const isSubmittingCheckin = ref(false)
const locationCoords = ref(null)
const locationStatusText = ref("GPS Ready")
const detectedDevice = ref(null)

// EEM computed states
const eemData = computed(() => todayEemResource.data || {})
const todayEemDoc = computed(() => eemData.value.doc)
const eemTripStatus = computed(() => eemData.value.trip_status || "NOT_STARTED")
const todayEemSiteVisitsCount = computed(() => todayEemDoc.value?.employee_site_tracking?.length || 0)
const todayEemExpensesSum = computed(() => {
	const exps = todayEemDoc.value?.employee_expense_tracking || []
	return exps.reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0)
})

const eemTripStatusLabel = computed(() => {
	switch (eemTripStatus.value) {
		case "IN_PROGRESS":
			return "Trip In Progress"
		case "COMPLETED":
			return "Day Completed"
		case "READY_TO_SUBMIT":
			return "Trip Finished"
		default:
			return "Not Started"
	}
})

const deviceLabel = computed(() => {
	if (!detectedDevice.value) return "Detecting Device..."
	return `${detectedDevice.value.os} • ${detectedDevice.value.browser}`
})

// Live Clock
const currentTime = ref(new Date())
let clockTimer = null

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

const timeGreeting = computed(() => {
	const hour = currentTime.value.getHours()
	if (hour < 12) return "Good Morning"
	if (hour < 17) return "Good Afternoon"
	return "Good Evening"
})

// Checkin computations
const checkinStatus = computed(() => checkinStatusResource.data || {})
const lastCheckin = computed(() => checkinStatus.value.last_checkin)
const isCheckedIn = computed(() => lastCheckin.value && lastCheckin.value.log_type === "IN")
const nextAction = computed(() => checkinStatus.value.next_action || "IN")
const todayCheckins = computed(() => checkinStatus.value.today_checkins || [])

const firstPunchInTime = computed(() => {
	if (!todayCheckins.value || todayCheckins.value.length === 0) return "Not Yet"
	const inPunches = todayCheckins.value.filter((c) => c.log_type === "IN")
	if (inPunches.length === 0) return "Not Yet"
	// Sort ascending to get earliest IN punch
	const earliest = [...inPunches].sort((a, b) => new Date(a.time) - new Date(b.time))[0]
	return formatLogTime(earliest.time)
})

const lastPunchSummary = computed(() => {
	if (!lastCheckin.value) return "No recent punch"
	const type = lastCheckin.value.log_type
	const time = formatLogTime(lastCheckin.value.time)
	return `${type === "IN" ? "In" : "Out"} at ${time}`
})

const showLocationModal = ref(false)
const showCheckinRequiredModal = ref(false)
const showActiveTripModal = ref(false)
const isAcquiringLocation = ref(false)
const isAcquiringGps = ref(false)
const gpsLoadingTitle = ref("Acquiring GPS Location...")
const gpsLoadingSubtitle = ref("Locking high-accuracy satellite coordinates. Please hold on...")

function toggleDropdown() {
	isDropdownOpen.value = !isDropdownOpen.value
}

function closeDropdown() {
	isDropdownOpen.value = false
}

const isUpdatingCustomerViewPref = ref(false)

async function toggleViewAllCustomers() {
	if (isUpdatingCustomerViewPref.value) return
	isUpdatingCustomerViewPref.value = true
	const newVal = !employee.value?.view_all_customers
	try {
		const res = await call("tq_erphr.pwa_api.update_user_customer_view_preference", {
			view_all: newVal,
		})
		if (res && res.status === "success") {
			await employeeResource.fetch()
			if (newVal) {
				toast.success("You can now view and search all company customers in Site Visits.", "All Customers Enabled")
			} else {
				toast.info("Customer listing is now limited to your assigned customers.", "Assigned Customers Scope")
			}
		}
	} catch (err) {
		console.error("Failed to update customer view preference:", err)
		toast.error("Failed to update preference")
	} finally {
		isUpdatingCustomerViewPref.value = false
	}
}

function openProfileModal() {
	closeDropdown()
	showProfileModal.value = true
}

function openHistoryModal() {
	closeDropdown()
	showHistoryModal.value = true
	fetchInitialCheckinHistory()
}

async function fetchInitialCheckinHistory() {
	isCheckinLoading.value = true
	try {
		const res = await call("tq_erphr.pwa_api.get_employee_checkin_history", {
			limit: 10,
			limit_start: 0,
		})
		checkinLogs.value = res || []
		hasMoreCheckins.value = (res || []).length === 10
	} catch (err) {
		console.error("Failed to fetch checkin history:", err)
		toast.error("Failed to load check-in history")
	} finally {
		isCheckinLoading.value = false
	}
}

async function loadMoreCheckins() {
	if (isLoadingMoreCheckins.value || !hasMoreCheckins.value) return
	isLoadingMoreCheckins.value = true
	try {
		const res = await call("tq_erphr.pwa_api.get_employee_checkin_history", {
			limit: 10,
			limit_start: checkinLogs.value.length,
		})
		const items = res || []
		checkinLogs.value = [...checkinLogs.value, ...items]
		if (items.length < 10) {
			hasMoreCheckins.value = false
		}
	} catch (err) {
		console.error("Failed to load more checkin history:", err)
		toast.error("Failed to load more check-in logs")
	} finally {
		isLoadingMoreCheckins.value = false
	}
}

function refreshHistory() {
	fetchInitialCheckinHistory()
}

function toggleTodayPunches() {
	isPunchesExpanded.value = !isPunchesExpanded.value
}

function goToEem() {
	closeDropdown()
	if (!employee.value?.is_sales_person) {
		return
	}
	router.push("/eem")
}

function goToCustomers() {
	closeDropdown()
	router.push("/customers")
}

function goToStock() {
	closeDropdown()
	router.push("/stock")
}

function goToEemHistory() {
	closeDropdown()
	if (!employee.value?.is_sales_person) {
		return
	}
	router.push("/eem/history")
}

function goToSupervisorEem() {
	closeDropdown()
	router.push("/eem/team")
}

function goToEemFromModal() {
	showActiveTripModal.value = false
	router.push("/eem")
}

function promptLogout() {
	closeDropdown()
	showLogoutConfirm.value = true
}

function confirmLogout() {
	showLogoutConfirm.value = false
	session.logout.submit()
}

function openChangePasswordModal() {
	closeDropdown()
	showProfileModal.value = false
	oldPassword.value = ""
	newPassword.value = ""
	confirmPassword.value = ""
	pwdError.value = ""
	pwdSuccess.value = ""
	showOldPassword.value = false
	showNewPassword.value = false
	showConfirmPassword.value = false
	showChangePasswordModal.value = true
}

function closeChangePasswordModal() {
	showChangePasswordModal.value = false
	oldPassword.value = ""
	newPassword.value = ""
	confirmPassword.value = ""
	pwdError.value = ""
	pwdSuccess.value = ""
}

async function submitChangePassword() {
	pwdError.value = ""
	pwdSuccess.value = ""

	if (!oldPassword.value) {
		pwdError.value = "Please enter your current password."
		return
	}
	if (!newPassword.value) {
		pwdError.value = "Please enter a new password."
		return
	}
	if (newPassword.value.length < 6) {
		pwdError.value = "New password must be at least 6 characters long."
		return
	}
	if (newPassword.value !== confirmPassword.value) {
		pwdError.value = "New password and confirmation do not match."
		return
	}
	if (newPassword.value === oldPassword.value) {
		pwdError.value = "New password cannot be the same as your current password."
		return
	}

	isChangingPassword.value = true
	try {
		const res = await call("tq_erphr.pwa_api.change_user_password", {
			old_password: oldPassword.value,
			new_password: newPassword.value,
		})
		pwdSuccess.value = res?.message || "Password updated successfully. All other devices have been logged out."
		oldPassword.value = ""
		newPassword.value = ""
		confirmPassword.value = ""
		setTimeout(() => {
			if (showChangePasswordModal.value) {
				closeChangePasswordModal()
			}
		}, 2500)
	} catch (error) {
		console.error("Failed to change password:", error)
		const msg = error?.messages?.[0] || error?.message || error?.error || "Failed to change password. Please check your current password."
		// Clean frappe exc trace formatting if present
		pwdError.value = typeof msg === "string" ? msg.replace(/^Error:\s*/, "") : "Failed to change password."
	} finally {
		isChangingPassword.value = false
	}
}

async function promptPunchConfirmation() {
	if (isAcquiringLocation.value || isSubmittingCheckin.value) return
	isAcquiringLocation.value = true
	isAcquiringGps.value = true
	gpsLoadingTitle.value = nextAction.value === "IN" ? "Locking GPS for Check In..." : "Locking GPS for Check Out..."
	gpsLoadingSubtitle.value = "Acquiring high-accuracy satellite coordinates. Please hold on..."

	try {
		const coords = await getCurrentLocation()
		if (!coords || (!coords.latitude && !coords.longitude)) {
			showLocationModal.value = true
			return
		}
		showPunchConfirm.value = true
	} finally {
		isAcquiringLocation.value = false
		isAcquiringGps.value = false
	}
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
			showPunchConfirm.value = true
		} else {
			toast.warning(
				"GPS location could not be acquired. Please verify that Location / GPS is turned ON and location permission is allowed for this site.",
				"GPS Location Required"
			)
		}
	} finally {
		isAcquiringLocation.value = false
		isAcquiringGps.value = false
	}
}

function handleCheckinFromModal() {
	showCheckinRequiredModal.value = false
	promptPunchConfirmation()
}

async function confirmPunch() {
	await handleCheckinAction()
	showPunchConfirm.value = false
}

function refreshData() {
	employeeResource.reload()
	checkinStatusResource.fetch()
	todayEemResource.fetch()
}

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
				console.warn("Geolocation warning/denied:", err.message)
				locationStatusText.value = "📍 GPS not enabled"
				resolve(null)
			},
			{ enableHighAccuracy: true, timeout: 6000, maximumAge: 5000 }
		)
	})
}

// Check-in submission handler
async function handleCheckinAction() {
	if (isSubmittingCheckin.value) return

	const currentAction = nextAction.value
	isSubmittingCheckin.value = true
	locationStatusText.value = "Acquiring GPS location..."

	try {
		let coords = locationCoords.value
		if (!coords || (!coords.latitude && !coords.longitude)) {
			isAcquiringGps.value = true
			gpsLoadingTitle.value = currentAction === "IN" ? "Locking GPS for Check In..." : "Locking GPS for Check Out..."
			gpsLoadingSubtitle.value = "Acquiring high-accuracy satellite coordinates. Please hold on..."
			coords = await getCurrentLocation()
			isAcquiringGps.value = false
		}

		if (!coords || (!coords.latitude && !coords.longitude)) {
			showLocationModal.value = true
			isSubmittingCheckin.value = false
			return
		}

		const dev = detectedDevice.value || detectDeviceDetails()
		
		await addCheckinResource.submit({
			log_type: currentAction,
			latitude: coords.latitude,
			longitude: coords.longitude,
			device_id: dev.shortDeviceId,
			remarks: dev.remarks,
		})

		toast.success(`Punch ${currentAction === "IN" ? "IN" : "OUT"} recorded successfully!`, "Attendance Updated")

		// Refresh status, eem and history
		await checkinStatusResource.fetch()
		await todayEemResource.fetch()
		if (showHistoryModal.value) {
			await fetchInitialCheckinHistory()
		}
	} catch (err) {
		console.error("Check-in error:", err)
		toast.error(err.messages?.[0] || err.message || "Failed to record check-in.", "Punch Failed")
	} finally {
		isAcquiringGps.value = false
		isSubmittingCheckin.value = false
	}
}

// Formatting helpers
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

function formatFullDateTime(timeStr) {
	if (!timeStr) return "-"
	const d = new Date(timeStr)
	if (isNaN(d.getTime())) return timeStr
	return d.toLocaleDateString([], {
		day: "2-digit",
		month: "short",
	}) + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

function getInitials(name) {
	if (!name) return "HR"
	const parts = name.trim().split(" ")
	if (parts.length >= 2) {
		return (parts[0][0] + parts[1][0]).toUpperCase()
	}
	return name.slice(0, 2).toUpperCase()
}

function handleClickOutside(event) {
	if (profileDropdownRef.value && !profileDropdownRef.value.contains(event.target)) {
		closeDropdown()
	}
}

function handleKeydown(event) {
	if (event.key === "Escape") {
		closeDropdown()
		showLogoutConfirm.value = false
		showProfileModal.value = false
		showHistoryModal.value = false
		showPunchConfirm.value = false
		showChangePasswordModal.value = false
	}
}

onMounted(() => {
	document.addEventListener("click", handleClickOutside)
	document.addEventListener("keydown", handleKeydown)
	
	// Detect client device details
	detectedDevice.value = detectDeviceDetails()

	// Start live clock
	clockTimer = setInterval(() => {
		currentTime.value = new Date()
	}, 1000)

	// Attempt passive GPS query on mount
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(
			(pos) => {
				locationCoords.value = {
					latitude: pos.coords.latitude,
					longitude: pos.coords.longitude,
				}
				locationStatusText.value = `📍 GPS: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`
			},
			() => {
				locationStatusText.value = "📍 GPS Ready"
			},
			{ timeout: 4000 }
		)
	}

	todayEemResource.fetch()

	if (route.query.openProfile) {
		showProfileModal.value = true
	}
})

onUnmounted(() => {
	document.removeEventListener("click", handleClickOutside)
	document.removeEventListener("keydown", handleKeydown)
	if (clockTimer) clearInterval(clockTimer)
})
</script>
