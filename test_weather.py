# Quick Test Script for Weather Alert System
# Run this in Django shell: python manage.py shell < test_weather.py

from core.models import User, Profile
from core.weather_service import WeatherService
from core.telegram_service import TelegramService

print("=" * 60)
print("HARVEST SYNC - Weather Alert System Test")
print("=" * 60)

# Test 1: Weather Service
print("\n[TEST 1] Testing Weather Service...")
try:
    weather_service = WeatherService()
    # Test with Thrissur, Kerala coordinates
    data = weather_service.get_weather(10.8505, 76.2711)
    print(f"✅ Weather fetched successfully!")
    print(f"   Temperature: {data['weather']['temperature']}°C")
    print(f"   Humidity: {data['weather']['humidity']}%")
    print(f"   Alerts: {len(data['alerts'])} found")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Telegram Service
print("\n[TEST 2] Testing Telegram Service...")
try:
    telegram_service = TelegramService()
    result = telegram_service.verify_bot()
    if result.get('ok'):
        bot_info = result.get('result', {})
        print(f"✅ Telegram bot verified!")
        print(f"   Bot name: {bot_info.get('first_name')}")
        print(f"   Username: @{bot_info.get('username')}")
    else:
        print(f"❌ Bot verification failed: {result.get('error')}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Create Test Alert
print("\n[TEST 3] Creating Test Alert...")
try:
    weather_service = WeatherService()
    alerts = weather_service.create_test_alert()
    print(f"✅ Test alert created!")
    print(f"   Message (EN): {alerts[0]['message'][:50]}...")
    print(f"   Message (ML): {alerts[0]['message_ml'][:50]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Check Farmer Profiles
print("\n[TEST 4] Checking Farmer Profiles...")
try:
    farmers = Profile.objects.filter(role='farmer')
    print(f"✅ Found {farmers.count()} farmer(s)")
    for farmer in farmers[:3]:  # Show first 3
        has_coords = farmer.latitude and farmer.longitude
        has_telegram = bool(farmer.telegram_chat_id)
        print(f"   - {farmer.user.first_name}: coords={has_coords}, telegram={has_telegram}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Start server: python manage.py runserver")
print("2. Login as farmer")
print("3. Click 'Trigger Test Alert' button")
print("4. Check browser notification and Telegram")
print("=" * 60)
