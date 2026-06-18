# Copyright (c) 2025, Turqosoft Solutions Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import math
from frappe.model.document import Document
from tq_erphr.geo import street_distance, reverse_geocode

class ExecutiveExpenseManager(Document):
    def validate(self):
        self.calculate_site_distances()        
        self.calculate_odometer_distance()
        self.calculate_totals()
        self.build_route_polyline()
        self.fill_location_names()

    def before_insert(self):
        self.validate_employee_has_checkin()

    def before_submit(self):
        self.validate_employee_has_checkout()
    
    def before_save(self):
        
        self.add_travel_expensetype_and_rate()
        
        if self.end_lat and self.end_long:
            self.fetch_site_location()
            self.calculate_site_distances()        
            self.calculate_odometer_distance()
            self.calculate_totals()
            self.build_route_polyline()
            self.fill_location_names()

    def validate_employee_has_checkin(self):
        if not (self.employee and self.date):
            return

        if not self.has_employee_checkin(("IN", "CHECKIN")):
            frappe.throw(
                f"Executive Expense Manager can be created only if employee {self.employee} "
                f"has checked in on {self.date}."
            )

    def validate_employee_has_checkout(self):
        if not (self.employee and self.date):
            return

        if not self.has_employee_checkin(("OUT", "CHECKOUT")):
            frappe.throw(
                f"Executive Expense Manager can be submitted only if employee {self.employee} "
                f"has checked out on {self.date}."
            )

    def has_employee_checkin(self, log_types):
        start_datetime = f"{self.date} 00:00:00"
        end_datetime = f"{self.date} 23:59:59"

        return frappe.db.exists(
            "Employee Checkin",
            {
                "employee": self.employee,
                "log_type": ["in", log_types],
                "time": ["between", [start_datetime, end_datetime]]
            }
        )
    
    def add_travel_expensetype_and_rate(self):
    
            hr_settings = frappe.get_single("TQ ERPHRHR Settings")
            self.travel_expense_type = hr_settings.travel_expense_type
            if self.vehicle_type == "Two Wheeler":
                self.rate_per_km = hr_settings.two_wheeler_rate_per_km
            elif self.vehicle_type == "Four Wheeler":
                self.rate_per_km = hr_settings.four_wheeler_rate_per_km
            elif self.vehicle_type == "Other":
                self.rate_per_km = hr_settings.other_rate_per_km
    
    
    
    
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
                    "sanctioned_amount" : self.total_travel_expense,
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
                        "sanctioned_amount": row.amount,
                        "description": row.description 
                    })

            expense_claim.insert(ignore_permissions=True)
            

            frappe.msgprint(
                f"Expense Claim <b>{expense_claim.name}</b> created successfully."
            )
            
    def calculate_odometer_distance(self):
        start_odometer = self.start_odometerkm or 0
        end_odometer = self.end_odometerkm or 0

        if not (start_odometer and end_odometer):
            self.odometer_distance = 0
            return

        self.odometer_distance = round(end_odometer - start_odometer, 3)

  
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

            for row in self.employee_site_tracking:

                # If site location is missing, there is no site distance to calculate.
                if not (row.site_lat and row.site_long):
                    row.distance_travelled = 0
                    
                    continue

                if not (prev_lat and prev_long):
                    row.distance_travelled = 0
                    prev_lat = row.site_lat
                    prev_long = row.site_long
                    continue

                # Calculate distance between previous location and current site.
                distance = street_distance(
                    prev_lat,
                    prev_long,
                    row.site_lat,
                    row.site_long
                )

                # Save distance
                row.distance_travelled = round(distance, 3)
                if not row.actual_distance:
                    row.actual_distance = round(distance, 3)

                # Update previous coordinates to current site.
                prev_lat = row.site_lat
                prev_long = row.site_long

            # ---------- Last leg: last site -> end point ----------
            if self.end_lat and self.end_long and self.employee_site_tracking:
                last = self.employee_site_tracking[-1]
                if last.site_lat and last.site_long:
                    last_leg = street_distance(
                        last.site_lat,
                        last.site_long,
                        self.end_lat,
                        self.end_long
                    )
                


   

        
    def fill_location_names(self):
        for row in self.employee_site_tracking:
            if row.site_lat and row.site_long:
                if not row.location_name:
                    row.location_name = reverse_geocode(row.site_lat, row.site_long)
                
                
                    
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

        def add_direction_marker(start_coord, end_coord):
            start_lon, start_lat = start_coord
            end_lon, end_lat = end_coord

            dx = end_lon - start_lon
            dy = end_lat - start_lat
            length = math.hypot(dx, dy)
            if not length:
                return

            unit_x = dx / length
            unit_y = dy / length
            perp_x = -unit_y
            perp_y = unit_x

            arrow_lon = start_lon + dx * 0.6
            arrow_lat = start_lat + dy * 0.6
            arrow_size = min(max(length * 0.18, 0.00025), length * 0.45, 0.001)
            arrow_width = arrow_size * 0.6

            base_lon = arrow_lon - unit_x * arrow_size
            base_lat = arrow_lat - unit_y * arrow_size

            left = [
                base_lon + perp_x * arrow_width,
                base_lat + perp_y * arrow_width
            ]
            right = [
                base_lon - perp_x * arrow_width,
                base_lat - perp_y * arrow_width
            ]
            tip = [arrow_lon, arrow_lat]

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [tip, left, right, tip]
                    ]
                },
                "properties": {
                    "name": "Direction",
                    "stroke": "#0f766e",
                    "stroke-width": 2,
                    "fill": "#0f766e",
                    "fill-opacity": 1
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

        # ---------------- SITE MARKERS ONLY ----------------

        for idx, row in enumerate(self.employee_site_tracking, start=1):

            if not (row.site_lat and row.site_long):
                continue

            coords.append([row.site_long, row.site_lat])

            # Marker
            site_label = row.site or row.location_name or ""
            add_marker(
                row.site_lat,
                row.site_long,
                f"Site {idx}: {site_label}",
                "#0066ff"    # blue
            )

            # Store segment distance (already calculated in row)
            if row.distance_travelled:
                segment_distances.append(row.distance_travelled)
            else:
                segment_distances.append(0)

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
                    "stroke": "#2563eb",
                    "stroke-width": 4,

                    # JS will use this to draw distance labels
                    "segment_distances": segment_distances
                }
            }
            features.append(route_feature)

            for start_coord, end_coord in zip(coords, coords[1:]):
                add_direction_marker(start_coord, end_coord)

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
                    "sanctioned_amount": eem.total_travel_expense,
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
                        "sanctioned_amount": row.amount,
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


