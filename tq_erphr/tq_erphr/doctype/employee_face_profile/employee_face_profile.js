frappe.ui.form.on("Employee Face Profile", {
	refresh(frm) {
		if (!frm.doc.employee || !frappe.user_roles.includes("System Manager")) {
			return;
		}

		frm.add_custom_button(__("Enroll Face"), () => {
			new frappe.ui.FileUploader({
				allow_multiple: false,
				restrictions: {
					allowed_file_types: ["image/jpeg", "image/png"],
				},
				on_success(file) {
					frappe.call({
						method: "tq_erphr.mobile_api.enroll_employee_face",
						args: {
							employee: frm.doc.employee,
							file_url: file.file_url,
						},
						freeze: true,
						freeze_message: __("Generating face embedding..."),
					}).then((r) => {
						if (r.message && r.message.enrolled) {
							frappe.show_alert({
								message: __("Face enrolled successfully"),
								indicator: "green",
							});
							frm.reload_doc();
						}
					});
				},
			});
		});
	},
});
