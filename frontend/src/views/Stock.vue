<template>
	<div class="min-h-screen bg-slate-100/80 flex flex-col font-sans pb-24">
		<!-- Main Mobile Container -->
		<div class="w-full max-w-md mx-auto flex-1 flex flex-col min-h-screen bg-slate-100/80 sm:shadow-lg sm:border-x sm:border-slate-200">
			<!-- Header -->
			<header class="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 pt-3 pb-3 sm:px-5 shadow-2xs">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-2.5">
						<button
							type="button"
							@click="goBack"
							class="w-9 h-9 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center transition-colors cursor-pointer"
							title="Go Back"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
							</svg>
						</button>
						<div class="min-w-0">
							<h1 class="text-base font-black text-slate-900 leading-tight truncate">Stock & Inventory</h1>
							<p class="text-[11px] text-teal-700 font-medium truncate">{{ employee?.company || 'Live Item Balances' }}</p>
						</div>
					</div>

					<button
						type="button"
						@click="refreshStock"
						:disabled="isLoading"
						class="w-9 h-9 rounded-2xl bg-teal-50 hover:bg-teal-100 text-teal-700 border border-teal-200/80 flex items-center justify-center transition-colors cursor-pointer"
						title="Refresh Stock Data"
					>
						<svg
							class="w-4 h-4 transition-transform duration-500"
							:class="{ 'animate-spin': isLoading }"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
						</svg>
					</button>
				</div>
			</header>

			<!-- Overview Dashboard KPI Cards -->
			<div class="px-4 pt-3.5 sm:px-5 space-y-2">
				<div class="grid grid-cols-3 gap-2">
					<!-- Card 1: Total Items -->
					<div class="bg-white p-3 rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-bold text-teal-800 uppercase tracking-wider">Total Items</span>
							<span class="text-xs">📦</span>
						</div>
						<div class="mt-1 flex items-baseline space-x-1">
							<span class="text-base font-black text-slate-900 font-mono">{{ dashboardStats.total_items || stockItems.length }}</span>
							<span class="text-[9px] text-slate-500 font-medium">items</span>
						</div>
					</div>

					<!-- Card 2: Warehouses -->
					<div class="bg-white p-3 rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-bold text-cyan-800 uppercase tracking-wider">Warehouses</span>
							<span class="text-xs">🏢</span>
						</div>
						<div class="mt-1 flex items-baseline space-x-1">
							<span class="text-base font-black text-slate-900 font-mono">{{ dashboardStats.total_warehouses || warehousesList.length }}</span>
							<span class="text-[9px] text-slate-500 font-medium">active</span>
						</div>
					</div>

					<!-- Card 3: Total Stock Units -->
					<div class="bg-white p-3 rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all">
						<div class="flex items-center justify-between">
							<span class="text-[10px] font-bold text-emerald-800 uppercase tracking-wider">Total Units</span>
							<span class="text-xs">📊</span>
						</div>
						<div class="mt-1 flex items-baseline space-x-1">
							<span class="text-base font-black text-emerald-800 font-mono">{{ formatQty(dashboardStats.total_actual_qty) }}</span>
							<span class="text-[9px] text-slate-500 font-medium">units</span>
						</div>
					</div>
				</div>

				<!-- In-Transit Global Banner (If in-transit units exist) -->
				<div
					v-if="Number(dashboardStats.total_in_transit_qty) > 0"
					class="px-3 py-1.5 bg-amber-50/90 border border-amber-200/80 rounded-2xl flex items-center justify-between text-xs text-amber-950 shadow-2xs"
				>
					<div class="flex items-center space-x-1.5 font-semibold">
						<span class="text-sm">🚚</span>
						<span>In-Transit Inventory:</span>
					</div>
					<span class="font-mono font-black text-amber-900 bg-amber-200/80 px-2 py-0.5 rounded-lg text-xs">
						{{ formatQty(dashboardStats.total_in_transit_qty) }} units
					</span>
				</div>
			</div>

			<!-- Search Input & Warehouse Filter Section (Inside Clean Card) -->
			<div class="px-4 pt-2.5 sm:px-5">
				<div class="bg-white p-3 rounded-2xl border border-slate-200/90 shadow-sm space-y-2">
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
						</div>
						<input
							type="text"
							v-model="searchQuery"
							@input="onSearchInput"
							placeholder="Search item code, name, brand, or desc..."
							class="w-full pl-9 pr-8 py-2.5 bg-slate-50 focus:bg-white text-xs text-slate-800 rounded-xl border border-slate-200/80 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition shadow-2xs"
						/>
						<button
							v-if="searchQuery"
							@click="clearSearch"
							class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-slate-400 hover:text-slate-600"
							title="Clear Search"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</div>

					<!-- Warehouse Dropdown Selector with Reset -->
					<div class="flex items-center gap-2 pt-1">
						<div class="relative flex-1">
							<select
								v-model="selectedWarehouse"
								@change="onWarehouseChange"
								class="w-full pl-8 pr-8 py-2 bg-slate-50 hover:bg-slate-100/80 focus:bg-white text-xs font-semibold text-slate-700 rounded-xl border border-slate-200/80 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-600 transition cursor-pointer appearance-none truncate"
							>
								<option value="all">🏢 All Warehouses ({{ warehousesList.length }})</option>
								<option v-for="wh in warehousesList" :key="wh" :value="wh">
									🏢 {{ wh }}
								</option>
							</select>
							<div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-teal-700 font-bold text-xs">
								🏢
							</div>
							<div class="absolute inset-y-0 right-0 pr-2.5 flex items-center pointer-events-none text-slate-400">
								<svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
								</svg>
							</div>
						</div>

						<button
							v-if="selectedWarehouse !== 'all' || searchQuery"
							type="button"
							@click="resetFilters"
							class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-semibold transition cursor-pointer flex-shrink-0"
							title="Reset Filters"
						>
							Reset
						</button>
					</div>
				</div>
			</div>

			<!-- Main Content Area -->
			<main class="flex-1 px-4 pt-3 pb-3 sm:px-5 space-y-3">
				<!-- Context / Active Indicator -->
				<div class="flex items-center justify-between text-xs px-1 text-slate-500">
					<span class="font-medium text-slate-600">
						<template v-if="searchQuery">
							{{ stockItems.length }} result{{ stockItems.length === 1 ? '' : 's' }} for "{{ searchQuery }}"
						</template>
						<template v-else-if="selectedWarehouse !== 'all'">
							Filtered by: <strong class="text-teal-800">{{ selectedWarehouse }}</strong>
						</template>
						<template v-else>
							Consolidated Inventory Items
						</template>
					</span>
					<span class="text-[11px] font-bold font-mono text-teal-700">
						{{ stockItems.length }} / {{ totalCount }} items
					</span>
				</div>

				<!-- Loading State -->
				<div v-if="isLoading && stockItems.length === 0" class="py-16 text-center space-y-3">
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-teal-500 border-t-transparent"></div>
					<h3 class="text-sm font-bold text-slate-900">Loading Stock Balances...</h3>
					<p class="text-xs text-slate-500">Fetching live inventory quantities from ERP</p>
				</div>

				<!-- Empty State -->
				<div
					v-else-if="!isLoading && stockItems.length === 0"
					class="py-12 bg-white rounded-3xl border border-dashed border-slate-200 text-center p-6 space-y-3 shadow-sm"
				>
					<div class="w-12 h-12 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center mx-auto">
						<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
						</svg>
					</div>
					<h3 class="text-sm font-bold text-slate-800">No Stock Records Found</h3>
					<p class="text-xs text-slate-500 max-w-xs mx-auto">
						<template v-if="searchQuery || selectedWarehouse !== 'all'">
							No stock balances match your search query or warehouse filter.
						</template>
						<template v-else>
							No item bins or stock ledger balances have been recorded yet.
						</template>
					</p>
					<div class="pt-2 flex justify-center">
						<button
							v-if="searchQuery || selectedWarehouse !== 'all'"
							@click="resetFilters"
							class="px-4 py-2 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition cursor-pointer"
						>
							Clear Filters
						</button>
					</div>
				</div>

				<!-- Single Item Cards with Warehouse Breakdown -->
				<div v-else class="space-y-3">
					<div
						v-for="item in stockItems"
						:key="item.item_code"
						class="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-sm hover:shadow-md hover:border-teal-300 transition-all relative overflow-hidden space-y-3"
					>
						<!-- Top Row: Name, Code & Multi-Warehouse Tag -->
						<div class="flex items-start justify-between">
							<div class="space-y-1 min-w-0 pr-2">
								<h3 class="text-sm font-bold text-slate-900 leading-tight">
									{{ item.item_name || item.item_code }}
								</h3>
								<div class="flex items-center space-x-1.5 text-[10px] text-slate-500 font-medium flex-wrap">
									<span class="font-mono bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded text-[9px] font-bold">{{ item.item_code }}</span>
									<span v-if="item.item_group" class="text-slate-600">• {{ item.item_group }}</span>
									<span v-if="item.stock_uom">• UOM: {{ item.stock_uom }}</span>
								</div>
							</div>

							<!-- Warehouse Count Badge -->
							<div class="flex flex-col items-end flex-shrink-0">
								<span
									class="px-2 py-0.5 rounded-lg text-[9px] font-bold border truncate"
									:class="item.warehouse_count > 1 ? 'bg-teal-50 text-teal-800 border-teal-200/80' : 'bg-slate-50 text-slate-700 border-slate-200'"
								>
									🏢 {{ item.warehouse_count }} {{ item.warehouse_count === 1 ? 'Warehouse' : 'Warehouses' }}
								</span>
							</div>
						</div>

						<!-- Aggregated Quantities Bar: Actual Qty, Available Qty & In Transit Qty -->
						<div class="pt-2 border-t border-slate-100 grid grid-cols-3 gap-1.5 text-center">
							<!-- Total Actual Qty -->
							<div class="bg-slate-50/90 p-2 rounded-xl border border-slate-200/70">
								<span class="text-[9px] text-slate-500 font-semibold block uppercase">Actual Qty</span>
								<div class="mt-1 flex items-center justify-center space-x-1">
									<span
										class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg text-xs font-black font-mono border shadow-2xs truncate"
										:class="Number(item.actual_qty) > 0 ? 'bg-emerald-100/90 text-emerald-950 border-emerald-300' : 'bg-rose-100/90 text-rose-950 border-rose-300'"
									>
										<span :class="Number(item.actual_qty) > 0 ? 'w-1.5 h-1.5 rounded-full bg-emerald-600 shrink-0' : 'w-1.5 h-1.5 rounded-full bg-rose-600 shrink-0'"></span>
										<span>{{ formatQty(item.actual_qty) }}</span>
									</span>
								</div>
							</div>

							<!-- Total Available Qty (Projected) -->
							<div class="bg-slate-50/90 p-2 rounded-xl border border-slate-200/70">
								<span class="text-[9px] text-slate-500 font-semibold block uppercase">Available</span>
								<div class="mt-1 flex items-center justify-center space-x-1">
									<span
										class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg text-xs font-black font-mono border shadow-2xs truncate"
										:class="Number(item.projected_qty) > 0 ? 'bg-cyan-100/90 text-cyan-950 border-cyan-300' : 'bg-slate-100 text-slate-700 border-slate-300'"
									>
										<span :class="Number(item.projected_qty) > 0 ? 'w-1.5 h-1.5 rounded-full bg-cyan-600 shrink-0' : 'w-1.5 h-1.5 rounded-full bg-slate-400 shrink-0'"></span>
										<span>{{ formatQty(item.projected_qty) }}</span>
									</span>
								</div>
							</div>

							<!-- In Transit Qty -->
							<div class="bg-slate-50/90 p-2 rounded-xl border border-slate-200/70">
								<span class="text-[9px] text-slate-500 font-semibold block uppercase">In Transit</span>
								<div class="mt-1 flex items-center justify-center space-x-1">
									<span
										class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg text-xs font-black font-mono border shadow-2xs truncate"
										:class="Number(item.in_transit_qty) > 0 ? 'bg-amber-100/90 text-amber-950 border-amber-300 ring-1 ring-amber-400/20' : 'bg-slate-100 text-slate-500 border-slate-200'"
									>
										<span v-if="Number(item.in_transit_qty) > 0" class="text-[10px] shrink-0">🚚</span>
										<span v-else class="w-1.5 h-1.5 rounded-full bg-slate-300 shrink-0"></span>
										<span>{{ formatQty(item.in_transit_qty) }}</span>
									</span>
								</div>
							</div>
						</div>

						<!-- Warehouse Breakdown List (Compact in Card) -->
						<div v-if="item.warehouses && item.warehouses.length > 0" class="pt-2 border-t border-slate-100 space-y-1.5">
							<div class="flex items-center justify-between text-[10px] font-bold text-slate-500 uppercase tracking-wider">
								<span>Warehouse Breakdown</span>
								<span class="text-[9px] font-normal lowercase text-slate-400">Actual / Available</span>
							</div>

							<div class="space-y-1 bg-slate-50/90 p-2.5 rounded-xl border border-slate-200/70">
								<div
									v-for="wh in item.warehouses"
									:key="wh.bin_name || wh.warehouse"
									class="flex items-center justify-between text-xs py-0.5"
								>
									<span class="font-medium text-slate-700 truncate pr-2 flex items-center space-x-1">
										<span class="text-[11px]">🏢</span>
										<span class="truncate">{{ wh.warehouse }}</span>
									</span>
									<div class="flex items-center space-x-2 shrink-0 font-mono">
										<span
											class="px-2 py-0.5 rounded text-[11px] font-bold"
											:class="Number(wh.actual_qty) > 0 ? 'bg-emerald-100 text-emerald-900' : 'bg-slate-200 text-slate-600'"
										>
											{{ formatQty(wh.actual_qty) }} {{ item.stock_uom }}
										</span>
										<span class="text-[10px] text-teal-700 font-semibold">
											(Avail: {{ formatQty(wh.projected_qty) }})
										</span>
									</div>
								</div>
							</div>
						</div>

						<!-- Action Footer -->
						<div class="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
							<div class="text-[11px] text-slate-500 font-medium flex items-center gap-1.5">
								<span>{{ item.warehouses?.length || 1 }} warehouse location{{ (item.warehouses?.length || 1) === 1 ? '' : 's' }}</span>
								<span v-if="Number(item.in_transit_qty) > 0" class="text-amber-800 font-bold text-[10px] flex items-center gap-0.5">
									• 🚚 {{ formatQty(item.in_transit_qty) }} in transit
								</span>
							</div>

							<button
								type="button"
								@click="openItemDetails(item)"
								class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-semibold transition cursor-pointer flex items-center space-x-1"
							>
								<span>Full Details</span>
								<svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Load More Button -->
					<div v-if="hasMore" class="pt-3 pb-2 text-center">
						<button
							@click="loadMoreStock"
							:disabled="isLoadingMore"
							class="w-full py-3 px-4 text-xs font-bold text-teal-800 bg-white hover:bg-teal-50/80 active:bg-teal-100 border border-teal-200/80 rounded-2xl transition-all duration-200 flex items-center justify-center space-x-2 shadow-xs hover:border-teal-300 cursor-pointer"
						>
							<svg v-if="isLoadingMore" class="w-4 h-4 animate-spin text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							<span>{{ isLoadingMore ? 'Loading more items...' : `View More Items (Showing ${stockItems.length} of ${totalCount})` }}</span>
						</button>
					</div>
				</div>
			</main>

			<!-- Bottom Navigation -->
			<BottomNavBar
				active-tab="stock"
				:show-eem="!!employee?.is_sales_person"
				:is-trip-active="isTripActive"
				@open-history="openHistory"
				@open-profile="openProfile"
			/>
		</div>

		<!-- Item Details Modal -->
		<Dialog v-model="showDetailsModal">
			<template #body-title>
				<div class="flex items-center space-x-2.5">
					<div class="w-8 h-8 rounded-full bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
						</svg>
					</div>
					<div>
						<h2 class="text-base font-bold text-slate-900 leading-tight">Item Stock Profile</h2>
						<p class="text-[10px] text-slate-500">{{ selectedItem?.item_code }}</p>
					</div>
				</div>
			</template>
			<template #body-content>
				<div v-if="selectedItem" class="mt-2 space-y-3.5 max-h-96 overflow-y-auto pr-1">
					<!-- Title Card -->
					<div class="p-3.5 rounded-2xl bg-gradient-to-br from-teal-50 to-emerald-50/40 border border-teal-200/80">
						<div class="flex items-start justify-between">
							<div>
								<h3 class="text-sm font-bold text-slate-900 leading-snug">{{ selectedItem.item_name || selectedItem.item_code }}</h3>
								<p class="text-xs text-teal-700 font-mono mt-0.5">{{ selectedItem.item_code }}</p>
							</div>
							<span class="px-2 py-0.5 rounded-lg text-[10px] font-bold bg-white text-teal-800 border border-teal-200 shadow-2xs">
								{{ selectedItem.item_group || 'Item' }}
							</span>
						</div>
					</div>

					<!-- Overall Quantities Snapshot -->
					<div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2.5">
						<div class="flex items-center justify-between text-xs font-bold text-slate-900">
							<span class="flex items-center gap-1.5">
								<span>📊 Consolidated Quantities</span>
							</span>
							<span class="px-2 py-0.5 rounded-lg text-[10px] font-mono font-bold bg-teal-50 text-teal-800 border border-teal-200">
								{{ selectedItem.warehouse_count }} {{ selectedItem.warehouse_count === 1 ? 'Warehouse' : 'Warehouses' }}
							</span>
						</div>

						<div class="grid grid-cols-3 gap-2">
							<div class="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
								<span class="text-[9px] text-slate-400 font-medium block uppercase">Actual Qty</span>
								<span class="text-sm font-black text-emerald-700 font-mono mt-0.5 block">
									{{ formatQty(selectedItem.actual_qty) }}
								</span>
							</div>
							<div class="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
								<span class="text-[9px] text-slate-400 font-medium block uppercase">Available</span>
								<span class="text-sm font-black text-cyan-800 font-mono mt-0.5 block">
									{{ formatQty(selectedItem.projected_qty) }}
								</span>
							</div>
							<div class="bg-white p-2.5 rounded-xl border border-slate-200/80 shadow-2xs">
								<span class="text-[9px] text-slate-400 font-medium block uppercase">In Transit</span>
								<span class="text-sm font-black text-amber-800 font-mono mt-0.5 block">
									{{ formatQty(selectedItem.in_transit_qty) }}
								</span>
							</div>
						</div>
					</div>

					<!-- In-Transit Purchase Invoices Section (if any) -->
					<div v-if="selectedItem.in_transit_records && selectedItem.in_transit_records.length > 0" class="bg-amber-50/70 rounded-2xl p-3.5 border border-amber-200/80 space-y-2.5 text-xs">
						<div class="flex items-center justify-between">
							<span class="font-bold text-amber-950 flex items-center gap-1.5">
								<span class="text-sm">🚚</span>
								<span>In-Transit Shipments ({{ selectedItem.in_transit_records.length }})</span>
							</span>
							<span class="px-2 py-0.5 rounded-full bg-amber-200/90 text-amber-950 font-mono font-bold text-[10px]">
								+{{ formatQty(selectedItem.in_transit_qty) }} {{ selectedItem.stock_uom }}
							</span>
						</div>

						<div class="space-y-1.5">
							<div
								v-for="(tr, idx) in selectedItem.in_transit_records"
								:key="tr.purchase_invoice_number || idx"
								class="p-2.5 bg-white rounded-xl border border-amber-200/60 flex items-start justify-between gap-2 shadow-2xs"
							>
								<div class="space-y-0.5">
									<div class="font-bold text-slate-800 text-xs flex items-center gap-1.5">
										<span class="font-mono text-teal-800">{{ tr.purchase_invoice_number }}</span>
										<span v-if="tr.date_of_purchase" class="text-[10px] text-slate-500 font-normal">• {{ tr.date_of_purchase }}</span>
									</div>
									<div class="text-[11px] text-slate-600">
										<span class="font-medium text-slate-700">Supplier:</span> {{ tr.supplier_name || tr.supplier || 'N/A' }}
									</div>
								</div>
								<span class="font-mono font-black text-amber-900 bg-amber-100 px-2 py-1 rounded-lg text-xs shrink-0 border border-amber-300/60">
									+{{ formatQty(tr.qty) }} {{ selectedItem.stock_uom }}
								</span>
							</div>
						</div>
					</div>

					<!-- Warehouse-by-Warehouse Table -->
					<div class="space-y-2">
						<h4 class="text-xs font-bold text-slate-800 flex items-center justify-between">
							<span>Warehouse Breakdown</span>
							<span class="text-[10px] font-mono text-slate-400">{{ (selectedItem.warehouses || []).length }} recorded</span>
						</h4>

						<div class="space-y-2">
							<div
								v-for="wh in selectedItem.warehouses"
								:key="wh.bin_name || wh.warehouse"
								class="p-3 rounded-2xl bg-slate-50 border border-slate-100 space-y-2"
							>
								<div class="flex items-center justify-between text-xs">
									<span class="font-bold text-slate-900 flex items-center space-x-1">
										<span>🏢</span>
										<span>{{ wh.warehouse }}</span>
									</span>
									<span class="font-mono text-[11px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-md">
										{{ formatQty(wh.actual_qty) }} {{ selectedItem.stock_uom }}
									</span>
								</div>

								<div class="grid grid-cols-2 gap-2 text-[10px] text-slate-600 bg-white p-2 rounded-xl border border-slate-100">
									<div>
										<span class="text-slate-400 block uppercase">Available Qty</span>
										<span class="font-mono font-bold text-cyan-800">{{ formatQty(wh.projected_qty) }} {{ selectedItem.stock_uom }}</span>
									</div>
									<div>
										<span class="text-slate-400 block uppercase">Reserved Qty</span>
										<span class="font-mono font-bold" :class="Number(wh.reserved_qty) > 0 ? 'text-amber-700' : 'text-slate-700'">
											{{ formatQty(wh.reserved_qty) }} {{ selectedItem.stock_uom }}
										</span>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex items-center justify-end w-full pt-1">
					<Button
						variant="solid"
						@click="showDetailsModal = false"
						class="px-4 py-2 text-xs font-bold text-white bg-teal-600 hover:bg-teal-500 rounded-2xl cursor-pointer"
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
import { Dialog, Button, call } from "frappe-ui"
import BottomNavBar from "@/components/BottomNavBar.vue"
import { employeeResource } from "@/data/employee"
import { todayEemResource } from "@/data/eem"
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
const selectedWarehouse = ref("all")
const warehousesList = ref([])
const itemGroupsList = ref([])
const dashboardStats = ref({
	total_items: 0,
	total_warehouses: 0,
	total_actual_qty: 0,
	total_available_qty: 0,
	in_stock_items: 0,
})

