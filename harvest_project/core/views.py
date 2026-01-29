from django.shortcuts import render

def index(request):
    """Landing page to choose role"""
    return render(request, 'index.html')

def farmer_dashboard(request):
    """Farmer module dashboard"""
    return render(request, 'farmer_dashboard.html')

def marketplace(request):
    """User (Consumer) marketplace"""
    # Dummy data for initial display
    products = [
        {'name': 'Tomatoes', 'price': 40, 'offer_price': 25, 'is_surplus': True, 'expiry': '2 days'},
        {'name': 'Potatoes', 'price': 30, 'offer_price': 30, 'is_surplus': False, 'expiry': '10 days'},
        {'name': 'Spinach', 'price': 20, 'offer_price': 15, 'is_surplus': True, 'expiry': '1 day'},
    ]
    return render(request, 'marketplace.html', {'products': products})
