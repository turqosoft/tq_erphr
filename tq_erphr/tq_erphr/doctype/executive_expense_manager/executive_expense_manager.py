# Copyright (c) 2025, Turqosoft Solutions Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tq_erphr.geo import street_distance, reverse_geocode

class ExecutiveExpenseManager(Document):
    def validate(self):
        self.calculate_site_distances()        
        self.calculate_totals()
        self.build_route_polyline()
        self.fill_location_names()
    
    def before_save(self):
        
        self.add_travel_expensetype_and_rate()
        
        if self.end_lat and self.end_long:
            self.fetch_site_location()
            self.calculate_site_distances()        
            self.calculate_totals()
            self.build_route_polyline()
            self.fill_location_names()
    
    def add_travel_expensetype_and_rate(self):
    
            hr_settings = frappe.get_single("HR Settings")
            self.travel_expense_type = hr_settings.travel_expense_type
            self.rate_per_km = hr_settings.rate_per_km
    
    
    
    
    def fetch_site_location(self):
            """Fetch employee check-in/out entries and populate Employee Site Tracking child table."""
            
            if self.employee_site_tracking:
                # Do not overwrite existing data
                return
                
            if not self.employee:
                frappe.throw("Employee is required before fetching site locations.")

            if not (self.start_time and self.end_time and self.date):
                frappe.throw("Start time, end time and date are required.")

            # Clear existing child rows so data doesn't duplicate
            self.employee_site_tracking = []

            start_datetime = f"{self.date} {self.start_time}"
            end_datetime = f"{self.date} {self.end_time}"

            # Fetch matching employee checkins
            checkins = frappe.get_all(
                "Employee Checkin",
                filters={
                    "employee": self.employee,
                    "time": ["between", [start_datetime, end_datetime]]
                },
                fields=["log_type", "time", "latitude", "longitude","customer","remarks"]
            )

            # Sort by timestamp
            checkins = sorted(checkins, key=lambda x: x.time)

            current_row = None

            for entry in checkins:

                # --- Handle CHECK-IN ---
                if entry.log_type in ("IN", "CHECKIN"):
                    current_row = self.append("employee_site_tracking", {})
                    current_row.checkin_time = entry.time
                    current_row.checkin_lat = entry.latitude
                    current_row.checkin_long = entry.longitude
                    current_row.remarks = entry.remarks
                    current_row.customer = entry.customer

                # --- Handle CHECK-OUT ---
                elif entry.log_type in ("OUT", "CHECKOUT"):
                    if current_row:
                        current_row.checkout_time = entry.time
                        current_row.checkout_lat = entry.latitude
                        current_row.checkout_long = entry.longitude
                        current_row = None  # close the row

            # frappe.msgprint("Site locations updated from Employee Checkin.")

                
                
    
    
    def create_expense_claim(self):
            # Prevent duplicate claims
            if frappe.db.exists(
                "Expense Claim",
                {"reference_name": self.name, "executive_expense_manager": self.name}
            ):
                frappe.throw("Expense Claim already created for this record.")

            if not self.employee:
                frappe.throw("Employee is mandatory to create Expense Claim.")

            expense_claim = frappe.new_doc("Expense Claim")
            expense_claim.employee = self.employee
            expense_claim.posting_date = frappe.utils.nowdate()
            expense_claim.company = frappe.defaults.get_user_default("Company")

          
            
          

            # ---------------- Travel Expense ----------------
            if self.total_travel_expense and self.total_travel_expense > 0:
                expense_claim.append("expenses", {
                    "expense_type": self.travel_expense_type,
                    "expense_date": self.date,
                    "amount": self.total_travel_expense,
                    # Link back to Executive Expense Manager
                    "executive_expense_manager": self.name,
                    "description": (
                        f"Travel expense: {self.total_distance} km "
                        f"@ {self.rate_per_km} per km"
                    )
                })

            # ---------------- Other Expenses ----------------
            for row in self.employee_expense_tracking:
                if row.amount and row.amount > 0:
                    expense_claim.append("expenses", {
                        "expense_type": row.expense_type,
                        "expense_date": self.date,
                        # Link back to Executive Expense Manager
                        "executive_expense_manager": self.name,
                        "amount": row.amount,
                        "description": row.description 
                    })

            expense_claim.insert(ignore_permissions=True)
            

            frappe.msgprint(
                f"Expense Claim <b>{expense_claim.name}</b> created successfully."
            )
            
  
    def calculate_totals(self):
        # 1. Total distance from Employee Site Tracking
        total_distance = 0
        for row in self.employee_site_tracking:
            total_distance += (row.actual_distance or 0)

        self.total_distance = total_distance

        # 2. Travel expense = total distance × rate_per_km
        rate = self.rate_per_km or 0
        self.total_travel_expense = total_distance * rate

        # 3. Total other expenses from Employee Expense Tracking
        total_other = 0
        for row in self.employee_expense_tracking:
            total_other += (row.amount or 0)

        self.total_other_expenses = total_other

        # 4. Grand total
        self.total_expense = self.total_travel_expense + self.total_other_expenses

    def calculate_site_distances(self):

        
        
            # Starting point for the first row
            prev_lat = self.start_lat
            prev_long = self.start_long

            for idx, row in enumerate(self.employee_site_tracking):

                # If check-in is missing → no distance
                if not (row.checkin_lat and row.checkin_long):
                    row.distance_travelled = 0
                    
                    continue
                
                if row.distance_travelled:
                    # Use existing distance if already calculated
                    prev_lat = row.checkin_lat
                    prev_long = row.checkin_long
                    continue

                # Calculate distance between previous → current check-in
                distance = street_distance(
                    prev_lat,
                    prev_long,
                    row.checkin_lat,
                    row.checkin_long
                )

                # Save distance
                row.distance_travelled = round(distance, 3)
                if not row.actual_distance:
                    row.actual_distance = round(distance, 3)

                # Update previous coordinates to current check-in (NOT checkout)
                prev_lat = row.checkin_lat
                prev_long = row.checkin_long

            # ---------- Last leg: last check-in → end point ----------
            if self.end_lat and self.end_long and self.employee_site_tracking:
                last = self.employee_site_tracking[-1]
                if last.checkin_lat and last.checkin_long:
                    last_leg = street_distance(
                        last.checkin_lat,
                        last.checkin_long,
                        self.end_lat,
                        self.end_long
                    )
                


   

        
    def fill_location_names(self):
        for row in self.employee_site_tracking:
            if row.checkin_lat and row.checkin_long:
                if not row.location_name:
                    row.location_name = reverse_geocode(row.checkin_lat, row.checkin_long)
                
                
                    
    @frappe.whitelist()           
    def build_route_polyline(self):
        coords = []
        features = []

        # ---------------- Helper to Add Marker ----------------
        def add_marker(lat, lon, name="", color="blue"):
            if lat and lon:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "name": name,
                        "marker-color": color,
                        "marker-size": "medium"
                    }
                })

        frappe.log_error(
            title="Build Route Polyline", 
            message="Building route polyline for Executive Expense Manager."
        )

        # ---------------- START POINT ----------------
        if self.start_lat and self.start_long:
            coords.append([self.start_long, self.start_lat])
            add_marker(
                self.start_lat,
                self.start_long,
                "Start Location",
                "#00cc44"     # green
            )

        segment_distances = []

        # ---------------- CHECK-IN MARKERS ONLY ----------------
        prev_lat = self.start_lat
        prev_long = self.start_long

        for idx, row in enumerate(self.employee_site_tracking, start=1):

            if not (row.checkin_lat and row.checkin_long):
                continue

            coords.append([row.checkin_long, row.checkin_lat])

            # Marker
            add_marker(
                row.checkin_lat,
                row.checkin_long,
                f"Check-in {idx}: {row.location_name or ''}",
                "#0066ff"    # blue
            )

            # Store segment distance (already calculated in row)
            if row.distance_travelled:
                segment_distances.append(row.distance_travelled)
            else:
                segment_distances.append(0)

            # Move pointer forward
            prev_lat = row.checkin_lat
            prev_long = row.checkin_long

        # ---------------- END POINT ----------------
        if self.end_lat and self.end_long:
            coords.append([self.end_long, self.end_lat])
            add_marker(
                self.end_lat,
                self.end_long,
                "End Location",
                "#ff3333"     # red
            )

        # ---------------- LINESTRING ROUTE ----------------
        if len(coords) >= 2:
            route_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords
                },
                "properties": {
                    "name": "Travel Route",
                    "stroke": "#333333",
                    "stroke-width": 3,

                    # JS will use this to draw distance labels
                    "segment_distances": segment_distances
                }
            }
            features.append(route_feature)

        # ---------------- FINAL GEOJSON ----------------
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        self.employee_route = frappe.as_json(geojson)






