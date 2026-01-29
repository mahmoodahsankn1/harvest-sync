/* JS Module: UI - Handles Global UI Logic & Translations */

import { translations } from './translations.js';

const STORAGE_KEY = 'harvest_sync_lang';

export class UI {
    constructor() {
        this.currentLang = localStorage.getItem(STORAGE_KEY) || 'en';
        this.initLanguageToggle();
        this.applyLanguage();
    }

    initLanguageToggle() {
        // Handle simple toggle button (index/signup pages)
        const simpleToggle = document.getElementById('lang-toggle');
        if (simpleToggle) {
            this.updateToggleButtonText(simpleToggle);
            simpleToggle.addEventListener('click', () => this.toggleLanguage());
        }

        // Handle EN/ML button pairs (navigation bars)
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === this.currentLang);
            btn.addEventListener('click', () => {
                this.setLanguage(btn.dataset.lang);
            });
        });

        this.initMobileNav();
    }

    initMobileNav() {
        const menuBtn = document.querySelector('.mobile-menu-btn');
        const navLinks = document.querySelector('.nav-links');

        if (menuBtn && navLinks) {
            menuBtn.addEventListener('click', (e) => {
                e.preventDefault();
                menuBtn.classList.toggle('active');
                navLinks.classList.toggle('active');
            });

            // Close menu when clicking a link
            navLinks.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    menuBtn.classList.remove('active');
                    navLinks.classList.remove('active');
                });
            });
        }
    }

    toggleLanguage() {
        const newLang = this.currentLang === 'en' ? 'ml' : 'en';
        this.setLanguage(newLang);
    }

    setLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem(STORAGE_KEY, lang);
        this.applyLanguage();

        // Update toggle button text
        const simpleToggle = document.getElementById('lang-toggle');
        if (simpleToggle) {
            this.updateToggleButtonText(simpleToggle);
        }

        // Update EN/ML buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });

        console.log('Language switched to:', lang);
    }

    updateToggleButtonText(btn) {
        btn.textContent = this.currentLang === 'en' ? 'English / മലയാളം' : 'മലയാളം / English';
    }

    applyLanguage() {
        const t = translations[this.currentLang] || translations.en;
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key]) {
                // Handle input placeholders vs text content
                if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
                    el.placeholder = t[key];
                } else {
                    el.textContent = t[key];
                }
            }
        });

        // Set lang attribute on html element
        document.documentElement.lang = this.currentLang === 'ml' ? 'ml' : 'en';
    }

    // Expose translations for external use
    getTranslation(key) {
        const t = translations[this.currentLang] || translations.en;
        return t[key] || translations.en[key] || key;
    }
}

// Factory function for easy initialization
export function initUI() {
    return new UI();
}

export default UI;
