import frappe
from frappe.utils import getdate, formatdate
from datetime import timedelta
from frappe import _
import html
def execute(filters=None):
    if not filters:
        filters = {}
    
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    branch = filters.get("branch")
    employment_type = filters.get("employment_type")

    date_list = get_dates(from_date, to_date)
    columns = get_columns(date_list)
    data = get_data(from_date, to_date, date_list, branch, employment_type)

    # Chart removed as per request
    return columns, data

def get_dates(from_date, to_date):
    """Generate list of dates between from_date and to_date"""
    current = from_date
    dates = []
    while current <= to_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def get_columns(date_list):
    """Generate columns for the report"""
    columns = [
        {
            "fieldname": "employee", 
            "label": _("Employee"), 
            "fieldtype": "Link", 
            "options": "Employee", 
            "width": 120
        },
        {
            "fieldname": "employee_name", 
            "label": _("Employee Name"), 
            "fieldtype": "Data", 
            "width": 150
        },
       
    ]

    # Add date columns with weekday abbreviation
    for d in date_list:
        columns.append({
            "fieldname": d.strftime('%Y-%m-%d'),
            "label": d.strftime("%d\n%a"),  # e.g., 01\nMon (two lines)
            "fieldtype": "Data",
            "width": 80,
            "align": "center"
        })

    # Summary columns
    summary_columns = [
        {
            "fieldname": "present_days", 
            "label": _("Present"), 
            "fieldtype": "Int", 
            "width": 80,
            "cell_style": {"background-color": "#e6f7e6"}
        },
        {
            "fieldname": "absent_days", 
            "label": _("Absent"), 
            "fieldtype": "Int", 
            "width": 80,
            "cell_style": {"background-color": "#ffebee"}
        },
        {
            "fieldname": "leave_days", 
            "label": _("Leave"), 
            "fieldtype": "Int", 
            "width": 80,
            "cell_style": {"background-color": "#e3f2fd"}
        },
        {
            "fieldname": "half_days", 
            "label": _("Half Day"), 
            "fieldtype": "Int", 
            "width": 80,
            "cell_style": {"background-color": "#fff8e1"}
        },
        {
            "fieldname": "wfh_days", 
            "label": _("WFH"), 
            "fieldtype": "Int", 
            "width": 80,
            "cell_style": {"background-color": "#f3e5f5"}
        },
        {
            "fieldname": "holiday_count", 
            "label": _("Holidays"), 
            "fieldtype": "Int", 
            "width": 80,
            "cell_style": {"background-color": "#f5f5f5"}
        },
        {
            "fieldname": "unmarked_days", 
            "label": _("Unmarked"), 
            "fieldtype": "Int", 
            "width": 80,
            "cell_style": {"background-color": "#eceff1"}
        },
        {
            "fieldname": "total_days", 
            "label": _("Total Days"), 
            "fieldtype": "Int", 
            "width": 90,
            "cell_style": {"background-color": "#fff"}
        },
        {
            "fieldname": "working_days", 
            "label": _("Working Days"), 
            "fieldtype": "Int", 
            "width": 100,
            "cell_style": {"background-color": "#e0f7fa"}
        },
        {
            "fieldname": "attendance_percentage", 
            "label": _("Attendance %"), 
            "fieldtype": "Percent", 
            "width": 100,
            "precision": 1,
            "cell_style": {
                "background-color": "#e8f5e9",
                "font-weight": "bold"
            }
        },
    ]

    
    columns.extend(summary_columns)
    return columns