@frappe.whitelist()
def bulk_create_expense_claim(executive_expense_managers):

    if isinstance(executive_expense_managers, str):
        executive_expense_managers = frappe.parse_json(executive_expense_managers)

    eems = frappe.get_all(
        "Executive Expense Manager",
        filters={"name": ["in", executive_expense_managers]},
        fields=["name", "employee", "expense_claim_status"]
    )

    if not eems:
        frappe.throw("No valid records found.")

    # ---- Group EEMs by Employee ----
    employee_map = {}
    for row in eems:
        if row.expense_claim_status not in ("Not Created", "Cancelled"):
            continue
        employee_map.setdefault(row.employee, []).append(row.name)

    if not employee_map:
        frappe.throw("No eligible records to process.")

    created_claims = []

    # ---- One Expense Claim per Employee ----
    for employee, eem_names in employee_map.items():

        expense_claim = frappe.new_doc("Expense Claim")
        expense_claim.employee = employee
        expense_claim.posting_date = frappe.utils.nowdate()
        expense_claim.company = frappe.defaults.get_user_default("Company")

        for eem_name in eem_names:
            eem = frappe.get_doc("Executive Expense Manager", eem_name)

            # ---- Travel Expense ----
            if eem.total_travel_expense and eem.total_travel_expense > 0:
                expense_claim.append("expenses", {
                    "expense_type": eem.travel_expense_type,
                    "expense_date": eem.date,
                    "amount": eem.total_travel_expense,
                    "executive_expense_manager": eem.name,
                    "description": (
                        f"Travel: {eem.total_distance} km "
                        f"@ {eem.rate_per_km} per km"
                    )
                })

            # ---- Other Expenses ----
            for row in eem.employee_expense_tracking:
                if row.amount and row.amount > 0:
                    expense_claim.append("expenses", {
                        "expense_type": row.expense_type,
                        "expense_date": eem.date,
                        "amount": row.amount,
                        "executive_expense_manager": eem.name,
                        "description": row.description or ""
                    })

            # Update EEM status
            eem.expense_claim_status = "Processing"
            eem.save(ignore_permissions=True)

        expense_claim.insert(ignore_permissions=True)
        created_claims.append(expense_claim.name)

    return (
        f"Created {len(created_claims)} Expense Claim(s):<br>"
        + "<br>".join(created_claims)
    )




