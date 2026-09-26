<template>
	<div class="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col justify-start items-center p-0 sm:p-4 font-sans selection:bg-teal-500 selection:text-white relative overflow-x-hidden pb-24">
		<!-- Background ambient soft gradients for desktop container -->
		<div class="hidden sm:block absolute -top-40 -left-40 w-96 h-96 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>
		<div class="hidden sm:block absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-emerald-200/20 blur-3xl pointer-events-none"></div>

		<!-- Mobile App Shell Container -->
		<div class="w-full sm:max-w-md bg-[#f8fafc] min-h-screen sm:min-h-[720px] sm:rounded-3xl sm:shadow-2xl sm:border sm:border-slate-200/80 flex flex-col justify-between relative z-10 overflow-hidden pb-6">
			
			<!-- Mobile Top Header (Sticky at top) -->
			<header class="sticky top-0 z-40 bg-white/95 backdrop-blur-xl border-b border-slate-200/80 shadow-[0_2px_16px_rgba(0,0,0,0.04)] px-4 py-2.5 sm:px-5 transition-all">
				<div class="max-w-md mx-auto">
					<div class="flex items-center justify-between">
						<!-- Back Navigation & Title -->
						<div class="flex items-center space-x-2 min-w-0 pr-2">
							<button
								@click="goBack"
								class="p-2 -ml-1 rounded-2xl text-slate-600 hover:text-teal-700 hover:bg-teal-50/80 active:scale-95 transition cursor-pointer shrink-0"
								title="Back"
							>
								<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
								</svg>
							</button>
							<div class="min-w-0">
								<h1 class="text-sm font-bold text-slate-900 leading-tight flex items-center gap-1.5 truncate">
									<span>Customers Directory</span>
									<span class="w-1.5 h-1.5 rounded-full bg-teal-500 inline-block shrink-0"></span>
								</h1>
								<p class="text-[10px] font-medium text-slate-500 leading-tight truncate mt-0.5" :title="employee?.company_name || 'Partner Locations'">
									<span v-if="employee?.company_name" class="font-semibold text-teal-700">{{ employee.company_name }} • </span>
									<span>Partner Locations</span>
								</p>
							</div>
						</div>

						<!-- Header Actions -->
						<div class="flex items-center space-x-1.5 shrink-0">
							<!-- Toggle View All Customers Scope Quick Button (for Sales Persons) -->
							<button
								v-if="employee?.is_sales_person"
								@click="toggleScope"
								class="px-2.5 py-1 rounded-xl text-[10px] font-bold transition flex items-center space-x-1 border cursor-pointer"
								:class="employee?.view_all_customers ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100' : 'bg-teal-50 text-teal-700 border-teal-200 hover:bg-teal-100'"
								:title="employee?.view_all_customers ? 'Showing all company customers. Tap to show only assigned.' : 'Showing your assigned customers. Tap to view all.'"
							>
								<span>{{ employee?.view_all_customers ? '🌐 All' : '👤 Assigned' }}</span>
							</button>

							<!-- Refresh Button -->
							<button
								@click="fetchInitialCustomers"
								:disabled="isLoading"
								class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
								title="Refresh customer list"
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

					<!-- Search Input Box -->
					<div class="mt-2.5 relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
							<svg v-if="!isLoading" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							<svg v-else class="w-4 h-4 animate-spin text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
						</div>
						<input
							type="text"
							v-model="searchQuery"
							@input="onSearchInput"
							placeholder="Search customer, territory, phone, group..."
							class="w-full pl-9 pr-20 py-2.5 text-xs rounded-2xl bg-slate-50 border border-slate-200 focus:bg-white focus:outline-none focus:ring-4 focus:ring-teal-500/15 focus:border-teal-500 text-slate-900 font-medium placeholder:text-slate-400 shadow-xs transition"
						/>
						<div class="absolute inset-y-0 right-0 pr-2 flex items-center space-x-1">
							<button
								v-if="searchQuery"
								type="button"
								@click="searchQuery = ''; onSearchInput()"
								class="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
								title="Clear search"
							>
								<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							</button>
							<!-- GPS Nearby Toggle Button inside search bar -->
							<button
								type="button"
								@click="toggleNearMe"
								:class="[
									'px-2 py-1 rounded-xl text-[10px] font-bold transition flex items-center space-x-1 cursor-pointer shadow-2xs',
									isNearMeActive ? 'bg-emerald-600 text-white shadow-xs' : 'bg-slate-200/80 text-slate-600 hover:bg-slate-300'
								]"
								:title="isNearMeActive ? 'Sorted by real-time GPS proximity' : 'Tap to sort by closest to your location'"
							>
								<span>📍</span>
								<span>Near Me</span>
							</button>
						</div>
					</div>

					<!-- Quick Filter Chips: Customer Groups -->
					<div class="mt-2.5 flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
						<button
							v-for="group in customerGroups"
							:key="group.value"
							@click="setCustomerGroup(group.value)"
							:class="[
								'px-2.5 py-1 rounded-xl text-[11px] font-semibold whitespace-nowrap transition-all cursor-pointer',
								selectedGroup === group.value
									? 'bg-teal-700 text-white shadow-xs'
									: 'bg-slate-100 text-slate-600 hover:bg-slate-200/80 hover:text-slate-800'
							]"
						>
							{{ group.label }}
						</button>
					</div>
				</div>
			</header>

			<!-- Main Content Area -->
			<main class="flex-1 px-4 pt-3.5 pb-3 sm:px-5 space-y-3">
				<!-- Context / Active Filter Indicator -->
				<div class="flex items-center justify-between text-xs px-1 text-slate-500">
					<div class="flex items-center space-x-1.5">
						<span v-if="isNearMeActive" class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
						<span class="font-medium text-slate-600">
							<template v-if="searchQuery">
								{{ customersList.length }} result{{ customersList.length === 1 ? '' : 's' }} for "{{ searchQuery }}"
							</template>
							<template v-else-if="isNearMeActive">
								Nearest customers to your GPS position
							</template>
							<template v-else>
								{{ employee?.is_sales_person && !employee?.view_all_customers ? 'Assigned Customers' : 'All Customers Directory' }}
							</template>
						</span>
					</div>
					<span class="text-[11px] font-bold font-mono text-teal-700">
						{{ customersList.length }} loaded
					</span>
				</div>

				<!-- Loading State -->
				<div v-if="isLoading && customersList.length === 0" class="py-16 text-center space-y-3">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent"></div>
					<h3 class="text-sm font-bold text-slate-900">Loading Customers...</h3>
					<p class="text-xs text-slate-500">Fetching customer records from ERP</p>
				</div>

				<!-- Empty State -->
				<div
					v-else-if="!isLoading && customersList.length === 0"
					class="py-12 bg-white rounded-3xl border border-dashed border-slate-200 text-center p-6 space-y-3 shadow-xs"
				>
					<div class="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center mx-auto">
						<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
						</svg>
					</div>
					<h3 class="text-sm font-bold text-slate-800">No Customers Found</h3>
					<p class="text-xs text-slate-500 max-w-xs mx-auto">
						<template v-if="searchQuery || selectedGroup !== 'all'">
							No customers match your search filters.
						</template>
						<template v-else-if="employee?.is_sales_person && !employee?.view_all_customers">
							No customers are currently assigned to your sales account. You can switch to "All Customers" to view all organization accounts.
						</template>
						<template v-else>
							No customer master records have been configured yet in the system.
						</template>
					</p>
					<div class="pt-2 flex justify-center gap-2">
						<button
							v-if="searchQuery || selectedGroup !== 'all'"
							@click="resetFilters"
							class="px-3.5 py-2 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
						>
							Clear Search
						</button>
						<button
							v-if="employee?.is_sales_person && !employee?.view_all_customers"
							@click="toggleScope"
							class="inline-flex items-center space-x-1.5 px-4 py-2 rounded-2xl bg-teal-600 text-white text-xs font-semibold shadow-xs hover:bg-teal-700 transition cursor-pointer"
						>
							<span>View All Customers</span>
						</button>
					</div>
				</div>

				<!-- Customer Cards List -->
				<div v-else class="space-y-3">
					<div
						v-for="c in customersList"
						:key="c.name"
						class="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-xs hover:border-teal-300 hover:shadow-sm transition-all relative overflow-hidden"
					>
						<!-- Card Top Row: Name, Code & Distance Badge -->
						<div class="flex items-start justify-between">
							<div class="space-y-1 min-w-0 pr-2">
								<div class="flex items-center space-x-2 flex-wrap">
									<h3 class="text-sm font-bold text-slate-900 leading-tight">
										{{ c.customer_name || c.name }}
									</h3>
									<!-- Distance Badge -->
									<span
										v-if="c.distance_km !== null && c.distance_km !== undefined"
										class="px-1.5 py-0.2 rounded-md text-[9px] font-bold font-mono"
										:class="Number(c.distance_km) <= 5 ? 'bg-emerald-100 text-emerald-800 border border-emerald-300/80' : 'bg-slate-100 text-slate-600 border border-slate-200'"
									>
										📍 {{ formatDistance(c.distance_km) }}
									</span>
								</div>
								<div class="flex items-center space-x-1.5 text-[10px] text-slate-400 font-medium flex-wrap">
									<span class="font-mono bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded text-[9px] font-bold">{{ c.name }}</span>
									<span v-if="c.customer_group" class="text-slate-600">• {{ c.customer_group }}</span>
									<span v-if="c.territory">• {{ c.territory }}</span>
								</div>
							</div>

							<!-- Sales Person Tag -->
							<div v-if="c.sales_person_names" class="flex flex-col items-end flex-shrink-0">
								<span class="px-2 py-0.5 rounded-lg text-[9px] font-bold bg-teal-50 text-teal-800 border border-teal-200/80 truncate max-w-[130px]" :title="c.sales_person_names">
									👤 {{ c.sales_person_names }}
								</span>
							</div>
						</div>

						<!-- Contact & Coordinate Info Bar -->
						<div class="mt-3 pt-2.5 border-t border-slate-100 grid grid-cols-2 gap-2 text-[11px] text-slate-600">
							<div class="flex items-center space-x-1.5 truncate">
								<svg class="w-3.5 h-3.5 text-teal-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
								</svg>
								<a
									v-if="c.mobile_no"
									:href="`tel:${c.mobile_no}`"
									class="text-teal-700 font-semibold hover:underline truncate"
								>
									{{ c.mobile_no }}
								</a>
								<span v-else class="text-slate-400 italic text-[10px]">No phone</span>
							</div>

							<div class="flex items-center space-x-1.5 truncate justify-end">
								<svg class="w-3.5 h-3.5 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
								</svg>
								<span v-if="c.latitude && c.longitude && c.latitude != 0" class="text-teal-600 font-medium text-[10px] truncate">
									Location Tagged
								</span>
								<span v-else class="text-slate-400 italic text-[10px]">No Location</span>
							</div>
						</div>

						<!-- Financial Snapshot Bar: Total Billed & Unpaid -->
						<div class="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
							<!-- Billed -->
							<div class="flex items-center space-x-1.5 min-w-0">
								<span class="text-[11px] text-slate-500 font-semibold shrink-0">Billing:</span>
								<span
									class="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-lg text-xs font-bold font-mono border shadow-2xs truncate"
									:class="Number(c.total_billed) > 0 ? 'bg-emerald-50 text-emerald-800 border-emerald-300' : 'bg-slate-50 text-slate-500 border-slate-200'"
								>
									<span v-if="Number(c.total_billed) > 0" class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>
									<span>₹{{ formatCurrency(c.total_billed) }}</span>
								</span>
							</div>

							<!-- Unpaid / Outstanding -->
							<div class="flex items-center space-x-1.5 shrink-0">
								<span class="text-[11px] text-slate-500 font-semibold">Unpaid:</span>
								<span
									class="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-lg text-xs font-black font-mono border shadow-2xs"
									:class="Number(c.total_unpaid) > 0 ? 'bg-rose-50 text-rose-700 border-rose-300' : 'bg-emerald-50 text-emerald-800 border-emerald-300'"
								>
									<span :class="Number(c.total_unpaid) > 0 ? 'w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0 animate-pulse' : 'w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0'"></span>
									<span>₹{{ formatCurrency(c.total_unpaid) }}</span>
								</span>
							</div>
						</div>

						<!-- Card Bottom Action Toolbar -->
						<div class="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between gap-1.5">
							<!-- 1-Tap Google Maps Navigation -->
							<a
								v-if="c.latitude && c.longitude && c.latitude != 0"
								:href="`https://www.google.com/maps/dir/?api=1&destination=${c.latitude},${c.longitude}`"
								target="_blank"
								class="px-2.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-semibold transition flex items-center space-x-1"
								title="Open Google Maps Directions"
							>
								<span>🧭</span>
								<span>Directions</span>
							</a>
							<div v-else class="text-[10px] text-slate-400 italic">No Location coordinates</div>

							<div class="flex items-center space-x-1.5">
								<!-- View Details -->
								<button
									type="button"
									@click="openCustomerDetails(c)"
									class="px-2.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-semibold transition cursor-pointer"
								>
									Details
								</button>

								<!-- Quick Visit in EEM -->
								<button
									v-if="employee?.is_sales_person"
									type="button"
									@click="goToRecordVisit(c)"
									class="px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-[11px] font-bold shadow-xs transition flex items-center space-x-1 cursor-pointer"
								>
									<span>Visit</span>
									<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
									</svg>
								</button>
							</div>
						</div>
					</div>

					<!-- View More Customers Button -->
					<div v-if="hasMore" class="pt-3 pb-2 text-center">
						<button
							@click="loadMoreCustomers"
							:disabled="isLoadingMore"
							class="w-full py-3 px-4 text-xs font-bold text-teal-800 bg-white hover:bg-teal-50/80 active:bg-teal-100 border border-teal-200/80 rounded-2xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-xs hover:border-teal-300 cursor-pointer"
						>
							<svg v-if="isLoadingMore" class="w-4 h-4 animate-spin text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<span>{{ isLoadingMore ? 'Loading more customers...' : `View More Customers (Showing ${customersList.length})` }}</span>
						</button>
					</div>
				</div>
			</main>

			<!-- Bottom Navigation -->
			<BottomNavBar
				active-tab="customers"
				:show-eem="!!employee?.is_sales_person"
				:is-trip-active="isTripActive"
				@open-history="openHistory"
				@open-profile="openProfile"
			/>
		</div>

		<!-- Customer Details Modal -->
		<Dialog v-model="showDetailsModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900 leading-tight">Customer Profile</h2>
						<p class="text-[10px] text-slate-500">{{ selectedCustomer?.name }}</p>
					</div>
				</div>
			</template>
			<template #body-content>
				<div v-if="selectedCustomer" class="mt-2 space-y-3.5 max-h-96 overflow-y-auto pr-1">
					<!-- Main Title Banner -->
					<div class="p-3.5 rounded-2xl bg-gradient-to-br from-teal-50 to-emerald-50/40 border border-teal-200/80">
						<div class="flex items-start justify-between">
							<div>
								<h3 class="text-sm font-bold text-slate-900 leading-snug">{{ selectedCustomer.customer_name || selectedCustomer.name }}</h3>
								<p class="text-xs text-teal-700 font-mono mt-0.5">{{ selectedCustomer.name }}</p>
							</div>
							<span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-white text-teal-800 border border-teal-200 shadow-2xs">
								{{ selectedCustomer.customer_group || 'General' }}
							</span>
						</div>
					</div>

					<!-- Financial & Account Status Card -->
					<div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2.5">
						<div class="flex items-center justify-between text-xs font-bold text-slate-900">
							<span class="flex items-center gap-1.5">
								<span>💳 Accounts & Billing Overview</span>
							</span>
							<span
								class="px-2 py-0.5 rounded-lg text-[10px] font-black font-mono border"
								:class="Number(selectedCustomer.total_unpaid) > 0 ? 'bg-rose-50 text-rose-800 border-rose-200' : 'bg-emerald-50 text-emerald-800 border-emerald-200'"
							>
								{{ Number(selectedCustomer.total_unpaid) > 0 ? 'Outstanding Due' : 'All Dues Clear' }}
							</span>
						</div>

						<div class="grid grid-cols-2 gap-2">
							<div class="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
								<span class="text-[10px] text-slate-400 font-medium block">Total Billed</span>
								<span class="text-sm font-black text-emerald-700 font-mono mt-0.5 block">
									₹{{ formatCurrency(selectedCustomer.total_billed) }}
								</span>
							</div>
							<div class="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
								<span class="text-[10px] text-slate-400 font-medium block">Total Unpaid</span>
								<span
									class="text-sm font-black font-mono mt-0.5 block"
									:class="Number(selectedCustomer.total_unpaid) > 0 ? 'text-rose-700' : 'text-emerald-700'"
								>
									₹{{ formatCurrency(selectedCustomer.total_unpaid) }}
								</span>
							</div>
						</div>

						<!-- Company-wise breakdown if present -->
						<div v-if="selectedCustomer.dashboard_info && selectedCustomer.dashboard_info.length > 0" class="pt-1.5 border-t border-slate-200/70 space-y-1">
							<div
								v-for="info in selectedCustomer.dashboard_info"
								:key="info.company"
								class="flex items-center justify-between text-[10px] text-slate-500"
							>
								<span class="font-medium text-slate-700">{{ info.company }} (This Year)</span>
								<span class="font-mono font-bold text-slate-800">
									Billing: ₹{{ formatCurrency(info.billing_this_year) }} | Unpaid: ₹{{ formatCurrency(info.total_unpaid) }}
								</span>
							</div>
						</div>
					</div>

					<!-- Key Metrics Grid -->
					<div class="grid grid-cols-2 gap-2 text-xs">
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Territory</span>
							<span class="font-bold text-slate-900 truncate block">{{ selectedCustomer.territory || '-' }}</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100">
							<span class="text-[10px] text-slate-400 font-medium block">Mobile Contact</span>
							<a v-if="selectedCustomer.mobile_no" :href="`tel:${selectedCustomer.mobile_no}`" class="font-bold text-teal-700 block truncate hover:underline">
								📞 {{ selectedCustomer.mobile_no }}
							</a>
							<span v-else class="text-slate-400 italic">-</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100 col-span-2">
							<span class="text-[10px] text-slate-400 font-medium block">Email Address</span>
							<a v-if="selectedCustomer.email_id" :href="`mailto:${selectedCustomer.email_id}`" class="font-bold text-teal-700 block truncate hover:underline">
								✉️ {{ selectedCustomer.email_id }}
							</a>
							<span v-else class="text-slate-400 italic">-</span>
						</div>
						<div class="p-3 rounded-2xl bg-slate-50 border border-slate-100 col-span-2">
							<span class="text-[10px] text-slate-400 font-medium block">GPS Location</span>
							<div v-if="selectedCustomer.latitude && selectedCustomer.longitude && selectedCustomer.latitude != 0" class="flex items-center justify-between mt-0.5">
								<span class="text-xs font-bold text-slate-800">
									📍 Location Recorded
								</span>
								<a
									:href="`https://www.google.com/maps/dir/?api=1&destination=${selectedCustomer.latitude},${selectedCustomer.longitude}`"
									target="_blank"
									class="px-2 py-1 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-700 font-bold text-[10px] border border-teal-200"
								>
									Google Maps ↗
								</a>
							</div>
							<span v-else class="text-slate-400 italic">No Location coordinates recorded</span>
						</div>
					</div>

					<!-- Sales Team Allocation -->
					<div v-if="selectedCustomer.sales_team && selectedCustomer.sales_team.length > 0" class="space-y-1.5">
						<h4 class="text-xs font-bold text-slate-800 flex items-center space-x-1">
							<span>Assigned Sales Team</span>
						</h4>
						<div class="space-y-1.5">
							<div
								v-for="st in selectedCustomer.sales_team"
								:key="st.sales_person"
								class="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between text-xs"
							>
								<div class="flex items-center space-x-2">
									<div class="w-6 h-6 rounded-lg bg-teal-100 text-teal-800 font-bold text-[10px] flex items-center justify-center">
										👤
									</div>
									<div>
										<p class="font-bold text-slate-900">{{ st.sales_person }}</p>
										<p v-if="st.contact_no" class="text-[10px] text-slate-500">{{ st.contact_no }}</p>
									</div>
								</div>
								<span class="px-2 py-0.5 bg-white text-slate-700 font-mono text-[10px] font-bold rounded-lg border border-slate-200">
									{{ Math.round(Number(st.allocated_percentage) || 100) }}%
								</span>
							</div>
						</div>
					</div>

					<!-- Past Visit History for this Customer -->
					<div class="space-y-2">
						<h4 class="text-xs font-bold text-slate-800 flex items-center justify-between">
							<span>Past Visit Logs</span>
							<span class="text-[10px] font-mono text-slate-400">{{ (selectedCustomer.recent_visits || []).length }} recorded</span>
						</h4>
						<div v-if="!selectedCustomer.recent_visits || selectedCustomer.recent_visits.length === 0" class="p-3 text-center bg-slate-50 rounded-2xl border border-slate-100 text-xs text-slate-400">
							No previous field visits logged for this customer.
						</div>
						<div v-else class="space-y-1.5">
							<div
								v-for="v in selectedCustomer.recent_visits"
								:key="v.name"
								class="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs space-y-1"
							>
								<div class="flex items-center justify-between">
									<span class="font-bold text-slate-900">{{ v.trip_date }} • {{ v.visit_time || '-' }}</span>
									<span class="text-[10px] font-mono text-teal-700 font-semibold">{{ v.employee_name }}</span>
								</div>
								<p v-if="v.remarks" class="text-[11px] text-slate-600 italic">"{{ v.remarks }}"</p>
								<p v-if="v.site" class="text-[10px] text-slate-400">Location: {{ v.site }}</p>
							</div>
						</div>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-between w-full pt-1">
					<Button
						variant="subtle"
						@click="showDetailsModal = false"
						class="px-3 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-2xl"
					>
						Close
					</Button>
					<Button
						v-if="employee?.is_sales_person"
						variant="solid"
						@click="goToRecordVisit(selectedCustomer); showDetailsModal = false"
						class="px-4 py-2 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl flex items-center space-x-1"
					>
						<span>Record Site Visit</span>
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
						{{ gpsLoadingTitle || 'Fetching Location...' }}
					</h3>
					<p class="text-[11px] text-slate-500 leading-relaxed">
						{{ gpsLoadingSubtitle || 'Please hold on while we get your current location...' }}
					</p>
				</div>

				<div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
					<div class="bg-teal-600 h-1.5 rounded-full w-2/3 animate-[pulse_1s_ease-in-out_infinite]"></div>
				</div>
			</div>
		</div>

	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { Dialog, Button, call } from "frappe-ui"
