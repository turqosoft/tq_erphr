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
						<div class="flex items-center space-x-2.5 min-w-0">
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
									<span class="truncate">Team Sales & Receivables</span>
									<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-teal-100 text-teal-800 shrink-0">
										Supervisor
									</span>
								</h1>
								<p class="text-[10px] font-medium text-slate-500 leading-none flex items-center gap-1 mt-0.5 truncate">
									<span v-if="employee?.company_name" class="font-semibold text-teal-700 truncate">{{ employee.company_name }} •</span>
									<span>Billing & Collections</span>
								</p>
							</div>
						</div>

						<!-- Header Actions -->
						<div class="flex items-center space-x-1.5 shrink-0">
							<!-- Refresh Button -->
							<button
								@click="refreshActiveView"
								:disabled="isLoading"
								class="p-2 rounded-2xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 active:scale-95 transition cursor-pointer"
								title="Refresh data"
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

			<!-- Main Content Body -->
			<main class="w-full flex-1 flex flex-col pt-16 px-4 sm:px-5 space-y-4">
				
				<!-- Not a Supervisor Warning -->
				<div
					v-if="!isLoading && !isSupervisorUser"
					class="bg-amber-50 border border-amber-200 rounded-3xl p-6 text-center my-8 space-y-3 shadow-xs"
				>
					<div class="w-12 h-12 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center mx-auto">
						<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
					<h3 class="text-sm font-bold text-slate-800">Supervisor Access Required</h3>
					<p class="text-xs text-slate-600 leading-relaxed">
						You do not have any subordinate sales executives assigned under your profile in ERPNext.
					</p>
					<button
						@click="router.push('/')"
						class="px-4 py-2 bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold rounded-xl transition"
					>
						Return to Home
					</button>
				</div>

				<template v-else>
					<!-- Supervisor Module Switcher -->
					<div class="grid grid-cols-2 p-1 bg-slate-200/70 rounded-2xl gap-1">
						<button
							type="button"
							class="py-1.5 text-xs font-bold rounded-xl bg-white text-teal-800 shadow-xs flex items-center justify-center gap-1.5 cursor-default"
						>
							<span>📊 Team Sales</span>
						</button>
						<button
							type="button"
							@click="router.push('/eem/team')"
							class="py-1.5 text-xs font-bold rounded-xl text-slate-600 hover:text-slate-900 flex items-center justify-center gap-1.5 cursor-pointer transition hover:bg-white/50"
						>
							<span>🚗 Field Trips</span>
						</button>
					</div>

					<!-- ========================================== -->
					<!-- 1. TEAM MEMBER SELECTOR CAROUSEL           -->
					<!-- ========================================== -->
					<div class="bg-white rounded-2xl p-2.5 shadow-xs border border-slate-200/80 space-y-2">
						<div class="flex items-center justify-between px-1">
							<span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Team Member Filter</span>
							<span class="text-[10px] font-semibold text-teal-700">
								{{ activeMemberLabel }}
							</span>
						</div>

						<div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
							<!-- All Team Option -->
							<button
								type="button"
								@click="selectSalesPerson('all')"
								class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 shrink-0"
								:class="selectedSalesPerson === 'all' ? 'bg-teal-700 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
							>
								<span>👥 All Team</span>
								<span v-if="teamMembers.length > 0" class="text-[10px] opacity-80">({{ teamMembers.length }})</span>
							</button>

							<!-- Me / Current User Option (if available) -->
							<button
								v-if="hasCurrentUserSp"
								type="button"
								@click="selectSalesPerson('me')"
								class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 shrink-0"
								:class="selectedSalesPerson === 'me' ? 'bg-teal-700 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
							>
								<span>⭐ Me (Current)</span>
							</button>

							<!-- Individual Subordinates -->
							<button
								v-for="member in subordinatesOnly"
								:key="member.sales_person"
								type="button"
								@click="selectSalesPerson(member.sales_person)"
								class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 shrink-0"
								:class="selectedSalesPerson === member.sales_person ? 'bg-teal-700 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
							>
								<div class="w-4 h-4 rounded-full bg-slate-300 text-[9px] flex items-center justify-center font-bold text-slate-700 overflow-hidden">
									<img v-if="member.image" :src="member.image" class="w-full h-full object-cover" />
									<span v-else>{{ getInitials(member.sales_person_name) }}</span>
								</div>
								<span>{{ member.sales_person_name }}</span>
							</button>
						</div>
					</div>

					<!-- ========================================== -->
					<!-- 2. PRIMARY VIEW SWITCHER TABS              -->
					<!-- ========================================== -->
					<div class="grid grid-cols-2 p-1 bg-slate-200/70 rounded-2xl gap-1">
						<button
							type="button"
							@click="activeTab = 'billing'"
							class="py-2 text-xs font-black rounded-xl transition-all cursor-pointer flex items-center justify-center gap-1.5"
							:class="activeTab === 'billing' ? 'bg-white text-teal-800 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
							</svg>
							<span>Billing Overview</span>
						</button>

						<button
							type="button"
							@click="activeTab = 'outstanding'"
							class="py-2 text-xs font-black rounded-xl transition-all cursor-pointer flex items-center justify-center gap-1.5 relative"
							:class="activeTab === 'outstanding' ? 'bg-white text-teal-800 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
							</svg>
							<span>Outstanding Details</span>
							<span
								v-if="outstandingSummary?.total_customers_count > 0"
								class="px-1.5 py-0.2 rounded-full text-[9px] font-black bg-rose-500 text-white"
							>
								{{ outstandingSummary.total_customers_count }}
							</span>
						</button>
					</div>

					<!-- ========================================== -->
					<!-- TAB 1: BILLING OVERVIEW                     -->
					<!-- ========================================== -->
					<div v-if="activeTab === 'billing'" class="space-y-4">
						
						<!-- Period Filter Pills -->
						<div class="bg-white rounded-2xl p-2.5 shadow-xs border border-slate-200/80 space-y-2">
							<div class="flex items-center justify-between px-1">
								<span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Date Period</span>
								<span class="text-[10px] font-semibold text-slate-600">
									{{ salesData?.from_date }} ➔ {{ salesData?.to_date }}
								</span>
							</div>

							<div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
								<button
									v-for="p in periods"
									:key="p.value"
									type="button"
									@click="selectPeriod(p.value)"
									class="px-2.5 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition cursor-pointer"
									:class="selectedPeriod === p.value ? 'bg-teal-600 text-white shadow-xs font-bold' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
								>
									{{ p.label }}
								</button>
							</div>

							<!-- Custom Date Range Picker (if period === 'custom') -->
							<div v-if="selectedPeriod === 'custom'" class="pt-2 border-t border-slate-100 flex items-center gap-2">
								<div class="flex-1">
									<label class="text-[9px] font-bold text-slate-400 block mb-0.5">From Date</label>
									<input
										type="date"
										v-model="customFromDate"
										@change="fetchSalesData"
										class="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-2 py-1 text-slate-700 outline-none focus:ring-1 focus:ring-teal-500"
									/>
								</div>
								<div class="flex-1">
									<label class="text-[9px] font-bold text-slate-400 block mb-0.5">To Date</label>
									<input
										type="date"
										v-model="customToDate"
										@change="fetchSalesData"
										class="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-2 py-1 text-slate-700 outline-none focus:ring-1 focus:ring-teal-500"
									/>
								</div>
							</div>
						</div>

						<!-- Billing Main KPI Card -->
						<div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-teal-700 via-teal-600 to-teal-500 text-white p-5 shadow-lg shadow-teal-700/20">
							<div class="absolute -right-10 -bottom-10 w-44 h-44 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>

							<div class="relative z-10 space-y-3.5">
								<div class="flex items-start justify-between">
									<div>
										<span class="text-[10px] uppercase font-bold text-teal-100 tracking-wider block">
											Total Billed ({{ activePeriodLabel }})
										</span>
										<div class="text-3xl font-black tracking-tight text-white font-mono mt-1">
											₹{{ formatCurrency(salesSummary?.total_billed || 0) }}
										</div>
									</div>

									<!-- Growth Pill -->
									<div
										v-if="salesSummary?.growth_percentage !== undefined && salesSummary?.previous_period_billed > 0"
										class="px-2.5 py-1 rounded-xl text-xs font-black flex items-center gap-1 shadow-xs"
										:class="salesSummary.growth_percentage >= 0 ? 'bg-emerald-400 text-emerald-950' : 'bg-rose-400 text-rose-950'"
									>
										<span>{{ salesSummary.growth_percentage >= 0 ? '▲ +' : '▼ ' }}{{ Math.abs(salesSummary.growth_percentage) }}%</span>
									</div>
								</div>

								<!-- 3-Column KPI Ribbon: Total, Tax, Grand Total -->
								<div class="grid grid-cols-3 gap-2 pt-3 border-t border-white/20 text-center">
									<!-- Total (Net Amount) -->
									<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
										<span class="text-[9px] font-bold text-teal-100 uppercase tracking-wider block">Total</span>
										<span class="text-xs font-black text-white font-mono mt-0.5 block truncate" :title="`₹${formatCurrency(salesSummary?.total_amount || 0)}`">
											₹{{ formatCurrency(salesSummary?.total_amount || 0) }}
										</span>
									</div>

									<!-- Tax Amount -->
									<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
										<span class="text-[9px] font-bold text-teal-100 uppercase tracking-wider block">Tax</span>
										<span class="text-xs font-black text-white font-mono mt-0.5 block truncate" :title="`₹${formatCurrency(salesSummary?.total_tax || 0)}`">
											₹{{ formatCurrency(salesSummary?.total_tax || 0) }}
										</span>
									</div>

									<!-- Grand Total -->
									<div class="bg-white/15 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/20 shadow-xs">
										<span class="text-[9px] font-bold text-teal-100 uppercase tracking-wider block">Grand Total</span>
										<span class="text-xs font-black text-teal-100 font-mono mt-0.5 block truncate" :title="`₹${formatCurrency(salesSummary?.total_grand_total || salesSummary?.total_billed || 0)}`">
											₹{{ formatCurrency(salesSummary?.total_grand_total || salesSummary?.total_billed || 0) }}
										</span>
									</div>
								</div>

								<!-- Operational Summary: Invoices, Collected, Pending -->
								<div class="grid grid-cols-3 gap-2 pt-2 border-t border-white/10 text-center">
									<div class="bg-black/10 rounded-xl py-1 px-1">
										<span class="text-[9px] font-medium text-teal-200/80 block">Invoices</span>
										<span class="text-xs font-bold text-white font-mono mt-0.5 block">
											{{ salesSummary?.total_invoices || 0 }}
										</span>
									</div>
									<div class="bg-black/10 rounded-xl py-1 px-1">
										<span class="text-[9px] font-medium text-emerald-200/80 block">Collected</span>
										<span class="text-xs font-bold text-emerald-300 font-mono mt-0.5 block truncate" :title="`₹${formatCurrency(salesSummary?.total_paid || 0)}`">
											₹{{ formatCurrency(salesSummary?.total_paid || 0) }}
										</span>
									</div>
									<div class="bg-black/10 rounded-xl py-1 px-1">
										<span class="text-[9px] font-medium text-amber-200/80 block">Pending</span>
										<span class="text-xs font-bold text-amber-300 font-mono mt-0.5 block truncate" :title="`₹${formatCurrency(salesSummary?.total_unpaid || 0)}`">
											₹{{ formatCurrency(salesSummary?.total_unpaid || 0) }}
										</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Team Contribution Leaderboard (Shown when viewing All Team) -->
						<div v-if="selectedSalesPerson === 'all'" class="bg-white rounded-3xl p-4 shadow-xs border border-slate-200/80 space-y-3">
							<div class="flex items-center justify-between pb-1 border-b border-slate-100">
								<span class="text-xs font-bold text-slate-800 flex items-center gap-1.5">
									<span>🏆 Team Contribution</span>
									<span class="text-[10px] text-slate-400 font-normal">({{ teamMembers.length }} Reps)</span>
								</span>
								<span class="text-[10px] font-semibold text-teal-700">Ranked by Volume</span>
							</div>

							<div v-if="teamMembers.length > 0" class="space-y-3">
								<div
									v-for="(member, idx) in teamMembers"
									:key="member.sales_person"
									@click="selectSalesPerson(member.sales_person)"
									class="p-2.5 rounded-2xl bg-slate-50 hover:bg-teal-50/60 border border-slate-100 transition cursor-pointer active:scale-98 space-y-1.5"
								>
									<div class="flex items-center justify-between">
										<div class="flex items-center space-x-2 min-w-0">
											<span class="w-5 h-5 rounded-full bg-slate-200 text-slate-700 text-[10px] font-black flex items-center justify-center shrink-0">
												{{ idx + 1 }}
											</span>
											<div class="min-w-0">
												<p class="text-xs font-bold text-slate-800 truncate flex items-center gap-1">
													<span>{{ member.sales_person_name }}</span>
													<span v-if="member.is_current_user" class="px-1 py-0.2 rounded text-[8px] font-bold bg-amber-100 text-amber-800">Me</span>
												</p>
												<p class="text-[10px] text-slate-400 truncate">{{ member.invoice_count || 0 }} Invoices</p>
											</div>
										</div>

										<div class="text-right shrink-0">
											<div class="text-xs font-black text-slate-900 font-mono">
												₹{{ formatCurrency(member.total_billed || 0) }}
											</div>
											<div class="text-[10px] font-bold text-teal-700">
												{{ member.contribution_percentage || 0 }}%
											</div>
										</div>
									</div>

									<!-- Progress Bar -->
									<div class="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
										<div
											class="h-full bg-gradient-to-r from-teal-500 to-emerald-400 rounded-full transition-all duration-300"
											:style="{ width: `${Math.min(100, Math.max(0, member.contribution_percentage || 0))}%` }"
										></div>
									</div>
								</div>
							</div>

							<div v-else class="text-center py-4 text-xs text-slate-400 italic">
								No team members registered yet.
							</div>
						</div>

						<!-- Recent Sales Invoices List -->
						<div ref="invoicesSectionRef" class="bg-white rounded-3xl p-4 shadow-xs border border-slate-200/80 space-y-3 scroll-mt-20">
							<div class="space-y-2.5 pb-2 border-b border-slate-100">
								<!-- Header Row -->
								<div class="flex items-center justify-between gap-2">
									<div class="flex items-center gap-1.5">
										<span class="text-xs font-bold text-slate-800">
											Recent Invoices
										</span>
										<span class="text-[10px] font-bold px-1.5 py-0.2 rounded-full bg-slate-100 text-slate-600 font-mono">
											{{ totalInvoicesCount }}<template v-if="rawInvoicesCount !== totalInvoicesCount"> / {{ rawInvoicesCount }}</template>
										</span>
									</div>
									<div class="flex items-center gap-2">
										<label class="flex items-center gap-1 text-[10px] text-slate-500">
											<span>Show:</span>
											<select
												v-model.number="invoicesPageSize"
												@change="onInvoicesPageSizeChange"
												class="px-1.5 py-0.5 text-[10px] font-bold rounded-lg bg-slate-100 border border-slate-200 text-slate-700 focus:outline-none cursor-pointer"
											>
												<option v-for="sz in pageSizeOptions" :key="sz" :value="sz">{{ sz }}</option>
											</select>
										</label>
										<span class="text-[10px] text-slate-400">Submitted</span>
									</div>
								</div>

								<!-- Customer Filter Row -->
								<div class="flex items-center gap-2">
									<!-- Customer Select Dropdown -->
									<div class="relative flex-1">
										<select
											v-model="invoiceCustomerFilter"
											@change="invoicesPage = 1"
											class="w-full py-1.5 pl-2.5 pr-7 text-xs rounded-xl bg-slate-50 border border-slate-200 text-slate-800 font-medium truncate focus:outline-none focus:ring-1 focus:ring-teal-500 cursor-pointer"
										>
											<option value="all">🏢 All Customers ({{ rawInvoicesCount }})</option>
											<option v-for="c in invoiceCustomerOptions" :key="c.customer" :value="c.customer">
												{{ c.customer_name }} ({{ c.count }})
											</option>
										</select>
									</div>

									<!-- Search Input (Customer Name or Invoice #) -->
									<div class="relative w-36 sm:w-44 shrink-0">
										<input
											type="text"
											v-model="invoiceSearchQuery"
											@input="invoicesPage = 1"
											placeholder="Search..."
											class="w-full pl-7 pr-6 py-1.5 text-xs rounded-xl bg-slate-50 border border-slate-200 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-teal-500"
										/>
										<svg class="w-3.5 h-3.5 text-slate-400 absolute left-2 top-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
										</svg>
										<button
											v-if="invoiceSearchQuery"
											type="button"
											@click="invoiceSearchQuery = ''; invoicesPage = 1"
											class="absolute right-2 top-1.5 text-slate-400 hover:text-slate-600 text-xs font-bold"
										>
											&times;
										</button>
									</div>
								</div>

								<!-- Active Filter Tags (when filtered) -->
								<div v-if="invoiceCustomerFilter !== 'all' || invoiceSearchQuery" class="flex items-center gap-1.5 text-[10px] flex-wrap pt-0.5">
									<span class="text-slate-400">Filtering:</span>
									<span v-if="invoiceCustomerFilter !== 'all'" class="px-2 py-0.5 rounded-full bg-teal-50 border border-teal-200 text-teal-800 font-semibold flex items-center gap-1">
										{{ selectedCustomerLabel }}
										<button @click="invoiceCustomerFilter = 'all'; invoicesPage = 1" class="text-teal-600 hover:text-teal-900 font-black ml-0.5">&times;</button>
									</span>
									<span v-if="invoiceSearchQuery" class="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-semibold flex items-center gap-1">
										"{{ invoiceSearchQuery }}"
										<button @click="invoiceSearchQuery = ''; invoicesPage = 1" class="text-slate-500 hover:text-slate-800 font-black ml-0.5">&times;</button>
									</span>
									<button
										type="button"
										@click="clearInvoiceCustomerFilter"
										class="text-[10px] text-teal-700 font-semibold underline hover:text-teal-900 ml-auto"
									>
										Clear Filter
									</button>
								</div>
							</div>

							<div v-if="totalInvoicesCount > 0" class="space-y-2">
								<div
									v-for="inv in visibleInvoices"
									:key="inv.name"
									class="p-3 rounded-2xl bg-slate-50 border border-slate-100 space-y-1.5"
								>
									<div class="flex items-start justify-between gap-2">
										<div class="min-w-0">
											<h4 class="text-xs font-bold text-slate-900 truncate">{{ inv.customer_name }}</h4>
											<p class="text-[10px] text-slate-500 font-mono mt-0.5">{{ inv.name }} • {{ inv.posting_date }}</p>
										</div>
										<div class="text-right shrink-0">
											<span class="text-xs font-black text-slate-900 font-mono block">
												₹{{ formatCurrency(inv.grand_total) }}
											</span>
											<span
												class="inline-block px-1.5 py-0.2 rounded text-[9px] font-bold mt-0.5"
												:class="inv.outstanding_amount > 0 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'"
											>
												{{ inv.outstanding_amount > 0 ? `Unpaid ₹${formatCurrency(inv.outstanding_amount)}` : 'Fully Paid' }}
											</span>
										</div>
									</div>

									<div class="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-200/60">
										<span class="flex items-center gap-1">
											<span class="text-slate-400">Rep:</span>
											<span class="font-semibold text-teal-800">{{ inv.sales_person_name }}</span>
										</span>
										<div class="flex items-center gap-2 font-mono text-[10px] text-slate-500">
											<span v-if="inv.total !== undefined">Total: ₹{{ formatCurrency(inv.total) }}</span>
											<span v-if="inv.total_taxes_and_charges !== undefined && inv.total_taxes_and_charges > 0">Tax: ₹{{ formatCurrency(inv.total_taxes_and_charges) }}</span>
											<span v-if="inv.due_date" class="text-slate-400 font-sans">
												Due: {{ inv.due_date }}
											</span>
										</div>
									</div>
								</div>

								<!-- Prev / Next Pagination Bar -->
								<div v-if="totalInvoicesPages > 1 || totalInvoicesCount > 10" class="flex items-center justify-between gap-2 pt-2 border-t border-slate-100">
									<button
										type="button"
										:disabled="invoicesPage <= 1"
										@click="changeInvoicesPage(invoicesPage - 1)"
										class="px-3 py-1.5 rounded-xl text-[11px] font-bold flex items-center gap-1 transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed bg-slate-100 hover:bg-slate-200 text-slate-700 active:scale-95"
									>
										<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
										</svg>
										<span>Prev</span>
									</button>

									<div class="text-center">
										<span class="text-[11px] font-bold text-slate-700 block">
											Page {{ invoicesPage }} of {{ totalInvoicesPages }}
										</span>
										<span class="text-[10px] text-slate-400">
											{{ invoicesRangeStart }}–{{ invoicesRangeEnd }} of {{ totalInvoicesCount }}
										</span>
									</div>

									<button
										type="button"
										:disabled="invoicesPage >= totalInvoicesPages"
										@click="changeInvoicesPage(invoicesPage + 1)"
										class="px-3 py-1.5 rounded-xl text-[11px] font-bold flex items-center gap-1 transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed bg-teal-600 hover:bg-teal-700 text-white active:scale-95"
									>
										<span>Next</span>
										<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
										</svg>
									</button>
								</div>
							</div>

							<div v-else class="text-center py-6 text-xs text-slate-400 italic space-y-2">
								<p v-if="invoiceCustomerFilter !== 'all' || invoiceSearchQuery">
									No invoices found matching the customer or search filter.
								</p>
								<p v-else>
									No billed invoices found for the selected period and rep.
								</p>
								<button
									v-if="invoiceCustomerFilter !== 'all' || invoiceSearchQuery"
									type="button"
									@click="clearInvoiceCustomerFilter"
									class="inline-block px-3 py-1 rounded-xl text-xs font-bold bg-teal-50 text-teal-700 border border-teal-200 hover:bg-teal-100 transition active:scale-95 cursor-pointer"
								>
									Clear Customer Filter
								</button>
							</div>
						</div>

					</div>

					<!-- ========================================== -->
					<!-- TAB 2: OUTSTANDING & AGING DETAILS         -->
					<!-- ========================================== -->
					<div v-else-if="activeTab === 'outstanding'" class="space-y-4">
						
						<!-- Outstanding Hero KPI Card -->
						<div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-teal-900 text-white p-5 shadow-lg shadow-slate-900/20">
							<div class="relative z-10 space-y-3.5">
								<div class="flex items-start justify-between">
									<div>
										<span class="text-[10px] uppercase font-bold text-teal-200 tracking-wider block">
											Total Customer Outstanding
										</span>
										<div class="text-3xl font-black tracking-tight text-white font-mono mt-1">
											₹{{ formatCurrency(outstandingSummary?.total_outstanding || 0) }}
										</div>
									</div>

									<!-- Overdue Alert Pill -->
									<div
										v-if="outstandingSummary?.total_overdue > 0"
										class="px-2.5 py-1 rounded-xl text-xs font-black bg-rose-500/90 text-white flex items-center gap-1 shadow-xs border border-rose-400/30"
									>
										<span>⚠️ ₹{{ formatCurrency(outstandingSummary.total_overdue) }} Overdue</span>
									</div>
								</div>

								<!-- 2-Column Metrics Ribbon -->
								<div class="grid grid-cols-2 gap-2 pt-3 border-t border-white/20 text-center">
									<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
										<span class="text-[9px] font-medium text-teal-100 uppercase tracking-wider block">On-Time (Not Due)</span>
										<span class="text-xs font-black text-emerald-300 font-mono mt-0.5 block truncate">
											₹{{ formatCurrency(outstandingSummary?.total_current || 0) }}
										</span>
									</div>

									<div class="bg-white/10 backdrop-blur-xs rounded-2xl py-2 px-1 border border-white/10">
										<span class="text-[9px] font-medium text-teal-100 uppercase tracking-wider block">Accounts with Balance</span>
										<span class="text-xs font-black text-white font-mono mt-0.5 block truncate">
											{{ outstandingSummary?.total_customers_count || 0 }} Customers
										</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Aging Buckets Filter Bar -->
						<div class="bg-white rounded-2xl p-2.5 shadow-xs border border-slate-200/80 space-y-2">
							<div class="flex items-center justify-between px-1">
								<span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Aging Breakdown</span>
								<span class="text-[10px] font-bold text-teal-700">Filter by Overdue Tier</span>
							</div>

							<div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
								<button
									v-for="b in agingBuckets"
									:key="b.value"
									type="button"
									@click="selectAgingBucket(b.value)"
									class="px-2.5 py-1.5 rounded-xl text-[11px] font-bold whitespace-nowrap transition cursor-pointer flex items-center gap-1 shrink-0"
									:class="selectedAgingBucket === b.value ? 'bg-slate-900 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
								>
									<span>{{ b.label }}</span>
									<span v-if="b.amount > 0" class="text-[10px] opacity-80 font-mono">
										(₹{{ formatCompact(b.amount) }})
									</span>
								</button>
							</div>
						</div>

						<!-- Search and Sorting Bar -->
						<div class="flex items-center gap-2">
							<div class="relative flex-1">
								<input
									type="text"
									v-model="searchQuery"
									@input="debouncedOutstandingSearch"
									placeholder="Search customer, invoice..."
									class="w-full pl-8 pr-3 py-2 text-xs rounded-2xl bg-white border border-slate-200 text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
								/>
								<svg class="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
								</svg>
							</div>

							<select
								v-model="sortBy"
								@change="fetchOutstandingData"
								class="px-2.5 py-2 text-xs rounded-2xl bg-white border border-slate-200 text-slate-700 font-semibold focus:outline-none cursor-pointer"
							>
								<option value="outstanding_desc">Highest Due</option>
								<option value="overdue_desc">Oldest Overdue</option>
								<option value="customer_asc">Customer A-Z</option>
							</select>
						</div>

						<!-- Customer Receivables List -->
						<div ref="customersSectionRef" class="space-y-3 scroll-mt-20">
							<!-- Receivables Header & Page Size -->
							<div v-if="totalCustomersCount > 0" class="flex items-center justify-between px-1">
								<span class="text-xs font-bold text-slate-700">
									Customer Receivables ({{ totalCustomersCount }})
								</span>
								<label class="flex items-center gap-1.5 text-[11px] text-slate-500">
									<span>Show:</span>
									<select
										v-model.number="customersPageSize"
										@change="onCustomersPageSizeChange"
										class="px-2 py-1 text-[11px] font-bold rounded-xl bg-white border border-slate-200 text-slate-700 focus:outline-none cursor-pointer shadow-xs"
									>
										<option v-for="sz in pageSizeOptions" :key="sz" :value="sz">{{ sz }}</option>
									</select>
								</label>
							</div>

							<div
								v-for="cust in visibleCustomers"
								:key="cust.customer"
								class="bg-white rounded-3xl p-4 shadow-xs border border-slate-200/80 space-y-3 transition hover:border-teal-200"
							>
								<!-- Customer Header -->
								<div class="flex items-start justify-between gap-2">
									<div class="min-w-0 flex-1">
										<h3 class="text-xs font-bold text-slate-900 truncate">{{ cust.customer_name }}</h3>
										<p class="text-[10px] text-slate-500 mt-0.5 flex items-center gap-1.5 truncate">
											<span class="font-medium text-teal-800 truncate">{{ cust.sales_person_name }}</span>
											<span class="text-slate-300">•</span>
											<span class="truncate">{{ cust.territory || 'General' }}</span>
										</p>
									</div>

									<div class="text-right shrink-0">
										<div class="text-sm font-black text-slate-900 font-mono">
											₹{{ formatCurrency(cust.total_outstanding) }}
										</div>
										<span
											v-if="cust.total_overdue > 0"
											class="inline-block px-1.5 py-0.2 rounded text-[9px] font-black bg-rose-100 text-rose-800 mt-0.5"
										>
											⚠️ {{ cust.max_overdue_days }}d Overdue: ₹{{ formatCurrency(cust.total_overdue) }}
										</span>
										<span
											v-else
											class="inline-block px-1.5 py-0.2 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800 mt-0.5"
										>
											On-Time (Not Due)
										</span>
									</div>
								</div>

								<!-- 1-Tap Field Action Buttons -->
								<div class="flex items-center gap-2 pt-2 border-t border-slate-100">
									<!-- Call Button -->
									<a
										v-if="cust.mobile_no"
										:href="`tel:${cust.mobile_no}`"
										class="flex-1 py-1.5 px-2 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-800 text-[11px] font-bold flex items-center justify-center gap-1.5 transition active:scale-95 border border-teal-200/70"
									>
										<svg class="w-3.5 h-3.5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
										</svg>
										<span>Call ({{ cust.mobile_no }})</span>
									</a>

									<!-- WhatsApp Reminder Button -->
									<a
										v-if="cust.mobile_no"
										:href="getWhatsAppLink(cust)"
										target="_blank"
										class="flex-1 py-1.5 px-2 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-[11px] font-bold flex items-center justify-center gap-1.5 transition active:scale-95 border border-emerald-200/70"
									>
										<span class="text-xs">💬</span>
										<span>WhatsApp</span>
									</a>

									<!-- Toggle Invoices Detail Button -->
									<button
										type="button"
										@click="toggleInvoices(cust.customer)"
										class="py-1.5 px-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-bold flex items-center gap-1 transition cursor-pointer"
									>
										<span>{{ cust.invoices_count }} Invs</span>
										<svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': expandedCustomers[cust.customer] }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
										</svg>
									</button>
								</div>

								<!-- Invoices Expandable Breakdown -->
								<div v-if="expandedCustomers[cust.customer]" class="pt-2 border-t border-slate-100 space-y-1.5 bg-slate-50/80 -mx-4 -mb-4 p-3 rounded-b-3xl">
									<div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Unpaid Invoices Breakdown:</div>
									<div
										v-for="inv in cust.invoices"
										:key="inv.name"
										class="flex items-center justify-between text-xs py-1 px-2 rounded-xl bg-white border border-slate-100"
									>
										<div>
											<span class="font-bold text-slate-800 font-mono">{{ inv.name }}</span>
											<span class="text-[10px] text-slate-400 ml-1.5">Due: {{ inv.due_date }}</span>
										</div>
										<div class="text-right">
											<span class="font-black text-slate-900 font-mono">₹{{ formatCurrency(inv.outstanding_amount) }}</span>
											<span
												v-if="inv.is_overdue"
												class="text-[9px] font-bold text-rose-600 block"
											>
												{{ inv.overdue_days }}d overdue
											</span>
											<span v-else class="text-[9px] font-medium text-emerald-600 block">
												Not due
											</span>
										</div>
									</div>
								</div>
							</div>

							<!-- Prev / Next Pagination Bar for Customers -->
							<div v-if="totalCustomersPages > 1 || totalCustomersCount > 10" class="bg-white rounded-2xl p-3 shadow-xs border border-slate-200/80 flex items-center justify-between gap-2">
								<button
									type="button"
									:disabled="customersPage <= 1"
									@click="changeCustomersPage(customersPage - 1)"
									class="px-3 py-1.5 rounded-xl text-[11px] font-bold flex items-center gap-1 transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed bg-slate-100 hover:bg-slate-200 text-slate-700 active:scale-95"
								>
									<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
									</svg>
									<span>Prev</span>
								</button>

								<div class="text-center">
									<span class="text-[11px] font-bold text-slate-700 block">
										Page {{ customersPage }} of {{ totalCustomersPages }}
									</span>
									<span class="text-[10px] text-slate-400">
										{{ customersRangeStart }}–{{ customersRangeEnd }} of {{ totalCustomersCount }}
									</span>
								</div>

								<button
									type="button"
									:disabled="customersPage >= totalCustomersPages"
									@click="changeCustomersPage(customersPage + 1)"
									class="px-3 py-1.5 rounded-xl text-[11px] font-bold flex items-center gap-1 transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed bg-teal-600 hover:bg-teal-700 text-white active:scale-95"
								>
									<span>Next</span>
									<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
									</svg>
								</button>
							</div>

							<!-- Empty State -->
							<div
								v-if="!isLoading && customerList.length === 0"
								class="bg-white rounded-3xl p-8 border border-dashed border-slate-200 text-center space-y-2 shadow-xs"
							>
								<div class="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center mx-auto text-xl">
									🎉
								</div>
								<h3 class="text-sm font-bold text-slate-800">No Outstanding Dues</h3>
								<p class="text-xs text-slate-500">
									All customer invoices for this rep are fully paid and clear.
								</p>
							</div>
						</div>

					</div>
				</template>

			</main>

			<!-- Bottom Navigation -->
			<BottomNavBar
				active-tab="team_sales"
				:show-eem="!!employee?.is_sales_person"
				:is-trip-active="isTripActive"
				@open-history="openHistory"
				@open-profile="openProfile"
			/>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { useRouter } from "vue-router"
import { call } from "frappe-ui"
import { employeeResource } from "@/data/employee"
import { todayEemResource } from "@/data/eem"
import BottomNavBar from "@/components/BottomNavBar.vue"

const router = useRouter()

const employee = computed(() => employeeResource.data)
const isTripActive = computed(() => !!todayEemResource.data?.trip_active)

function openHistory() {
	router.push("/eem/history")
}

function openProfile() {
	router.push("/?openProfile=1")
}

// State
const activeTab = ref("billing") // "billing" | "outstanding"
const selectedSalesPerson = ref("all")
const selectedPeriod = ref("current_month")
const selectedAgingBucket = ref("all")
const searchQuery = ref("")
const sortBy = ref("outstanding_desc")
const customFromDate = ref("")
const customToDate = ref("")
const isLoading = ref(false)

const pageSizeOptions = [10, 20, 50, 100]
const invoicesPage = ref(1)
const invoicesPageSize = ref(10)
const invoiceCustomerFilter = ref("all")
const invoiceSearchQuery = ref("")
const customersPage = ref(1)
const customersPageSize = ref(10)

const invoicesSectionRef = ref(null)
const customersSectionRef = ref(null)

const salesData = ref(null)
const outstandingData = ref(null)
const expandedCustomers = ref({})

// Periods list
const periods = [
	{ label: "Current Month", value: "current_month" },
	{ label: "Today", value: "today" },
	{ label: "This Week", value: "this_week" },
	{ label: "This Quarter", value: "this_quarter" },
	{ label: "This Year", value: "this_year" },
	{ label: "Custom", value: "custom" },
]

// Computed Getters
const isSupervisorUser = computed(() => {
	if (!employee.value) return false
	return Boolean(employee.value.is_supervisor || employee.value.subordinates_count > 0)
})

const teamMembers = computed(() => {
	if (salesData.value?.team_members) return salesData.value.team_members
	if (outstandingData.value?.team_members) return outstandingData.value.team_members
	return []
})

const hasCurrentUserSp = computed(() => {
	return teamMembers.value.some((m) => m.is_current_user)
})

const subordinatesOnly = computed(() => {
	return teamMembers.value.filter((m) => !m.is_current_user)
})

const activeMemberLabel = computed(() => {
	if (selectedSalesPerson.value === "all") return "All Team Combined"
	if (selectedSalesPerson.value === "me") return "My Own (Current User)"
	const m = teamMembers.value.find((x) => x.sales_person === selectedSalesPerson.value)
	return m ? m.sales_person_name : selectedSalesPerson.value
})

const activePeriodLabel = computed(() => {
	const p = periods.find((x) => x.value === selectedPeriod.value)
	return p ? p.label : "Period"
})

const salesSummary = computed(() => salesData.value?.summary || {})
const outstandingSummary = computed(() => outstandingData.value?.summary || {})
const customerList = computed(() => outstandingData.value?.customers || [])

const rawInvoices = computed(() => salesData.value?.recent_invoices || [])
const rawInvoicesCount = computed(() => rawInvoices.value.length)

const invoiceCustomerOptions = computed(() => {
	const map = {}
	for (const inv of rawInvoices.value) {
		const key = inv.customer || inv.customer_name
		if (!key) continue
		if (!map[key]) {
			map[key] = {
				customer: key,
				customer_name: inv.customer_name || key,
				count: 0,
			}
		}
		map[key].count++
	}
	return Object.values(map).sort((a, b) => a.customer_name.localeCompare(b.customer_name))
})

const selectedCustomerLabel = computed(() => {
	if (invoiceCustomerFilter.value === "all") return "All Customers"
	const opt = invoiceCustomerOptions.value.find((c) => c.customer === invoiceCustomerFilter.value)
	return opt ? opt.customer_name : invoiceCustomerFilter.value
})

const filteredInvoices = computed(() => {
	let list = rawInvoices.value

	if (invoiceCustomerFilter.value && invoiceCustomerFilter.value !== "all") {
		list = list.filter((inv) => inv.customer === invoiceCustomerFilter.value || inv.customer_name === invoiceCustomerFilter.value)
	}

	if (invoiceSearchQuery.value && invoiceSearchQuery.value.trim()) {
		const q = invoiceSearchQuery.value.trim().toLowerCase()
		list = list.filter(
			(inv) =>
				(inv.customer_name && inv.customer_name.toLowerCase().includes(q)) ||
				(inv.customer && inv.customer.toLowerCase().includes(q)) ||
				(inv.name && inv.name.toLowerCase().includes(q)) ||
				(inv.sales_person_name && inv.sales_person_name.toLowerCase().includes(q))
		)
	}

	return list
})

const totalInvoicesCount = computed(() => filteredInvoices.value.length)
const totalInvoicesPages = computed(() => Math.max(1, Math.ceil(totalInvoicesCount.value / invoicesPageSize.value)))
const invoicesRangeStart = computed(() => (totalInvoicesCount.value === 0 ? 0 : (invoicesPage.value - 1) * invoicesPageSize.value + 1))
const invoicesRangeEnd = computed(() => Math.min(invoicesPage.value * invoicesPageSize.value, totalInvoicesCount.value))

const visibleInvoices = computed(() => {
	const start = (invoicesPage.value - 1) * invoicesPageSize.value
	return filteredInvoices.value.slice(start, start + invoicesPageSize.value)
})

function clearInvoiceCustomerFilter() {
	invoiceCustomerFilter.value = "all"
	invoiceSearchQuery.value = ""
	invoicesPage.value = 1
}

watch(invoiceCustomerOptions, (newOptions) => {
	if (invoiceCustomerFilter.value !== "all") {
		const exists = newOptions.some((o) => o.customer === invoiceCustomerFilter.value)
		if (!exists) {
			invoiceCustomerFilter.value = "all"
			invoicesPage.value = 1
		}
	}
})

const totalCustomersCount = computed(() => customerList.value.length)
const totalCustomersPages = computed(() => Math.max(1, Math.ceil(totalCustomersCount.value / customersPageSize.value)))
const customersRangeStart = computed(() => (totalCustomersCount.value === 0 ? 0 : (customersPage.value - 1) * customersPageSize.value + 1))
const customersRangeEnd = computed(() => Math.min(customersPage.value * customersPageSize.value, totalCustomersCount.value))

const visibleCustomers = computed(() => {
	const start = (customersPage.value - 1) * customersPageSize.value
	return customerList.value.slice(start, start + customersPageSize.value)
})

const agingBuckets = computed(() => {
	const ag = outstandingSummary.value?.aging || {}
	return [
		{ label: "All", value: "all", amount: outstandingSummary.value?.total_outstanding || 0 },
		{ label: "Not Due", value: "not_due", amount: ag.not_due || 0 },
		{ label: "1-30 Days", value: "1-30", amount: ag.days_1_30 || 0 },
		{ label: "31-60 Days", value: "31-60", amount: ag.days_31_60 || 0 },
		{ label: "61-90 Days", value: "61-90", amount: ag.days_61_90 || 0 },
		{ label: "90+ Days", value: "90+", amount: ag.days_90_plus || 0 },
	]
})

// Methods
function goBack() {
	router.push("/")
}

function scrollToSection(sectionRef) {
	if (sectionRef.value) {
		sectionRef.value.scrollIntoView({ behavior: "smooth", block: "start" })
	}
}

function changeInvoicesPage(page) {
	if (page < 1 || page > totalInvoicesPages.value) return
	invoicesPage.value = page
	scrollToSection(invoicesSectionRef)
}

function onInvoicesPageSizeChange() {
	invoicesPage.value = 1
}

function changeCustomersPage(page) {
	if (page < 1 || page > totalCustomersPages.value) return
	customersPage.value = page
	scrollToSection(customersSectionRef)
}

function onCustomersPageSizeChange() {
	customersPage.value = 1
}

function selectSalesPerson(sp) {
	selectedSalesPerson.value = sp
	invoicesPage.value = 1
	customersPage.value = 1
	refreshActiveView()
}

function selectPeriod(p) {
	selectedPeriod.value = p
	invoicesPage.value = 1
	fetchSalesData()
}

function selectAgingBucket(b) {
	selectedAgingBucket.value = b
	customersPage.value = 1
	fetchOutstandingData()
}

let searchTimer = null
function debouncedOutstandingSearch() {
	clearTimeout(searchTimer)
	searchTimer = setTimeout(() => {
		customersPage.value = 1
		fetchOutstandingData()
	}, 350)
}

function toggleInvoices(custId) {
	expandedCustomers.value[custId] = !expandedCustomers.value[custId]
}

function getInitials(name) {
	if (!name) return "SP"
	const parts = name.trim().split(" ")
	if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
	return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

function formatCurrency(val) {
	if (val === null || val === undefined) return "0"
	return Number(val).toLocaleString("en-IN", { maximumFractionDigits: 2 })
}

function formatCompact(val) {
	if (!val) return "0"
	const num = Number(val)
	if (num >= 10000000) return (num / 10000000).toFixed(1) + "Cr"
	if (num >= 100000) return (num / 100000).toFixed(1) + "L"
	if (num >= 1000) return (num / 1000).toFixed(1) + "K"
	return num.toFixed(0)
}

function getWhatsAppLink(cust) {
	if (!cust.mobile_no) return "#"
	let phone = cust.mobile_no.replace(/\D/g, "")
	if (phone.length === 10) {
		phone = "91" + phone
	}
	const msg = encodeURIComponent(
		`Dear ${cust.customer_name}, Greetings from ${employee.value?.company_name || 'our team'}. This is a gentle reminder regarding your outstanding payment of ₹${formatCurrency(cust.total_outstanding)}. Kindly arrange for the settlement at your earliest convenience. Thank you!`
	)
	return `https://wa.me/${phone}?text=${msg}`
}

async function fetchSalesData() {
	isLoading.value = true
	invoicesPage.value = 1
	try {
		const res = await call("tq_erphr.pwa_api.get_supervisor_team_sales_summary", {
			period: selectedPeriod.value,
			from_date: customFromDate.value || null,
			to_date: customToDate.value || null,
			sales_person: selectedSalesPerson.value,
		})
		if (res) {
			salesData.value = res.message || res
		}
	} catch (e) {
		console.error("Error fetching sales summary:", e)
	} finally {
		isLoading.value = false
	}
}

async function fetchOutstandingData() {
	isLoading.value = true
	customersPage.value = 1
	try {
		const res = await call("tq_erphr.pwa_api.get_supervisor_team_outstanding", {
			sales_person: selectedSalesPerson.value,
			aging_bucket: selectedAgingBucket.value,
			search_term: searchQuery.value || null,
			sort_by: sortBy.value,
			limit: 500,
		})
		if (res) {
			outstandingData.value = res.message || res
		}
	} catch (e) {
		console.error("Error fetching outstanding data:", e)
	} finally {
		isLoading.value = false
	}
}

function refreshActiveView() {
	invoicesPage.value = 1
	customersPage.value = 1
	if (activeTab.value === "billing") {
		fetchSalesData()
	} else {
		fetchOutstandingData()
	}
}

onMounted(async () => {
	if (!employeeResource.data) {
		await employeeResource.fetch()
	}
	if (!todayEemResource.data && !todayEemResource.loading) {
		todayEemResource.fetch()
	}
	fetchSalesData()
	fetchOutstandingData()
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