def get_data(from_date, to_date, date_list, branch, employment_type):
    """Fetch and process attendance data"""
    # Base employee filters
    emp_filters = {"status": "Active"}
    if branch:
        emp_filters["branch"] = branch
    if employment_type:
        emp_filters["employment_type"] = employment_type

    # Get employees
    employees = frappe.get_all(
        "Employee",
        filters=emp_filters,
        fields=["name", "employee_name", "department", "holiday_list", "designation"],
        order_by="department, employee_name"
    )

    # Get attendance records
    attendance_records = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", [from_date, to_date]],
            "docstatus": 1
        },
        fields=["employee", "attendance_date", "status", "leave_type"]
    )

    # Create attendance map
    attendance_map = {
        (att.employee, att.attendance_date): {
            "status": get_status_short_code(att.status),
            "leave_type": att.leave_type if att.status == "On Leave" else None
        }
        for att in attendance_records
    }

    # Get holidays
    holiday_map = {}
    holiday_lists = list(set(emp.holiday_list for emp in employees if emp.holiday_list))
    if holiday_lists:
        holidays = frappe.get_all(
            "Holiday",
            filters={
                "holiday_date": ["between", [from_date, to_date]],
                "parent": ["in", holiday_lists]
            },
            fields=["parent", "holiday_date", "description"]
        )
        for h in holidays:
            holiday_map.setdefault(h.parent, {})[h.holiday_date] = h.description

    # Process data
    data = []
    total_days = len(date_list)
    
    for emp in employees:
        row = {
            "employee": emp.name,
            "employee_name": emp.employee_name,
           
        }

        # Initialize counters
        counters = {
            "P": 0, "A": 0, "L": 0, "HD": 0, "WFH": 0, "H": 0, "UM": 0
        }
        
        emp_holidays = holiday_map.get(emp.holiday_list, {})

        for d in date_list:
            key = (emp.name, d)
            attendance = attendance_map.get(key)
            
            
            if not attendance:
                if d in emp_holidays:
                    status = "H"
                    holiday_desc = emp_holidays[d]
                    if holiday_desc:
                            # Strip HTML tags and escape any special characters
                            holiday_desc = frappe.utils.strip_html(holiday_desc)
                            holiday_desc = html.escape(holiday_desc.strip('"'))  # Remove extra quotes
                            tooltip = f"Holiday: {holiday_desc}"
                    else:
                            tooltip = "Holiday"
                else:
                    status = "UM"
                    tooltip = "Unmarked"
            else:
                status = attendance["status"]
                if status == "L":                    
                    leave_type = attendance['leave_type'] or ""
                    leave_type = frappe.utils.strip_html(leave_type)
                    leave_type = html.escape(leave_type)
                    tooltip = f"Leave: {leave_type}" if leave_type else "Leave"
                else:
                    tooltip = get_status_label(status)

            counters[status] += 1
            
            # Add styled cell
            row[d.strftime('%Y-%m-%d')] = get_styled_cell(status, tooltip)

        # Calculate working days (excluding holidays)
        working_days = total_days - counters["H"]
        
        # Calculate attendance percentage (Present + 0.5*Half Day + WFH) / Working Days
        if working_days > 0:
            attendance_percentage = (
                (counters["P"] + counters["WFH"] + (counters["HD"] * 0.5)) / 
                working_days * 100
            )
        else:
            attendance_percentage = 0

        # Add summary data
        row.update({
        "present_days": counters["P"] + (counters["HD"] * 0.5),
        "absent_days": counters["A"],
        "leave_days": counters["L"],
        "half_days": counters["HD"], 
        "wfh_days": counters["WFH"],                   
        "holiday_count": counters["H"],
        "unmarked_days": counters["UM"],
        "total_days": total_days,
        "working_days": working_days,
        "attendance_percentage": attendance_percentage,
        "_statistics": {
            "present": counters["P"],
            "absent": counters["A"],
            "leave": counters["L"],
            "half_day": counters["HD"],
            "wfh": counters["WFH"],
            "holiday": counters["H"],
            "unmarked": counters["UM"]
        }
    })


        data.append(row)

    return data

def get_status_short_code(status):
    """Convert status to short code"""
    mapping = {
        "Present": "P",
        "Absent": "A",
        "Half Day": "HD",
        "On Leave": "L",
        "Work From Home": "WFH"
    }
    return mapping.get(status, status[:1])

def get_status_label(status_code):
    """Get full status name from code"""
    mapping = {
        "P": "Present",
        "A": "Absent",
        "HD": "Half Day",
        "L": "Leave",
        "WFH": "Work From Home",
        "H": "Holiday",
        "UM": "Unmarked"
    }
    return mapping.get(status_code, status_code)

def get_styled_cell(status, tooltip=""):
    """Return HTML for styled cell with tooltip"""
    styles = {
        "P": {"bg": "#4CAF50", "text": "P", "color": "#fff"},      # Green
        "A": {"bg": "#F44336", "text": "A", "color": "#fff"},      # Red
        "L": {"bg": "#2196F3", "text": "L", "color": "#fff"},      # Blue
        "HD": {"bg": "#FFC107", "text": "½", "color": "#000"},     # Yellow
        "WFH": {"bg": "#9C27B0", "text": "W", "color": "#fff"},    # Purple
        "H": {"bg": "#9E9E9E", "text": "H", "color": "#fff"},      # Grey
        "UM": {"bg": "#EEEEEE", "text": "", "color": "#9E9E9E"}    # Light grey
    }
    
    style = styles.get(status, styles["UM"])
    
    return f"""
        <div style="
            background: {style['bg']};
            color: {style['color']};
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            font-weight: bold;
            cursor: default;
        " title="{tooltip}">
            {style['text']}
        </div>
    """