import BottomNavBar from "@/components/BottomNavBar.vue"
import { employeeResource } from "@/data/employee"
import { todayEemResource } from "@/data/eem"
import { customerDetailResource } from "@/data/customer"
import { toast } from "@/utils/toast"

const router = useRouter()

// Employee & Sales Person Computed
const employee = computed(() => employeeResource.data)
const isTripActive = computed(() => {
	const tripStatus = todayEemResource.data?.trip_status
	return tripStatus === "IN_PROGRESS"
})

// Query & Filter States
const searchQuery = ref("")
const selectedGroup = ref("all")
const isNearMeActive = ref(true)
const locationCoords = ref(null)
const isAcquiringGps = ref(false)
const gpsLoadingTitle = ref("Fetching Location...")
const gpsLoadingSubtitle = ref("Please hold on while we get your location...")

// Customer List Pagination
const customersList = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(false)

// Customer Details Modal
const showDetailsModal = ref(false)
const selectedCustomer = ref(null)

const customerGroups = [
	{ label: "All Groups", value: "all" },
	{ label: "Commercial", value: "Commercial" },
	{ label: "Government", value: "Government" },
	{ label: "Individual", value: "Individual" },
	{ label: "Non Profit", value: "Non Profit" },
]

function formatDistance(dist) {
	if (dist === null || dist === undefined || isNaN(dist)) return null
	const num = Number(dist)
	if (num < 1) {
		return `${Math.round(num * 1000)} m`
	}
	return `${num.toFixed(1)} km`
}

