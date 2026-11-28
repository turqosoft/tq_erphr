function open_face_enrollment_dialog(employee, on_success) {
	const dialog = new frappe.ui.Dialog({
		title: __("Live Face Enrollment"),
		size: "large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "camera",
			},
		],
		primary_action_label: __("Enroll Captured Face"),
		primary_action() {
			if (!dialog.captured_image) {
				frappe.msgprint(__("Capture a face image before enrolling."));
				return;
			}

			dialog.get_primary_btn().prop("disabled", true);
			frappe.call({
				method: "tq_erphr.mobile_api.enroll_employee_face",
				args: {
					employee,
					image_base64: dialog.captured_image,
				},
				freeze: true,
				freeze_message: __("Generating face embedding..."),
			}).then((response) => {
				if (response.message && response.message.enrolled) {
					dialog.hide();
					frappe.show_alert({
						message: __("Face enrolled successfully"),
						indicator: "green",
					});
					on_success(response.message);
				}
			}).finally(() => {
				dialog.get_primary_btn().prop("disabled", !dialog.captured_image);
			});
		},
	});

	dialog.captured_image = null;
	dialog.stream = null;
	dialog.fields_dict.camera.$wrapper.html(`
		<div class="face-enrollment-camera text-center">
			<p>${__("Align the full face inside the oval. Only the area inside the guide will be kept.")}</p>
			<div class="face-enrollment-frame" style="position: relative; width: 100%; max-width: 480px; margin: auto; overflow: hidden; background: #111; border-radius: 8px;">
				<video autoplay playsinline style="display: block; width: 100%; height: 100%;"></video>
				<div class="face-enrollment-guide" style="position: absolute; left: 22%; top: 8%; width: 56%; height: 80%; box-sizing: border-box; border: 3px solid #fff; border-radius: 50%; box-shadow: 0 0 0 999px rgba(0, 0, 0, 0.38); pointer-events: none;"></div>
			</div>
			<canvas style="display: none;"></canvas>
			<img class="face-enrollment-preview" alt="${__("Cropped face preview")}" style="display: none; width: 100%; max-width: 320px; max-height: 45vh; object-fit: contain; border-radius: 8px;" />
			<div class="text-muted face-enrollment-status" style="margin-top: 8px;"></div>
			<button type="button" class="btn btn-primary face-enrollment-capture" style="margin-top: 8px;">${__("Capture")}</button>
			<button type="button" class="btn btn-default face-enrollment-retake" style="display: none; margin-top: 8px;">${__("Remove Image and Retake")}</button>
		</div>
	`);

	const wrapper = dialog.fields_dict.camera.$wrapper;
	const video = wrapper.find("video").get(0);
	const frame = wrapper.find(".face-enrollment-frame").get(0);
	const canvas = wrapper.find("canvas").get(0);
	const preview = wrapper.find(".face-enrollment-preview");
	const status = wrapper.find(".face-enrollment-status");
	const capture = wrapper.find(".face-enrollment-capture");
	const retake = wrapper.find(".face-enrollment-retake");
	const primary_button = dialog.get_primary_btn();
	primary_button.prop("disabled", true);

	function stop_camera() {
		if (dialog.stream) {
			dialog.stream.getTracks().forEach((track) => track.stop());
			dialog.stream = null;
		}
		video.srcObject = null;
	}

	function start_camera() {
		if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
			status.text(__("Camera capture requires a supported browser and a secure HTTPS connection."));
			return;
		}

		status.text(__("Requesting camera access..."));
		navigator.mediaDevices.getUserMedia({
			audio: false,
			video: {
				facingMode: "user",
				width: { ideal: 1280 },
				height: { ideal: 720 },
			},
		}).then((stream) => {
			dialog.stream = stream;
			video.srcObject = stream;
			video.onloadedmetadata = () => {
				const scale = Math.min(
					480 / video.videoWidth,
					(window.innerHeight * 0.55) / video.videoHeight,
				);
				frame.style.width = `${Math.round(video.videoWidth * scale)}px`;
				frame.style.height = `${Math.round(video.videoHeight * scale)}px`;
			};
			return video.play();
		}).then(() => {
			status.text(__("Camera ready. Make sure the face is well lit and clearly visible."));
		}).catch((error) => {
			stop_camera();
			status.text(__("Could not access the camera: {0}", [error.message || error.name]));
		});
	}

	wrapper.find(".face-enrollment-retake").on("click", () => {
		dialog.captured_image = null;
		preview.hide().attr("src", "");
		video.style.display = "";
		capture.show();
		retake.hide();
		primary_button.prop("disabled", true);
		start_camera();
	});

	capture.on("click", () => {
		if (!video.videoWidth || dialog.captured_image) {
			status.text(__("Wait for the camera preview before capturing."));
			return;
		}

		const crop_x = Math.round(video.videoWidth * 0.22);
		const crop_y = Math.round(video.videoHeight * 0.08);
		const crop_width = Math.round(video.videoWidth * 0.56);
		const crop_height = Math.round(video.videoHeight * 0.8);
		const output_scale = Math.min(
			1,
			1280 / crop_width,
			1280 / crop_height,
		);
		canvas.width = Math.round(crop_width * output_scale);
		canvas.height = Math.round(crop_height * output_scale);
		canvas.getContext("2d").drawImage(
			video,
			crop_x,
			crop_y,
			crop_width,
			crop_height,
			0,
			0,
			canvas.width,
			canvas.height,
		);
		dialog.captured_image = canvas.toDataURL("image/jpeg", 0.9);
		preview.attr("src", dialog.captured_image).show();
		video.style.display = "none";
		capture.hide();
		retake.show();
		status.text(__("Review the image, then select Enroll Captured Face."));
		primary_button.prop("disabled", false);
		stop_camera();
	});

	dialog.$wrapper.on("shown.bs.modal", start_camera);
	dialog.$wrapper.on("hidden.bs.modal", stop_camera);
	dialog.show();
}

frappe.ui.form.on("Employee", {
	refresh(frm) {
		if (frm.is_new() || !frappe.user_roles.includes("System Manager")) {
			return;
		}

		frm.add_custom_button(__("Live Face Enrollment"), () => {
			open_face_enrollment_dialog(frm.doc.name, (result) => {
				frappe.set_route("Form", "Employee Face Profile", result.employee);
			});
		}, __("Face Recognition"));
	},
});

frappe.ui.form.on("Employee Face Profile", {
	refresh(frm) {
		if (!frm.doc.employee || !frappe.user_roles.includes("System Manager")) {
			return;
		}

		frm.add_custom_button(__("Live Face Enrollment"), () => {
			open_face_enrollment_dialog(frm.doc.employee, () => frm.reload_doc());
		});
	},
});
