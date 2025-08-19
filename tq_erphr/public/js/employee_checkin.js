frappe.ui.form.on('Employee Checkin', {
    refresh(frm) {
        const wrapper = frm.fields_dict.google_map_html?.$wrapper;
        if (!wrapper) return;

        // Clear wrapper (so button + map don't duplicate on refresh)
        wrapper.empty();

        // 👉 Create Fetch Location button inside wrapper
        const btn = $('<button class="btn btn-primary btn-xs">Fetch Location</button>')
            .css({ marginBottom: "10px" })
            .on('click', function () {
                frm.trigger("fetch_geolocation");
            });

        wrapper.append(btn);

        // Container for map
        const mapDiv = $('<div id="google_map_div"></div>')
            .css({ height: "300px", width: "100%" });
        wrapper.append(mapDiv);

        // Load Google Maps
        loadGoogleMapsApi('AIzaSyDtYS2HplGfg7HWxx2JxJ0vnpVAXbh0FyU')
            .then(() => {
                renderGoogleMap(frm);
            })
            .catch((err) => {
                console.error("Google Maps API load failed:", err);
            });
    },

    fetch_geolocation(frm) {
        if (!navigator.geolocation) {
            frappe.msgprint('Geolocation is not supported by this browser.');
            return;
        }
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                frm.set_value('latitude', lat);
                frm.set_value('longitude', lng);

                frappe.show_alert({
                    message: __("Location fetched successfully"),
                    indicator: "green"
                });

                updateGoogleMapMarker(lat, lng);
            },
            function (err) {
                frappe.msgprint('Error fetching geolocation: ' + err.message);
            }
        );
    }
});

let gmap;
let gmarker;

function loadGoogleMapsApi(apiKey) {
    return new Promise((resolve, reject) => {
        if (window.google && window.google.maps) {
            resolve();
            return;
        }

        window.initMap = function () {
            resolve();
        };

        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`;
        script.async = true;
        script.defer = true;
        script.onerror = () => reject(new Error("Failed to load Google Maps API script"));
        document.head.appendChild(script);
    });
}

function renderGoogleMap(frm) {
    const mapDiv = document.getElementById("google_map_div");
    if (!mapDiv) return;

    const lat = parseFloat(frm.doc.latitude) || 20.5937;
    const lng = parseFloat(frm.doc.longitude) || 78.9629;

    gmap = new google.maps.Map(mapDiv, {
        center: { lat, lng },
        zoom: 15
    });

    gmarker = new google.maps.Marker({
        position: { lat, lng },
        map: gmap,
        draggable: true
    });

    gmarker.addListener('dragend', function (event) {
        const new_lat = event.latLng.lat();
        const new_lng = event.latLng.lng();
        frm.set_value('latitude', new_lat);
        frm.set_value('longitude', new_lng);
    });

    // ✅ Sync marker when lat/lng fields change manually
    if (frm.fields_dict.latitude && frm.fields_dict.latitude.$input) {
        frm.fields_dict.latitude.$input.on('change', () => {
            updateGoogleMapMarker(parseFloat(frm.doc.latitude), parseFloat(frm.doc.longitude));
        });
    }
    if (frm.fields_dict.longitude && frm.fields_dict.longitude.$input) {
        frm.fields_dict.longitude.$input.on('change', () => {
            updateGoogleMapMarker(parseFloat(frm.doc.latitude), parseFloat(frm.doc.longitude));
        });
    }
}

function updateGoogleMapMarker(lat, lng) {
    if (gmarker && gmap) {
        const pos = { lat: lat || 0, lng: lng || 0 };
        gmarker.setPosition(pos);
        gmap.setCenter(pos);
    }
}