function formatCurrency(val) {
	if (val === null || val === undefined || isNaN(val)) return "0"
	const num = Number(val)
	return num.toLocaleString("en-IN", {
		maximumFractionDigits: 2,
		minimumFractionDigits: num % 1 !== 0 ? 2 : 0,
	})
}

// Geolocation helper
function acquireUserLocation() {
	return new Promise((resolve) => {
		if (!navigator.geolocation) {
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
				resolve(coords)
			},
			() => resolve(null),
			{ enableHighAccuracy: true, timeout: 6000, maximumAge: 5000 }
		)
	})
}

// Fetch Initial 20 Customers
async function fetchInitialCustomers() {
	isLoading.value = true
	try {
		const params = {
			limit: 20,
			limit_start: 0,
		}
		if (searchQuery.value && searchQuery.value.trim()) {
			params.search_term = searchQuery.value.trim()
		}
		if (selectedGroup.value && selectedGroup.value !== "all") {
			params.customer_group = selectedGroup.value
		}
		if (isNearMeActive.value && locationCoords.value && locationCoords.value.latitude) {
			params.latitude = locationCoords.value.latitude
			params.longitude = locationCoords.value.longitude
		}

		const res = await call("tq_erphr.pwa_api.get_customers_list", params)
		customersList.value = res || []
		hasMore.value = (res || []).length === 20
	} catch (err) {
		console.error("Failed to fetch customers list:", err)
		toast.error("Failed to load customers")
	} finally {
		isLoading.value = false
	}
}