# ----------------------------
# Status Handling  Functions
# ----------------------------

def get_eem_names_from_expense_claim(doc):
    """Collect unique Executive Expense Manager names from Expense Claim rows"""
    eem_names = set()

    if not doc.expenses:
        return eem_names

    for row in doc.expenses:
        if row.executive_expense_manager:
            eem_names.add(row.executive_expense_manager)

    return eem_names


def update_eem_status(doc, status):
    """Update EEM status safely without triggering unnecessary hooks"""
    eem_names = get_eem_names_from_expense_claim(doc)

    for eem_name in eem_names:
        if not frappe.db.exists("Executive Expense Manager", eem_name):
            continue

        values = {
            "expense_claim_status": status
        }

        # Store Expense Claim reference if field exists
        if frappe.db.has_column("Executive Expense Manager", "expense_claim"):
            values["expense_claim"] = doc.name

        frappe.db.set_value(
            "Executive Expense Manager",
            eem_name,
            values,
            update_modified=False
        )


# ----------------------------
# Hook Handlers
# ----------------------------

def update_eem_on_draft_save(doc, method=None):
    """
    Triggered on after_save.
    Only update status when Expense Claim is in Draft.
    """
    if doc.docstatus != 0:
        return

    update_eem_status(doc, "Draft")


def update_eem_on_submit(doc, method=None):
    """
    Triggered on on_submit.
    """
    if doc.is_paid or doc.status == "Paid":
        update_eem_status(doc, "Paid")
    else:
        update_eem_status(doc, "Submitted")


def update_eem_on_update(doc, method=None):
    """
    Triggered on on_update.
    Used only to detect Paid state.
    """
    if doc.docstatus != 1:
        return

    if doc.is_paid or doc.status == "Paid":
        update_eem_status(doc, "Paid")


def update_eem_on_cancel(doc, method=None):
    """
    Triggered on on_cancel.
    """
    update_eem_status(doc, "Cancelled")
    

def update_eem_on_payment_submit(doc, method=None):
    """
    Triggered on Payment Entry submit.
    Update linked EEMs to Paid if applicable.
    """
    if doc.docstatus != 1:
        return

    # Check if Payment Entry is linked to Expense Claims
    if not doc.references:
        return

    linked_expense_claims = [
        ref.reference_name for ref in doc.references
        if ref.reference_doctype == "Expense Claim"
    ]

    if not linked_expense_claims:
        return

    for expense_claim_name in linked_expense_claims:
        expense_claim = frappe.get_doc("Expense Claim", expense_claim_name)
        update_eem_status(expense_claim, "Paid")
        
def update_eem_on_payment_cancel(doc, method=None):
    """
    Triggered on Payment Entry cancel.
    Revert linked EEMs from Paid to Submitted if applicable.
    """
    if doc.docstatus != 2:
        return

    # Check if Payment Entry is linked to Expense Claims
    if not doc.references:
        return

    linked_expense_claims = [
        ref.reference_name for ref in doc.references
        if ref.reference_doctype == "Expense Claim"
    ]

    if not linked_expense_claims:
        return

    for expense_claim_name in linked_expense_claims:
        expense_claim = frappe.get_doc("Expense Claim", expense_claim_name)
        update_eem_status(expense_claim, "Submitted")        