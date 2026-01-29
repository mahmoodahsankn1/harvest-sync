# Weather Service Module - Open-Meteo API Integration
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache


class WeatherService:
    """Service for fetching and analyzing weather data from Open-Meteo API"""
    
    def __init__(self):
        self.api_url = settings.OPENMETEO_API_URL
        self.cache_timeout = settings.WEATHER_ALERT_CACHE_TIMEOUT
    
    def get_weather(self, latitude, longitude):
        """
        Fetch current weather data for given coordinates
        Returns: dict with weather data and alerts
        """
        cache_key = f"weather_{latitude}_{longitude}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Fetch weather data from Open-Meteo
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,uv_index_max',
                'timezone': 'auto',
                'forecast_days': 3
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract current weather
            current = data.get('current', {})
            daily = data.get('daily', {})
            
            weather_data = {
                'temperature': current.get('temperature_2m', 0),
                'humidity': current.get('relative_humidity_2m', 0),
                'precipitation': current.get('precipitation', 0),
                'wind_speed': current.get('wind_speed_10m', 0),
                'weather_code': current.get('weather_code', 0),
                'timestamp': current.get('time', datetime.now().isoformat()),
                'daily_forecast': {
                    'temp_max': daily.get('temperature_2m_max', []),
                    'temp_min': daily.get('temperature_2m_min', []),
                    'precipitation': daily.get('precipitation_sum', []),
                    'wind_max': daily.get('wind_speed_10m_max', []),
                    'uv_index': daily.get('uv_index_max', [])
                }
            }
            
            # Analyze for alerts
            alerts = self.analyze_weather(weather_data)
            
            result = {
                'weather': weather_data,
                'alerts': alerts
            }
            
            # Cache the result
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            print(f"Weather API Error: {str(e)}")
            return {
                'weather': self._get_dummy_weather(),
                'alerts': [],
                'error': str(e)
            }
    
    def analyze_weather(self, weather_data):
        """
        Analyze weather data for severe conditions
        Returns: list of alert dictionaries
        """
        alerts = []
        
        # Check current conditions
        temp = weather_data.get('temperature', 0)
        wind = weather_data.get('wind_speed', 0)
        precip = weather_data.get('precipitation', 0)
        
        # Check daily forecast
        daily = weather_data.get('daily_forecast', {})
        max_temps = daily.get('temp_max', [])
        daily_precip = daily.get('precipitation', [])
        max_winds = daily.get('wind_max', [])
        uv_indexes = daily.get('uv_index', [])
        
        # Heavy Rain Alert (>50mm in next 24h)
        if daily_precip and len(daily_precip) > 0 and daily_precip[0] > 50:
            alerts.append({
                'type': 'heavy_rain',
                'severity': 'high',
                'message': f'Heavy rainfall expected: {round(daily_precip[0])}mm. Protect crops and ensure drainage.',
                'message_ml': f'കനത്ത മഴ പ്രതീക്ഷിക്കുന്നു: {round(daily_precip[0])}mm. വിളകൾ സംരക്ഷിക്കുക, ഡ്രെയിനേജ് ഉറപ്പാക്കുക.'
            })
        
        # High Temperature Alert (>35°C)
        if max_temps and len(max_temps) > 0 and max_temps[0] > 35:
            alerts.append({
                'type': 'high_temperature',
                'severity': 'medium',
                'message': f'High temperature warning: {round(max_temps[0])}°C. Ensure adequate irrigation.',
                'message_ml': f'ഉയർന്ന താപനില മുന്നറിയിപ്പ്: {round(max_temps[0])}°C. മതിയായ ജലസേചനം ഉറപ്പാക്കുക.'
            })
        
        # Strong Wind Alert (>40 km/h)
        if max_winds and len(max_winds) > 0 and max_winds[0] > 40:
            alerts.append({
                'type': 'strong_wind',
                'severity': 'high',
                'message': f'Strong winds expected: {round(max_winds[0])} km/h. Secure loose structures.',
                'message_ml': f'ശക്തമായ കാറ്റ് പ്രതീക്ഷിക്കുന്നു: {round(max_winds[0])} km/h. അയഞ്ഞ ഘടനകൾ സുരക്ഷിതമാക്കുക.'
            })
        
        # Low Temperature Alert (<10°C - crop damage risk)
        if max_temps and len(max_temps) > 0 and max_temps[0] < 10:
            alerts.append({
                'type': 'low_temperature',
                'severity': 'medium',
                'message': f'Low temperature alert: {round(max_temps[0])}°C. Risk of crop damage.',
                'message_ml': f'കുറഞ്ഞ താപനില മുന്നറിയിപ്പ്: {round(max_temps[0])}°C. വിളകൾക്ക് കേടുപാടുകൾ ഉണ്ടാകാനുള്ള സാധ്യത.'
            })
        
        # High UV Index Alert (>8)
        if uv_indexes and len(uv_indexes) > 0 and uv_indexes[0] > 8:
            alerts.append({
                'type': 'high_uv',
                'severity': 'low',
                'message': f'Very high UV index: {round(uv_indexes[0])}. Protect workers and sensitive crops.',
                'message_ml': f'വളരെ ഉയർന്ന UV സൂചിക: {round(uv_indexes[0])}. തൊഴിലാളികളെയും സെൻസിറ്റീവ് വിളകളെയും സംരക്ഷിക്കുക.'
            })
        
        return alerts
    
    def create_test_alert(self):
        """Create a demo alert for testing/demo purposes"""
        return [{
            'type': 'demo',
            'severity': 'high',
            'message': '⚡ DEMO ALERT: Heavy rainfall expected in your area (75mm). This is a test alert for demonstration purposes.',
            'message_ml': '⚡ ഡെമോ അലേർട്ട്: നിങ്ങളുടെ പ്രദേശത്ത് കനത്ത മഴ പ്രതീക്ഷിക്കുന്നു (75mm). ഇത് പ്രദർശനത്തിനുള്ള ഒരു ടെസ്റ്റ് അലേർട്ട് ആണ്.'
        }]
    
    def _get_dummy_weather(self):
        """Return dummy weather data when API fails"""
        return {
            'temperature': 28,
            'humidity': 65,
            'precipitation': 0,
            'wind_speed': 12,
            'weather_code': 1,
            'timestamp': datetime.now().isoformat(),
            'daily_forecast': {
                'temp_max': [30, 31, 29],
                'temp_min': [22, 23, 21],
                'precipitation': [0, 5, 10],
                'wind_max': [15, 18, 14],
                'uv_index': [7, 8, 6]
            }
        }