// Load Next Batch of 20 Customers
async function loadMoreCustomers() {
	if (isLoadingMore.value || !hasMore.value) return
	isLoadingMore.value = true
	try {
		const params = {
			limit: 20,
			limit_start: customersList.value.length,
		}
		if (searchQuery.value && searchQuery.value.trim()) {
			params.search_term = searchQuery.value.trim()
		}
		if (selectedGroup.value && selectedGroup.value !== "all") {
			params.customer_group = selectedGroup.value
		}
		if (isNearMeActive.value && locationCoords.value && locationCoords.value.latitude) {
			params.latitude = locationCoords.value.latitude
			params.longitude = locationCoords.value.longitude
		}

		const res = await call("tq_erphr.pwa_api.get_customers_list", params)
		const items = res || []
		customersList.value = [...customersList.value, ...items]
		if (items.length < 20) {
			hasMore.value = false
		}
	} catch (err) {
		console.error("Failed to load more customers:", err)
		toast.error("Failed to load more customers")
	} finally {
		isLoadingMore.value = false
	}
}

// Debounced Search Input
let searchTimer = null
function onSearchInput() {
	if (searchTimer) clearTimeout(searchTimer)
	searchTimer = setTimeout(() => {
		fetchInitialCustomers()
	}, 250)
}

