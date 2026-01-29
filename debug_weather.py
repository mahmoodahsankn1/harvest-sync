import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harvest_project.settings')
django.setup()

from core.models import User, Profile
from core.weather_service import WeatherService
from core.telegram_service import TelegramService
import traceback

print("=" * 60)
print("HARVEST SYNC - Weather Alert System Debug")
print("=" * 60)

# Test 1: Weather Service
print("\n[TEST 1] Testing Weather Service...")
try:
    weather_service = WeatherService()
    # Test with Thrissur, Kerala coordinates
    lat, lon = 10.8505, 76.2711
    print(f"Fetching weather for Lat: {lat}, Lon: {lon}")
    data = weather_service.get_weather(lat, lon)
    
    if 'error' in data:
        print(f"❌ API Error returned: {data['error']}")
    else:
        print(f"✅ Weather fetched successfully!")
        print(f"   Temperature: {data['weather']['temperature']}°C")
        print(f"   Humidity: {data['weather']['humidity']}%")
        print(f"   Daily Forecast keys: {list(data['weather']['daily_forecast'].keys())}")
        print(f"   Alerts: {len(data['alerts'])} found")
        for alert in data['alerts']:
            print(f"     - Alert: {alert['message']}")

except Exception:
    print(f"❌ Exception during weather fetch:")
    traceback.print_exc()

# Test 2: Check Farmer Profiles for valid coordinates
print("\n[TEST 2] Checking Farmer Profiles...")
try:
    farmers = Profile.objects.filter(role='farmer')
    print(f"✅ Found {farmers.count()} farmer(s)")
    for farmer in farmers:
        has_coords = farmer.latitude and farmer.longitude
        print(f"   - {farmer.user.username} ({farmer.user.first_name}): coords={farmer.latitude}, {farmer.longitude}")
        if not has_coords:
            print(f"     ⚠️  WARNING: No coordinates set for this farmer!")
except Exception:
    print(f"❌ Exception during profile check:")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug Complete!")
print("=" * 60)
