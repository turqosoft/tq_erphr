## Tq Erphr

Tqerphr

#### License

mit

## Release Notes

### v1.0.8 (2026-06-10)

#### New Features
- 

#### Improvements
- Added Employee name in list view of Executive Expense manager list view

#### Bug Fixes
- 

### v1.0.9 (2026-06-18)

#### New Features
- Ability to add expense for multiple types of vehicles

#### Improvements
- Create expense claim by selecting employee and period in expense manager
- Update status of expense manager on cacellation of expense claim, payment entry

#### Bug Fixes
- 

### v1.0.10 (2026-06-27)

#### New Features

#### Improvements
- Unclub Checkin and Site visit

#### Bug Fixes
- 

### v1.0.11 (2026-06-27)

#### New Features
- Expense summary report

#### Improvements
- Executive expense manager enhancements

#### Bug Fixes
- 

### v1.0.12 (2026-06-29)

#### New Features
- Expense summary report

#### Improvements
- Change field type of location to long text from Data in employee site tracking

#### Bug Fixes
- 

### v1.0.13 (2026-06-30)

#### New Features
- 

#### Improvements
- Update the expense summary reporting.

#### Bug Fixes
- 

### v1.0.14 (2026-06-30)

#### New Features
- Google Map based route distance
- Settings to chose Openstreet map or Google Map

#### Improvements
- Separate section for DA in expense claims summary report

#### Bug Fixes
- 

### v1.0.15 (2026-09-04)

#### New Features
- 

#### Improvements
- Create expense claim option under "Action"

#### Bug Fixes
- Draft expenses getting added to executive expense manager

### v1.1.0 (2026-09-15)

#### New Features
- MobiBiz PWA Module added

#### Improvements
- 

#### Bug Fixes
- 

### v1.1.1 (2026-09-16)

#### New Features
- 

#### Improvements
- MobiBiz PWA Module added - build updates

#### Bug Fixes
- 

### v1.1.2 (2026-09-17)

#### New Features
- 

#### Improvements
- Travel history

#### Bug Fixes
- Not showing app download and install

### v1.1.3 (2026-09-18)

#### New Features
- Customer listing and search
- Record site visit from customer list
- Call, direction from customer list
- Team site visit detals for supervisors

#### Improvements
- Customer search in employee expense manger
- Show only first 10 site visits and logs
- Checking for location based customer - mandatory check removed.

#### Bug Fixes
- 

### v1.1.4 (2026-09-21)

#### New Features
- 

#### Improvements
- Additional fields in employee site tracking to capture customer details.
- MobiBiz Lite UI enhancements

#### Bug Fixes
- 

### v1.1.5 (2026-09-22)

#### New Features
- Customer billed and unpaid amount display
- Stock details

#### Improvements
- UI enhancements

#### Bug Fixes
- Fixed bug with stock and warehouse display

### v1.1.6 (2026-09-23)

#### New Features
- New Report - Customer visit report.

#### Improvements
- Removed zero stock godowns in stock

#### Bug Fixes
- 

### v1.1.7 (2026-09-24)

#### New Features
- Attach files in expenses

#### Improvements
- 

#### Bug Fixes
- 

### v1.1.9 (2026-09-26)

#### New Features
- Edit site visits

#### Improvements
- Removed display of geolocation
- UI improvements

#### Bug Fixes
- 

### v1.1.10 (2026-09-30)

#### New Features
- 

#### Improvements
- Increased field width of Remarks field in employee site tracking

#### Bug Fixes
- 

### v1.1.11 (2026-10-03)

#### New Features
- Executive Live Tracker

#### Improvements
- 

#### Bug Fixes
- 
### v1.1.12 (2026-10-06)

#### New Features
- Executive Live Tracker, enable,disable from server

#### Improvements
- 

#### Bug Fixes
- 

### v1.1.13 (2026-10-06)

#### New Features
- 

#### Improvements
- Slight modification in Executive expense manager site visit report.

#### Bug Fixes
- 

### v1.1.14 (2026-10-08)

#### New Features
- Designation wise and sales person wise expense rate settings.

#### Improvements
- Set time interval for tracking executives

#### Bug Fixes
- 

### v1.1.15 (2026-10-14)

#### New Features
- Installation and service visit features

#### Improvements
- 

#### Bug Fixes
- 

### v1.1.16 (2026-10-21)

#### New Features
- 

#### Improvements
- 

#### Bug Fixes
- Fixed the Naming series issue, now the maintenance visit will work with the correct naming series -> MAT-MVS-.YYYY.-

### v1.1.17 (2026-10-23)

#### New Features
- Added a serial number picker for spare parts. Service engineers can select serial numbers available in the selected warehouse. For items without serial numbers, no serial number field is displayed, and engineers can select spare parts that are in stock. This works for both Maintenance Visit and Installation Note.
- If no default warehouse is configured in stock settings, the service engineer can select a warehouse directly from the mobile app when choosing spare parts.