function setCustomerGroup(group) {
	selectedGroup.value = group
	fetchInitialCustomers()
}

async function toggleNearMe() {
	isNearMeActive.value = !isNearMeActive.value
	if (isNearMeActive.value && !locationCoords.value) {
		isAcquiringGps.value = true
		gpsLoadingTitle.value = "Fetching Location..."
		gpsLoadingSubtitle.value = "Please hold on while we get your location..."
		try {
			await acquireUserLocation()
		} finally {
			isAcquiringGps.value = false
		}
		fetchInitialCustomers()
	} else {
		fetchInitialCustomers()
	}
}

function resetFilters() {
	searchQuery.value = ""
	selectedGroup.value = "all"
	fetchInitialCustomers()
}

// Toggle View All Scope Quick Switch
async function toggleScope() {
	const newVal = !employee.value?.view_all_customers
	try {
		const res = await call("tq_erphr.pwa_api.update_user_customer_view_preference", {
			view_all: newVal,
		})
		if (res && res.status === "success") {
			await employeeResource.fetch()
			if (newVal) {
				toast.success("Now showing all organization customers.", "All Customers")
			} else {
				toast.info("Now showing only your assigned customers.", "Assigned Customers")
			}
			fetchInitialCustomers()
		}
	} catch (err) {
		console.error("Failed to update scope preference:", err)
		toast.error("Could not update scope")
	}
}

// Customer Details Modal Trigger
async function openCustomerDetails(c) {
	selectedCustomer.value = { ...c }
	showDetailsModal.value = true

	try {
		const res = await customerDetailResource.submit({ customer_name: c.name })
		if (res && res.name) {
			selectedCustomer.value = res
		}
	} catch (err) {
		console.warn("Could not load full customer details, using cached card:", err)
	}
}

function goToRecordVisit(c) {
	if (!c) return
	router.push({
		path: "/eem",
		query: {
			prefillCustomer: c.name,
			prefillCustomerName: c.customer_name || c.name,
			prefillLat: c.latitude || "",
			prefillLng: c.longitude || "",
			prefillMobile: c.mobile_no || "",
			prefillAddress: c.address_text || c.primary_address || c.territory || "",
			t: Date.now(),
		},
	})
}

function goBack() {
	router.push("/")
}

function openHistory() {
	router.push("/eem/history")
}

function openProfile() {
	router.push("/?openProfile=1")
}

onMounted(async () => {
	if (!employeeResource.data && !employeeResource.loading) {
		employeeResource.fetch()
	}
	todayEemResource.fetch()

	// Acquire location for nearby sorting
	const coords = await acquireUserLocation()
	fetchInitialCustomers()
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
