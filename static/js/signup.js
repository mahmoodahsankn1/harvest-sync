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

        // Ensure land area input is required for farmers
        const landInput = document.getElementById('land_area');
        if (landInput) {
            landInput.required = (role === 'farmer');
        }

        // Auto-detect location for farmer
        if (role === 'farmer') {
            this.detectLocation();
        }

        console.log(`Switched to role: ${role}`);
    }

    detectLocation() {
        const statusEl = document.getElementById('location-status');
        const container = document.getElementById('location-container');
        const latInput = document.getElementById('latitude');
        const longInput = document.getElementById('longitude');

        if (!statusEl || !latInput || !longInput) return;

        // Reset if already detected? We keep it to avoid re-fetching if user switches back and forth
        if (latInput.value) return;

        // Update Text to "Fetching..."
        const fetchMsg = this.currentLang === 'ml' ? "ലൊക്കേഷൻ തിരയുന്നു..." : "Fetching location...";
        statusEl.textContent = fetchMsg;
        container.style.cursor = 'wait';

        if (!navigator.geolocation) {
            statusEl.textContent = "Geolocation not supported";
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                latInput.value = latitude;
                longInput.value = longitude;

                const successMsg = this.currentLang === 'ml' ? "ലൊക്കേഷൻ കണ്ടെത്തി" : "Location detected";
                statusEl.textContent = `${successMsg}: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
                container.style.borderColor = 'var(--brand-farmer)';
                container.style.color = 'var(--brand-farmer)';
                container.style.cursor = 'default';
            },
            (error) => {
                console.error("Geolocation error:", error);
                const errorMsg = this.currentLang === 'ml' ? "ലൊക്കേഷൻ അനുമതി നിഷേധിച്ചു" : "Location access denied";
                statusEl.textContent = errorMsg;
                // Allow manual retry on click
                container.style.cursor = 'pointer';
                container.onclick = () => this.detectLocation();
            }
        );
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const signupUI = new SignupUI();
    console.log("Harvest Sync Signup Initialized");
});
