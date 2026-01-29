/* JS Module: Weather Service - Handles weather data and alerts */

import { translations } from './translations.js';

const API_BASE = '/api/weather';

class WeatherService {
    constructor() {
        this.currentWeather = null;
        this.forecast = [];
        this.alerts = [];
        this.lang = 'en';
    }

    setLanguage(lang) {
        this.lang = lang;
    }

    async fetchWeather() {
        try {
            const response = await fetch(`${API_BASE}/current/`);
            if (!response.ok) throw new Error('Failed to fetch weather');

            const data = await response.json();
            this.currentWeather = data.weather;
            this.forecast = data.weather?.daily_forecast || {};
            this.alerts = data.alerts || [];
            return data;
        } catch (error) {
            console.error('Weather fetch error:', error);
            throw error;
        }
    }

    async sendTestAlert() {
        try {
            const response = await fetch(`${API_BASE}/test-alert/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (!response.ok) throw new Error('Failed to send test alert');
            return await response.json();
        } catch (error) {
            console.error('Test alert error:', error);
            throw error;
        }
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    formatTemperature(temp) {
        return `${Math.round(temp)}°`;
    }

    formatWindSpeed(speed) {
        return `${Math.round(speed)} km/h`;
    }

    formatPrecipitation(precip) {
        return `${Math.round(precip)} mm`;
    }

    getWeatherIcon(code) {
        // WMO Weather interpretation codes
        if (code === 0) return '☀️';
        if (code <= 3) return '⛅';
        if (code <= 48) return '🌫️';
        if (code <= 57) return '🌧️';
        if (code <= 67) return '🌧️';
        if (code <= 77) return '🌨️';
        if (code <= 82) return '🌧️';
        if (code <= 86) return '🌨️';
        if (code <= 99) return '⛈️';
        return '🌤️';
    }

    getWeatherDescription(code, lang = 'en') {
        const descriptions = {
            en: {
                0: 'Clear Sky',
                1: 'Mainly Clear',
                2: 'Partly Cloudy',
                3: 'Overcast',
                45: 'Foggy',
                48: 'Depositing Rime Fog',
                51: 'Light Drizzle',
                53: 'Moderate Drizzle',
                55: 'Dense Drizzle',
                61: 'Slight Rain',
                63: 'Moderate Rain',
                65: 'Heavy Rain',
                71: 'Slight Snow',
                73: 'Moderate Snow',
                75: 'Heavy Snow',
                80: 'Rain Showers',
                81: 'Moderate Showers',
                82: 'Violent Showers',
                95: 'Thunderstorm',
                96: 'Thunderstorm with Hail'
            },
            ml: {
                0: 'തെളിഞ്ഞ ആകാശം',
                1: 'പ്രധാനമായും വ്യക്തം',
                2: 'ഭാഗികമായി മേഘാവൃതം',
                3: 'മേഘാവൃതം',
                45: 'മൂടൽമഞ്ഞ്',
                48: 'തണുത്ത മൂടൽമഞ്ഞ്',
                51: 'നേരിയ തുള്ളിമഴ',
                53: 'മിതമായ തുള്ളിമഴ',
                55: 'കടുത്ത തുള്ളിമഴ',
                61: 'ചെറിയ മഴ',
                63: 'മിതമായ മഴ',
                65: 'കനത്ത മഴ',
                71: 'ചെറിയ മഞ്ഞ്',
                73: 'മിതമായ മഞ്ഞ്',
                75: 'കനത്ത മഞ്ഞ്',
                80: 'മഴ ചാറ്റൽ',
                81: 'മിതമായ ചാറ്റൽ',
                82: 'കനത്ത ചാറ്റൽ',
                95: 'ഇടിമിന്നൽ',
                96: 'ആലിപ്പഴത്തോടെ ഇടിമിന്നൽ'
            }
        };

        const langDescs = descriptions[lang] || descriptions['en'];
        return langDescs[code] || langDescs[Math.floor(code / 10) * 10] || 'Unknown';
    }

    getDayName(index, lang = 'en') {
        const days = {
            en: ['Today', 'Tomorrow', 'Day After'],
            ml: ['ഇന്ന്', 'നാളെ', 'മറ്റന്നാൾ']
        };
        return (days[lang] || days['en'])[index] || `Day ${index + 1}`;
    }

    translate(key) {
        return translations[this.lang]?.[key] || translations['en'][key] || key;
    }
}

// Weather Widget UI Controller
export class WeatherWidget {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.service = new WeatherService();
        this.options = options;
        this.autoRefreshInterval = null;
        this.isLoading = false;

        // Set language from body data attribute or options
        const bodyLang = document.body.dataset.lang || 'en';
        this.service.setLanguage(options.language || bodyLang);
    }

    async init() {
        if (!this.container) {
            console.error('Weather widget container not found');
            return;
        }

        this.renderLoading();
        await this.refresh();

        // Auto-refresh every 30 minutes
        this.autoRefreshInterval = setInterval(() => this.refresh(), 30 * 60 * 1000);
    }

    renderLoading() {
        this.container.innerHTML = `
            <div class="weather-widget">
                <div class="weather-loading">
                    <div class="loading-spinner"></div>
                    <span class="loading-text">${this.service.translate('loading')}</span>
                </div>
            </div>
        `;
    }

    render(data) {
        const weather = data.weather;
        const forecast = weather.daily_forecast || {};
        const weatherIcon = this.service.getWeatherIcon(weather.weather_code || 0);
        const description = this.service.getWeatherDescription(weather.weather_code || 0, this.service.lang);

        this.container.innerHTML = `
            <div class="weather-container">
                <div class="weather-widget">
                    <div class="weather-header">
                        <h2 class="weather-title">
                            <span class="weather-icon-main">${weatherIcon}</span>
                            <span>${this.service.translate('weather_title')}</span>
                        </h2>
                        <div class="weather-actions">
                            <button class="weather-refresh-btn" id="refreshWeatherBtn">
                                <span id="refreshIcon">🔄</span>
                                <span>${this.service.translate('refresh')}</span>
                            </button>
                        </div>
                    </div>

                    <!-- Current Weather -->
                    <div class="current-weather">
                        <span class="current-weather-icon">${weatherIcon}</span>
                        <div class="current-weather-info">
                            <div class="current-temp">${this.service.formatTemperature(weather.temperature)}</div>
                            <div class="current-description">${description}</div>
                            <div class="current-location">📍 ${this.options.location || this.service.translate('your_location')}</div>
                        </div>
                    </div>

                    <!-- Weather Stats -->
                    <div class="weather-stats">
                        <div class="weather-stat">
                            <span class="weather-stat-icon">💧</span>
                            <div class="weather-stat-value">${Math.round(weather.humidity)}%</div>
                            <div class="weather-stat-label">${this.service.translate('humidity')}</div>
                        </div>
                        <div class="weather-stat">
                            <span class="weather-stat-icon">💨</span>
                            <div class="weather-stat-value">${Math.round(weather.wind_speed)}</div>
                            <div class="weather-stat-label">${this.service.translate('wind_speed')}</div>
                        </div>
                        <div class="weather-stat">
                            <span class="weather-stat-icon">🌧️</span>
                            <div class="weather-stat-value">${Math.round(weather.precipitation)}</div>
                            <div class="weather-stat-label">${this.service.translate('precipitation')}</div>
                        </div>
                        <div class="weather-stat">
                            <span class="weather-stat-icon">☀️</span>
                            <div class="weather-stat-value">${forecast.uv_index?.[0] || 'N/A'}</div>
                            <div class="weather-stat-label">UV Index</div>
                        </div>
                    </div>

                    <!-- 3-Day Forecast -->
                    <div class="forecast-section">
                        <h3 class="forecast-title">
                            <span>📅</span>
                            <span>${this.service.translate('forecast_title')}</span>
                        </h3>
                        <div class="forecast-grid">
                            ${this.renderForecastCards(forecast)}
                        </div>
                    </div>

                    <!-- Last Updated -->
                    <div class="last-updated">
                        <span>🕐</span>
                        <span>${this.service.translate('last_updated')}: ${new Date(weather.timestamp).toLocaleString()}</span>
                    </div>
                </div>

                <!-- Side Panel -->
                <div class="weather-side-panel">
                    <!-- Demo Panel -->
                    <div class="demo-panel">
                        <h3 class="demo-title">
                            <span>⚡</span>
                            <span>${this.service.translate('demo_mode')}</span>
                        </h3>
                        <div class="demo-actions">
                            <button class="demo-btn alert-btn" id="testAlertBtn">
                                <span>🚨</span>
                                <span>${this.service.translate('trigger_test_alert')}</span>
                            </button>
                        </div>
                    </div>

                    <!-- Telegram Panel -->
                    <div class="telegram-panel">
                        <div class="telegram-header">
                            <h3 class="telegram-title">
                                <span>📱</span>
                                <span>Telegram</span>
                            </h3>
                            <span class="telegram-status ${data.telegram_linked ? 'connected' : 'disconnected'}">
                                ${data.telegram_linked ? '✓ ' + this.service.translate('linked') : '✗ ' + this.service.translate('not_linked')}
                            </span>
                        </div>
                        <button class="telegram-link-btn" id="telegramLinkBtn">
                            <span>🔗</span>
                            <span>${this.service.translate('link_telegram')}</span>
                        </button>
                        <p class="telegram-info">${this.service.translate('telegram_instructions')}</p>
                    </div>

                    <!-- Quick Stats -->
                    ${this.renderQuickStats(forecast)}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderForecastCards(forecast) {
        const temps_max = forecast.temp_max || [30, 31, 29];
        const temps_min = forecast.temp_min || [22, 23, 21];
        const precip = forecast.precipitation || [0, 5, 10];
        const wind = forecast.wind_max || [15, 18, 14];

        let cards = '';
        for (let i = 0; i < 3; i++) {
            const icon = this.getForecastIcon(precip[i], temps_max[i]);
            cards += `
                <div class="forecast-card" data-day="${i}">
                    <div class="forecast-day">${this.service.getDayName(i, this.service.lang)}</div>
                    <span class="forecast-icon">${icon}</span>
                    <div class="forecast-temps">
                        <span class="forecast-temp-high">${this.service.formatTemperature(temps_max[i])}</span>
                        <span class="forecast-temp-low">${this.service.formatTemperature(temps_min[i])}</span>
                    </div>
                    <div class="forecast-details">
                        <span class="forecast-detail">
                            <span>🌧️</span>
                            <span>${Math.round(precip[i])}mm</span>
                        </span>
                        <span class="forecast-detail">
                            <span>💨</span>
                            <span>${Math.round(wind[i])}km/h</span>
                        </span>
                    </div>
                </div>
            `;
        }
        return cards;
    }

    getForecastIcon(precip, temp) {
        if (precip > 10) return '🌧️';
        if (precip > 0) return '🌦️';
        if (temp > 35) return '🌡️';
        if (temp > 28) return '☀️';
        return '⛅';
    }

    renderQuickStats(forecast) {
        const precip = forecast.precipitation || [0, 5, 10];
        const totalRain = precip.reduce((a, b) => a + b, 0);

        const temps = forecast.temp_max || [30, 31, 29];
        const avgTemp = temps.reduce((a, b) => a + b, 0) / temps.length;

        return `
            <div class="quick-stat-card">
                <div class="quick-stat-header">
                    <span>🌧️</span>
                    <span>${this.service.translate('total_rainfall')}</span>
                </div>
                <div class="quick-stat-value">${Math.round(totalRain)} mm</div>
                <div class="quick-stat-trend ${totalRain > 20 ? 'up' : 'down'}">
                    ${totalRain > 20 ? '↑ High' : '↓ Low'} ${this.service.translate('next_3_days')}
                </div>
            </div>
            <div class="quick-stat-card">
                <div class="quick-stat-header">
                    <span>🌡️</span>
                    <span>${this.service.translate('avg_temperature')}</span>
                </div>
                <div class="quick-stat-value">${Math.round(avgTemp)}°C</div>
                <div class="quick-stat-trend ${avgTemp > 30 ? 'up' : 'down'}">
                    ${avgTemp > 30 ? '↑ Warm' : '↓ Moderate'}
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const refreshBtn = document.getElementById('refreshWeatherBtn');
        const testAlertBtn = document.getElementById('testAlertBtn');
        const telegramLinkBtn = document.getElementById('telegramLinkBtn');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }

        if (testAlertBtn) {
            testAlertBtn.addEventListener('click', () => this.triggerTestAlert());
        }

        if (telegramLinkBtn) {
            telegramLinkBtn.addEventListener('click', () => this.openTelegramLink());
        }

        // Add hover effects to forecast cards
        document.querySelectorAll('.forecast-card').forEach(card => {
            card.addEventListener('click', () => this.showForecastDetails(card.dataset.day));
        });
    }

    async refresh() {
        if (this.isLoading) return;

        this.isLoading = true;
        const refreshIcon = document.getElementById('refreshIcon');
        if (refreshIcon) refreshIcon.classList.add('spin');

        try {
            const data = await this.service.fetchWeather();
            this.render(data);
            this.displayAlerts(data.alerts);
        } catch (error) {
            this.displayError(error.message);
        } finally {
            this.isLoading = false;
        }
    }

    displayAlerts(alerts) {
        if (!alerts || alerts.length === 0) {
            const existingBanner = document.querySelector('.weather-alert-banner');
            if (existingBanner) existingBanner.remove();
            return;
        }

        const alert = alerts[0];

        let banner = document.querySelector('.weather-alert-banner');
        if (!banner) {
            banner = document.createElement('div');
            banner.className = 'weather-alert-banner';
            this.container.insertBefore(banner, this.container.firstChild);
        }

        const messageKey = this.service.lang === 'ml' ? 'message_ml' : 'message';
        const message = alert[messageKey] || alert.message;

        banner.innerHTML = `
            <span class="weather-alert-icon">⚠️</span>
            <div class="weather-alert-content">
                <div class="weather-alert-title">${this.service.translate('severe_weather_alert')}</div>
                <div class="weather-alert-message">${message}</div>
            </div>
            <button class="alert-dismiss-btn" id="dismissAlert">✕</button>
        `;

        document.getElementById('dismissAlert')?.addEventListener('click', () => {
            banner.remove();
        });

        this.showNotification(alert);
    }

    displayError(message) {
        const widget = this.container.querySelector('.weather-widget');
        if (!widget) return;

        widget.innerHTML = `
            <div class="weather-error">
                <div class="weather-error-icon">😢</div>
                <h3>${this.service.translate('error')}</h3>
                <p>${message}</p>
                <button class="weather-refresh-btn" onclick="location.reload()">
                    <span>🔄</span>
                    <span>Retry</span>
                </button>
            </div>
        `;
    }

    async triggerTestAlert() {
        const btn = document.getElementById('testAlertBtn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = `<span class="spin">⏳</span><span>Sending...</span>`;
        }

        try {
            const result = await this.service.sendTestAlert();

            // Show success feedback
            this.showSuccessToast(this.service.translate('test_alert_sent'));

            // Display the alert banner
            this.displayAlerts(result.alerts);
        } catch (error) {
            this.showErrorToast(error.message);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = `<span>🚨</span><span>${this.service.translate('trigger_test_alert')}</span>`;
            }
        }
    }

    showSuccessToast(message) {
        this.showToast(message, 'success');
    }

    showErrorToast(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            background: ${type === 'success' ? 'linear-gradient(135deg, #10B981, #059669)' : 'linear-gradient(135deg, #EF4444, #DC2626)'};
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        `;
        toast.innerHTML = `${type === 'success' ? '✅' : '❌'} ${message}`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    showForecastDetails(dayIndex) {
        // Could open a modal with more details in future
        console.log(`Showing details for day ${dayIndex}`);
    }

    async openTelegramLink() {
        // Generate a unique linking code
        try {
            const response = await fetch('/api/telegram/generate-code/', {
                headers: {
                    'X-CSRFToken': this.service.getCSRFToken()
                }
            });

            if (!response.ok) throw new Error('Failed to generate code');

            const data = await response.json();
            const code = data.code;

            // Show modal with the code
            this.showLinkCodeModal(code);

            // Start polling for updates
            this.pollForTelegramLink();

        } catch (error) {
            console.error('Error generating code:', error);
            this.showErrorToast('Failed to generate link code');
            // Fallback: just open the bot
            window.open('https://t.me/harvestsyncbot', '_blank');
        }
    }

    showLinkCodeModal(code) {
        // Remove existing modal if any
        const existingModal = document.getElementById('telegramLinkModal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.id = 'telegramLinkModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            animation: fadeIn 0.3s ease;
        `;

        modal.innerHTML = `
            <div style="
                background: linear-gradient(145deg, rgba(30, 30, 40, 0.95), rgba(20, 20, 30, 0.98));
                border: 1px solid rgba(14, 165, 233, 0.3);
                border-radius: 24px;
                padding: 2.5rem;
                max-width: 400px;
                text-align: center;
                box-shadow: 0 25px 60px rgba(0,0,0,0.5);
                backdrop-filter: blur(20px);
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📱</div>
                <h2 style="color: white; margin-bottom: 1rem; font-size: 1.5rem;">Link Telegram</h2>
                <p style="color: rgba(255,255,255,0.7); margin-bottom: 1.5rem; line-height: 1.6;">
                    1. Open <a href="https://t.me/harvestsyncbot" target="_blank" style="color: #0EA5E9;">@harvestsyncbot</a> on Telegram<br>
                    2. Send this code to the bot:
                </p>
                <div style="
                    background: linear-gradient(135deg, #0EA5E9, #0284C7);
                    padding: 1.5rem 2rem;
                    border-radius: 16px;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
                ">
                    <span style="
                        font-size: 2.5rem;
                        font-weight: 800;
                        color: white;
                        letter-spacing: 8px;
                        font-family: monospace;
                    ">${code}</span>
                </div>
                <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-bottom: 1.5rem;">
                    The page will automatically update when linked!
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button id="openTelegramBtn" style="
                        background: linear-gradient(135deg, #0EA5E9, #0284C7);
                        color: white;
                        border: none;
                        padding: 0.8rem 1.5rem;
                        border-radius: 12px;
                        cursor: pointer;
                        font-weight: 600;
                        font-size: 1rem;
                        transition: transform 0.2s;
                    ">Open Telegram</button>
                    <button id="closeLinkModal" style="
                        background: rgba(255,255,255,0.1);
                        color: white;
                        border: 1px solid rgba(255,255,255,0.2);
                        padding: 0.8rem 1.5rem;
                        border-radius: 12px;
                        cursor: pointer;
                        font-weight: 600;
                        font-size: 1rem;
                        transition: transform 0.2s;
                    ">Close</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add event listeners
        document.getElementById('openTelegramBtn').addEventListener('click', () => {
            window.open('https://t.me/harvestsyncbot', '_blank');
        });

        document.getElementById('closeLinkModal').addEventListener('click', () => {
            modal.remove();
            this.stopPolling();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
                this.stopPolling();
            }
        });
    }

    pollForTelegramLink() {
        this.pollingInterval = setInterval(async () => {
            try {
                // First, trigger update check on server
                await fetch('/api/telegram/check-updates/');

                // Then refresh the weather widget to get new telegram status
                const response = await fetch('/api/weather/current/');
                if (response.ok) {
                    const data = await response.json();
                    if (data.telegram_linked) {
                        // Success! Close modal and refresh
                        this.stopPolling();
                        const modal = document.getElementById('telegramLinkModal');
                        if (modal) modal.remove();
                        this.showSuccessToast('✅ Telegram linked successfully!');
                        this.refresh();
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 3000); // Poll every 3 seconds
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    async showNotification(alert) {
        if (!('Notification' in window)) return;

        const messageKey = this.service.lang === 'ml' ? 'message_ml' : 'message';
        const message = alert[messageKey] || alert.message;

        if (Notification.permission === 'granted') {
            new Notification(this.service.translate('severe_weather_alert'), {
                body: message,
                icon: '/static/logo.jpeg',
                badge: '/static/logo.jpeg',
                vibrate: [200, 100, 200]
            });
        } else if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                new Notification(this.service.translate('severe_weather_alert'), {
                    body: message,
                    icon: '/static/logo.jpeg',
                    badge: '/static/logo.jpeg'
                });
            }
        }
    }

    destroy() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
    }
}

// Add CSS animation keyframes
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .spin {
        display: inline-block;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

export default WeatherWidget;