// Stock Items Pagination
const stockItems = ref([])
const totalCount = ref(0)
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(false)

// Item Detail Modal
const showDetailsModal = ref(false)
const selectedItem = ref(null)

function formatQty(val) {
	if (val === null || val === undefined || isNaN(val)) return "0"
	const num = Number(val)
	return num % 1 !== 0 ? num.toFixed(2) : String(num)
}

function formatCurrency(val) {
	if (val === null || val === undefined || isNaN(val)) return "0"
	const num = Number(val)
	return num.toLocaleString("en-IN", {
		maximumFractionDigits: 2,
		minimumFractionDigits: num % 1 !== 0 ? 2 : 0,
	})
}

// Fetch Initial Stock Items
async function fetchStockItems() {
	isLoading.value = true
	try {
		const params = {
			limit: 20,
			limit_start: 0,
		}
		if (searchQuery.value && searchQuery.value.trim()) {
			params.search_term = searchQuery.value.trim()
		}
		if (selectedWarehouse.value && selectedWarehouse.value !== "all") {
			params.warehouse = selectedWarehouse.value
		}

		const res = await call("tq_erphr.pwa_api.get_stock_items", params)
		stockItems.value = res?.items || []
		totalCount.value = res?.total_count || stockItems.value.length
		hasMore.value = stockItems.value.length < totalCount.value
	} catch (err) {
		console.error("Failed to fetch stock items:", err)
		toast.error("Failed to load stock balances")
	} finally {
		isLoading.value = false
	}
}

