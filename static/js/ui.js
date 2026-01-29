/* JS Module: UI - Handles Global UI Logic & Translations */

const translations = {
    en: {
        title: "Harvest Sync",
        subtitle: "Bridging Farmers, Markets, and Logistics for a Sustainable Future.",
        farmer_title: "For Farmers",
        farmer_desc: "AI Disease Detection, Weather Alerts, and Direct Sales.",
        farmer_btn: "Farmer Access",
        consumer_title: "For Consumers",
        consumer_desc: "Buy Fresh Produce & Surplus Food at Discounted Rates.",
        consumer_btn: "Start Shopping",
        worker_title: "For Workers",
        worker_desc: "Optimized Logistics and Delivery Routes.",
        worker_btn: "Join Logistics",
        govt_title: "For Government",
        govt_desc: "Scheme Dissemination and Agricultural Data Analysis.",
        govt_btn: "Admin Panel",
        login: "Login",
        signup: "Sign Up",
        signup_title: "Join Harvest Sync",
        role_select: "Select Your Role",
        farmer: "Farmer",
        consumer: "Consumer",
        worker: "Worker",
        name: "Full Name",
        phone: "Phone Number",
        email: "Email Address",
        place: "Place",
        location: "Location (Google Map)",
        land_area: "Land Area (in acres)",
        skills: "Worker Skills",
        plowing: "Plowing",
        harvesting: "Harvesting",
        irrigation: "Irrigation",
        transport: "Transport",
        password: "Password",
        confirm_password: "Confirm Password",
        fetching_loc: "Fetching location...",
        loc_detected: "Location detected",
        loc_denied: "Location access denied",
        use_current_loc: "Use Current Location",
        signup_btn: "Create Account"
    },
    ml: {
        title: "ഹാർവെസ്റ്റ് സിങ്ക്",
        subtitle: "കർഷകരെയും വിപണികളെയും ലോജിസ്റ്റിക്സിനെയും ബന്ധിപ്പിക്കുന്നു.",
        farmer_title: "കർഷകർക്ക്",
        farmer_desc: "രോഗനിർണയം, കാലാവസ്ഥാ മുന്നറിയിപ്പുകൾ, നേരിട്ടുള്ള വിൽപന.",
        farmer_btn: "കർഷക സേവനങ്ങൾ",
        consumer_title: "ഉപഭോക്താക്കൾക്ക്",
        consumer_desc: "പുതിയ വിളകളും അധികമുള്ള ഭക്ഷണവും കുറഞ്ഞ നിരക്കിൽ വാങ്ങാം.",
        consumer_btn: "ഷോപ്പിംഗ് തുടങ്ങാം",
        worker_title: "തൊഴിലാളികൾക്ക്",
        worker_desc: "മികച്ച ഡെലിവറി റൂട്ടുകൾ.",
        worker_btn: "ജോലികൾ കാണാം",
        govt_title: "സർക്കാരിന്",
        govt_desc: "കാർഷിക പദ്ധതികളും വിവരങ്ങളും.",
        govt_btn: "അഡ്മിൻ പാനൽ",
        login: "ലോഗിൻ",
        signup: "സൈൻ അപ്പ്",
        signup_title: "ഹാർവെസ്റ്റ് സിങ്കിൽ ചേരുക",
        role_select: "നിങ്ങളുടെ റോൾ തിരഞ്ഞെടുക്കുക",
        farmer: "കർഷകൻ",
        consumer: "ഉപഭോക്താവ്",
        worker: "തൊഴിലാളി",
        name: "മുഴുവൻ പേര്",
        phone: "ഫോൺ നമ്പർ",
        email: "ഇമെയിൽ വിലാസം",
        place: "സ്ഥലം",
        location: "ലൊക്കേഷൻ (ഗൂഗിൾ മാപ്പ്)",
        land_area: "കൃഷിഭൂമി (ഏക്കറിൽ)",
        skills: "തൊഴിൽ നൈപുണ്യങ്ങൾ",
        plowing: "നിലം ഒരുക്കൽ",
        harvesting: "വിളവെടുപ്പ്",
        irrigation: "നനയ്ക്കൽ",
        transport: "ഗതാഗതം",
        password: "പാസ്‌വേഡ്",
        confirm_password: "പാസ്‌വേഡ് ഉറപ്പാക്കുക",
        fetching_loc: "ലൊക്കേഷൻ തിരയുന്നു...",
        loc_detected: "ലൊക്കേഷൻ കണ്ടെത്തി",
        loc_denied: "ലൊക്കേഷൻ അനുമതി നിഷേധിച്ചു",
        use_current_loc: "നിലവിലെ ലൊക്കേഷൻ ഉപയോഗിക്കുക",
        signup_btn: "അക്കൗണ്ട് തുടങ്ങാം"
    }
};

export class UI {
    constructor() {
        this.currentLang = 'en';
        this.langToggleBtn = document.getElementById('lang-toggle');

        if (this.langToggleBtn) {
            this.langToggleBtn.addEventListener('click', () => this.toggleLanguage());
        }
    }

    toggleLanguage() {
        this.currentLang = this.currentLang === 'en' ? 'ml' : 'en';
        this.langToggleBtn.textContent = this.currentLang === 'en' ? 'English / മലയാളം' : 'മലയാളം / English';
        this.updateText();
    }

    updateText() {
        const t = translations[this.currentLang];
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key]) {
                el.textContent = t[key];
            }
        });
    }
}