#### Improvements
- Fixed the Maintenance Visit series from the mobile app. visits now save as MAT-MVS-2026-00001.


#### Bug Fixes
- 

### v1.1.18 (2026-10-29)

#### New Features
- 

#### Improvements
- The default warehouse configured in CRM Support Settings will be shown in the mobile app. If no default warehouse is configured, or if there is insufficient stock in the default warehouse, the service engineer can select another warehouse.


#### Bug Fixes
- 

### v1.1.19 (2026-11-05)

#### New Features
- 

#### Improvements
- CRM app enhancements

#### Bug Fixes
- 

### v1.1.20 (2026-11-06)

#### New Features
- Added search bars for Installations and Visits on the Home page. The search filters records by customer, installation/visit, and serial number.

#### Improvements
- Added incremental pagination. Initially, only 10 records are loaded, and the limit increases by 10 each time the user loads more records.

#### Bug Fixes
- 

### v1.1.21 (2026-11-07)

#### New Features
- 

#### Improvements
- Enhanced UI

#### Bug Fixes
- Earlier Service engineer was not able see completed installation notes using task number, no its fixed.

### v1.1.22 (2026-11-09)

#### New Features
- 

#### Improvements
- The item descriptions for some items were saved with HTML tags, while others were stored as plain text and displayed correctly. Added a strip_html() function to remove the HTML tags, which fixed the issue.

#### Bug Fixes
-

## v1.1.23 (2026-11-10)

#### New Features
- 

#### Improvements
- Added an eye icon to view task details.
- Restricted the Re-assign button to incomplete tasks.
- Enhanced the supervisor dashboard UI with task dropdowns, task type and status badges, and a details popup.

#### Bug Fixes
-

## v1.1.24 (2026-11-12)

#### New Features
- Draft Creation: Engineer fills in the form and taps Save. A draft Maintenance Visit or Installation Note is created. Combined maintenance visits are saved as a single draft.
- OTP Generation: After completing the signature, location, serial numbers and checklist, the engineer taps Generate OTP. The existing function inside tq_crm_support generates a 4-digit OTP and saves it against the draft.
- OTP Verification: A popup allows the engineer to enter the OTP, with a 5-minute countdown. Tapping Confirm & Submit validates the OTP and submits the same draft.
- Draft Persistence: If the engineer navigates back, the draft remains saved. Reopening the form restores the previously entered data.
- OTP Resumption: If an OTP is still valid, the app displays Enter OTP. Once expired, the engineer can generate a new OTP against the same draft without creating another visit.
- OTP Disabled: When the OTP setting is turned off, the engineer can submit the document directly without OTP verification, maintaining the existing workflow.

#### Improvements
- 

#### Bug Fixes
- The task list was not updating when switching between Maintenance and Installation.
Fix: Updated load( ) to send the selected task type and setKind( ) to reload the task list whenever the type changes.
- Completed visits and installations were still appearing in today's task list.
Fixed it by Updating the task filtering logic to hide fully completed tasks from today's pending task list.

### v1.1.25 (2026-11-16)

#### New Features
- 

#### Improvements
- Added View More Details: Moved task details, items with serial numbers, spare parts, and invoice under this section.
- Simplified cards in each page, now each page only display's only customer name, ID, status, and date.
- In My Installations page, Added All, Partial, and Completed tabs with server-side filtering.
- Added a back arrow in service page, my installation, my visits and team dashboard

#### Bug Fixes
-

### v1.1.26 (2026-11-17)

#### New Features
- Supervisor view of subordinate performance
#### Improvements
- Integrated latest changes of employee expense manager with crm support
#### Bug Fixes
- Visits created from ERPNext for service engineers were displaying only the maintenance visit id in the mobile app because customer_name field was missing in the Maintenance Visit Doctype. Fixed this by adding the "customer" field , now visits created from erpnext for the service engineer will show the correct customer name in mobile app

### v1.1.27 (2026-11-18)

#### New Features
- 
#### Improvements
- Pagenation in team sales view listing
- The pwa_crm API now reads the "customer_name" field from Maintenance Schedule Task and Installation Task to show the customer name on task cards, in the details view and in search. If the field is empty, it falls back to the Customer lookup.
- Removed the pwa_crm API's own OTP code check.
- Added _check_otp_window. It keeps the 5-minute expiry check, which the server-side validators don’t do.
- Updated the three submit functions (maintenance visit, combined maintenance visit and installation note) to call the new validate functions in tq_crm_support.
#### Bug Fixes
- 

### v1.1.28 (2026-11-25)

#### New Features
- 
#### Improvements
- Net total, tax and grand total in pwa performance dashboard
- Improved pagenation
#### Bug Fixes
- 

### v1.1.29 (2026-11-26)

#### New Features
- 
#### Improvements
- Corrected Net total in performance dashboard

#### Bug Fixes
- 