// Load Next Batch of Stock Items
async function loadMoreStock() {
	if (isLoadingMore.value || !hasMore.value) return
	isLoadingMore.value = true
	try {
		const params = {
			limit: 20,
			limit_start: stockItems.value.length,
		}
		if (searchQuery.value && searchQuery.value.trim()) {
			params.search_term = searchQuery.value.trim()
		}
		if (selectedWarehouse.value && selectedWarehouse.value !== "all") {
			params.warehouse = selectedWarehouse.value
		}

		const res = await call("tq_erphr.pwa_api.get_stock_items", params)
		const newItems = res?.items || []
		stockItems.value = [...stockItems.value, ...newItems]
		totalCount.value = res?.total_count || totalCount.value
		hasMore.value = stockItems.value.length < totalCount.value
	} catch (err) {
		console.error("Failed to load more stock items:", err)
		toast.error("Failed to load more items")
	} finally {
		isLoadingMore.value = false
	}
}

// Fetch Warehouse & Group Meta Filters
async function fetchMetaFilters() {
	try {
		const res = await call("tq_erphr.pwa_api.get_stock_meta_filters")
		if (res) {
			warehousesList.value = res.warehouses || []
			itemGroupsList.value = res.item_groups || []
			if (res.stats) {
				dashboardStats.value = res.stats
			}
		}
	} catch (err) {
		console.warn("Could not fetch stock meta filters:", err)
	}
}

// Debounced Search Input
let searchTimer = null
function onSearchInput() {
	if (searchTimer) clearTimeout(searchTimer)
	searchTimer = setTimeout(() => {
		fetchStockItems()
	}, 250)
}

function clearSearch() {
	searchQuery.value = ""
	fetchStockItems()
}

function onWarehouseChange() {
	fetchStockItems()
}

function resetFilters() {
	searchQuery.value = ""
	selectedWarehouse.value = "all"
	fetchStockItems()
}

function refreshStock() {
	fetchStockItems()
	fetchMetaFilters()
}

function openItemDetails(item) {
	selectedItem.value = item
	showDetailsModal.value = true
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

onMounted(() => {
	if (!employeeResource.data && !employeeResource.loading) {
		employeeResource.fetch()
	}
	todayEemResource.fetch()
	fetchMetaFilters()
	fetchStockItems()
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
