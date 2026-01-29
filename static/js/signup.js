/* JS Module: Signup - Handles Signup Page Logic & Role Switching */
import { UI } from './ui.js';

class SignupUI extends UI {
    constructor() {
        super();
        this.roleButtons = document.querySelectorAll('.role-btn');
        this.farmerFields = document.getElementById('farmer-fields');
        this.workerFields = document.getElementById('worker-fields');
        this.submitBtn = document.getElementById('submit-btn');
        this.body = document.body;

        // Map related
        this.map = null;
        this.marker = null;
        this.mapInitialized = false;

        this.initRoleSwitching();
    }

    initRoleSwitching() {
        this.roleButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const role = btn.getAttribute('data-role');
                this.switchRole(role);
            });
        });
    }

    switchRole(role) {
        // Update active button
        this.roleButtons.forEach(b => b.classList.remove('active'));
        document.querySelector(`.role-btn[data-role="${role}"]`).classList.add('active');

        // Update body data-role for global styling/logic
        this.body.setAttribute('data-role', role);

        // Toggle field visibility
        this.farmerFields.classList.toggle('hidden', role !== 'farmer');
        this.workerFields.classList.toggle('hidden', role !== 'worker');

        // Update submit button style based on role
        this.submitBtn.className = `btn btn-${role === 'consumer' ? 'user' : role}`;

        // Update hidden input for role
        const roleInput = document.getElementById('role-input');
        if (roleInput) {
            roleInput.value = role;
        }

        // Ensure land area input is required for farmers
        const landInput = document.getElementById('land_area');
        if (landInput) {
            landInput.required = (role === 'farmer');
        }

        // Initialize map if farmer role is selected
        if (role === 'farmer') {
            if (!this.mapInitialized) {
                this.initMap();
            } else {
                // Resize map if it was previously hidden
                setTimeout(() => {
                    if (this.map) google.maps.event.trigger(this.map, 'resize');
                }, 100);
            }
        }

        console.log(`Switched to role: ${role}`);
    }

    async initMap() {
        if (typeof google === 'undefined') {
            console.error("Google Maps API not loaded");
            return;
        }

        const mapElement = document.getElementById('location-container');
        if (!mapElement) return;

        // Clear placeholder content
        mapElement.innerHTML = '';
        mapElement.style.cursor = 'default';

        // Default location (Kerala)
        const defaultLoc = { lat: 10.8505, lng: 76.2711 };

        const { Map } = await google.maps.importLibrary("maps");
        const { Marker } = await google.maps.importLibrary("marker");

        this.map = new Map(mapElement, {
            center: defaultLoc,
            zoom: 8,
            mapId: "DEMO_MAP_ID", // Required for AdvancedMarkerElement if used, or just good practice
            streetViewControl: false,
            mapTypeControl: false
        });

        this.marker = new Marker({
            position: defaultLoc,
            map: this.map,
            draggable: true,
            title: "Farm Location"
        });

        this.mapInitialized = true;

        // Listeners for marker drag
        this.marker.addListener('dragend', () => {
            const pos = this.marker.getPosition();
            this.updateLocationInputs(pos.lat(), pos.lng());
        });

        // Click on map to move marker
        this.map.addListener('click', (e) => {
            const clickedPos = e.latLng;
            this.marker.setPosition(clickedPos);
            this.updateLocationInputs(clickedPos.lat(), clickedPos.lng());
        });

        // Try to get user's current location
        this.detectLocation();
    }

    updateLocationInputs(lat, lng) {
        document.getElementById('latitude').value = lat.toFixed(6);
        document.getElementById('longitude').value = lng.toFixed(6);
        console.log(`Updated location: ${lat}, ${lng}`);
    }

    detectLocation() {
        if (!navigator.geolocation) return;

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                const pos = { lat: latitude, lng: longitude };

                if (this.map && this.marker) {
                    this.map.setCenter(pos);
                    this.map.setZoom(15);
                    this.marker.setPosition(pos);
                    this.updateLocationInputs(latitude, longitude);
                }
            },
            (error) => {
                console.warn("Geolocation denied or error:", error);
            }
        );
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SignupUI();
    console.log("Harvest Sync Signup Initialized with Maps");
});