@frappe.whitelist()
def create_employee_expense_claim(employee, start_date, end_date):
    if not employee:
        frappe.throw("Employee is required.")
    if not start_date or not end_date:
        frappe.throw("Start Date and End Date are required.")
    if frappe.utils.getdate(start_date) > frappe.utils.getdate(end_date):
        frappe.throw("Start Date cannot be after End Date.")

    eems = frappe.get_all(
        "Executive Expense Manager",
        filters={
            "employee": employee,
            "date": ["between", [start_date, end_date]],
            "expense_claim_status": "Not Created",
        },
        fields=["name"],
        order_by="date asc, name asc",
    )

    if not eems:
        frappe.throw("No Not Created Executive Expense Manager records found for the selected employee and date range.")

    return bulk_create_expense_claim([row.name for row in eems])


@frappe.whitelist()
def get_eem_employees(doctype, txt, searchfield, start, page_length, filters):
    """Return list of employees who have Executive Expense Manager records with employee name"""
    employees = frappe.get_all(
        "Executive Expense Manager",
        fields=["DISTINCT employee"],
        filters={"employee": ["like", f"%{txt}%"]} if txt else {},
        limit_page_length=page_length,
        limit_start=start,
    )
    
    result = []
    for emp in employees:
        emp_doc = frappe.get_doc("Employee", emp.employee)
        result.append([emp.employee, f"{emp.employee} - {emp_doc.employee_name}"])
    
    return result


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


def get_eem_status_from_expense_claim(doc):
    """Map Expense Claim state to EEM status."""
    if doc.docstatus == 2:
        return "Cancelled"

    if doc.docstatus == 0:
        return "Processing"

    status = doc.status
    if hasattr(doc, "set_status"):
        doc.set_status()
        status = doc.status

    if status == "Paid":
        return "Paid"

    if doc.approval_status == "Rejected" or status == "Rejected":
        return "Rejected"

    if status == "Unpaid":
        return "Unpaid"

    if doc.approval_status == "Approved" or status == "Approved":
        return "Approved"

    return "Submitted"


def update_eem_status(doc, status=None):
    """Update linked EEM status safely without triggering unnecessary hooks."""
    eem_names = get_eem_names_from_expense_claim(doc)

    if not eem_names:
        return

    status = status or get_eem_status_from_expense_claim(doc)

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
    Draft Expense Claims keep linked EEMs in Processing.
    """
    if doc.docstatus != 0:
        return

    update_eem_status(doc)


def update_eem_on_submit(doc, method=None):
    """
    Triggered on on_submit.
    """
    update_eem_status(doc)


def update_eem_on_update(doc, method=None):
    """
    Triggered on on_update.
    Keep EEM status aligned with Expense Claim status.
    """
    update_eem_status(doc)


def update_eem_on_cancel(doc, method=None):
    """
    Triggered on on_cancel.
    """
    update_eem_status(doc, "Not Created")


def update_eem_on_draft_delete(doc, method=None):
    """
    Triggered when a draft Expense Claim is deleted.
    Revert linked EEMs to their initial claim state.
    """
    if doc.docstatus != 0:
        return

    update_eem_status(doc, "Not Created")
    

def update_eem_on_payment_submit(doc, method=None):
    """
    Triggered on Payment Entry submit.
    Update linked EEMs from linked Expense Claim status.
    """
    if doc.docstatus != 1:
        return

    if not doc.references:
        return

    linked_expense_claims = [
        ref.reference_name for ref in doc.references
        if ref.reference_doctype == "Expense Claim"
    ]

    for expense_claim_name in linked_expense_claims:
        expense_claim = frappe.get_doc("Expense Claim", expense_claim_name)
        update_eem_status(expense_claim)
        

def update_eem_on_payment_cancel(doc, method=None):
    """
    Triggered on Payment Entry cancel.
    Revert linked EEMs from the linked Expense Claim status.
    """
    if doc.docstatus != 2:
        return

    if not doc.references:
        return

    linked_expense_claims = [
        ref.reference_name for ref in doc.references
        if ref.reference_doctype == "Expense Claim"
    ]

    for expense_claim_name in linked_expense_claims:
        expense_claim = frappe.get_doc("Expense Claim", expense_claim_name)
        update_eem_status(expense_claim)
