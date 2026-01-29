from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Profile, Product, Bid, Order, Cart, CartItem

from .utils import generate_otp, send_otp_email, send_invoice_emails
from .weather_service import WeatherService
from .telegram_service import TelegramService
import json
from django.utils import timezone
import math

def index(request):
    """Landing page to choose role"""
    return render(request, 'index.html')

def signup(request):
    """Unified signup page for all roles with OTP flow"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if user already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "User with this email already exists.")
            return redirect('signup')
            
        # Store form data in session
        signup_data = {k: v for k, v in request.POST.items()} 
        signup_data['skills'] = request.POST.getlist('skills')
        request.session['signup_data'] = signup_data
        
        # Generate and send OTP
        otp = generate_otp()
        request.session['signup_otp'] = otp
        
        if send_otp_email(email, otp):
            messages.success(request, f"OTP sent to {email}")
            return redirect('verify_otp')
        else:
            messages.error(request, "Failed to send OTP. Please try again.")
            return redirect('signup')
            
    return render(request, 'signup.html')

def verify_otp(request):
    """Verify OTP and create account"""
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('signup_otp')
        signup_data = request.session.get('signup_data')
        
        if not session_otp or not signup_data:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect('signup')
            
        if entered_otp == session_otp:
            # Create User
            user = User.objects.create_user(
                username=signup_data.get('email'),
                email=signup_data.get('email'),
                password=signup_data.get('password'),
                first_name=signup_data.get('name')
            )
            
            # Create Profile
            profile = Profile.objects.create(
                user=user,
                role=signup_data.get('role', 'consumer'),
                phone=signup_data.get('phone'),
                place=signup_data.get('place'),
                latitude=signup_data.get('latitude') if signup_data.get('latitude') else None,
                longitude=signup_data.get('longitude') if signup_data.get('longitude') else None,
                land_area=signup_data.get('land_area') if signup_data.get('land_area') else None,
                skills=signup_data.get('skills', []),
            )

            # Clear session
            del request.session['signup_otp']
            del request.session['signup_data']
            
            messages.success(request, "Account created successfully! Please login.")
            return redirect('index') # Redirecting to Index as Login page isn't defined yet
            
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            
    return render(request, 'verify_otp.html')

def login_view(request):
    """Login page with role-based redirection"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check for existing profile
            try:
                profile = user.profile
                role = profile.role
                
                if role == 'farmer':
                    return redirect('farmer_dashboard')
                elif role == 'consumer':
                    return redirect('marketplace') # or consumer_dashboard
                elif role == 'worker':
                    return redirect('worker_dashboard') # To be implemented
                elif role == 'govt':
                    # return redirect('govt_dashboard')
                    return redirect('index') # Placeholder
                else:
                    return redirect('index')
                    
            except Profile.DoesNotExist:
                messages.error(request, "Profile not found. Please contact support.")
                return redirect('login')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')

@login_required
def farmer_dashboard(request):
    """Farmer module dashboard"""
    return render(request, 'farmer_dashboard.html')

@login_required
def farmer_marketplace(request):
    """Farmer Marketplace Dashboard"""
    if request.user.profile.role != 'farmer':
        messages.error(request, "Only farmers can access this page.")
        return redirect('index')
    return render(request, 'farmer_marketplace.html')


def marketplace(request):
    """User (Consumer) marketplace"""
    # Filter only available products (not expired, not sold out/deleted logic if exists)
    # roughly, if expiry_date >= today
    today = timezone.now().date()
    today = timezone.now().date()
    products = Product.objects.filter(expiry_date__gte=today)
    
    # Filter Handling
    sort = request.GET.get('sort', 'newest')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    delivery = request.GET.get('delivery') == 'on'
    bidding = request.GET.get('bidding') == 'on'
    
    # Apply Filters
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if delivery:
        products = products.filter(delivery_available=True)
    if bidding:
        products = products.filter(is_bidding=True)
        
    # Apply Sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else: # newest or default
        products = products.order_by('-created_at')
    
    context = {
        'products': products,
        'current_filters': {
            'sort': sort,
            'min_price': min_price,
            'max_price': max_price,
            'delivery': delivery,
            'bidding': bidding
        }
    }
    return render(request, 'marketplace.html', context)

@login_required
def add_product(request):
    """Farmer: Add a new product"""
    if request.user.profile.role != 'farmer':
        messages.error(request, "Only farmers can add products.")
        return redirect('index')

    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            quantity = request.POST.get('quantity')
            price = request.POST.get('price')
            harvest_date = request.POST.get('harvest_date')
            expiry_date = request.POST.get('expiry_date')
            surplus_date = request.POST.get('surplus_date')
            surplus_rate = request.POST.get('surplus_rate')
            
            is_bidding = request.POST.get('is_bidding') == 'on'
            base_bid_price = request.POST.get('base_bid_price')
            bidding_duration_hours = request.POST.get('bidding_duration_hours')
            
            # Calculate bidding end time from duration in hours
            bidding_end_time = None
            if is_bidding and bidding_duration_hours:
                from datetime import timedelta
                bidding_end_time = timezone.now() + timedelta(hours=int(bidding_duration_hours))
            
            delivery_available = request.POST.get('delivery_available') == 'on'
            
            image = request.FILES.get('image')
            
            product = Product.objects.create(
                farmer=request.user,
                name=name,
                quantity=quantity,
                price=price,
                harvest_date=harvest_date,
                expiry_date=expiry_date,
                surplus_date=surplus_date if surplus_date else None,
                surplus_rate=surplus_rate if surplus_rate else None,
                is_bidding=is_bidding,
                base_bid_price=base_bid_price if base_bid_price else None,
                bidding_end_time=bidding_end_time if bidding_end_time else None,
                delivery_available=delivery_available,
                image=image
            )
            
            messages.success(request, "Product added successfully!")
            return redirect('farmer_dashboard')
            
        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
            return redirect('add_product')

    return render(request, 'add_product.html')

def product_detail(request, product_id):
    """View product details (for bidding or buying)"""
    try:
        product = Product.objects.get(id=product_id)
        
        # Get highest bid
        highest_bid = product.bids.order_by('-amount').first()
        
        context = {
            'product': product,
            'highest_bid': highest_bid
        }
        return render(request, 'product_detail.html', context)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('marketplace')

@login_required
def place_bid(request, product_id):
    """Place a bid on a product"""
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            amount = float(request.POST.get('amount'))
            
            if not product.is_bidding:
                messages.error(request, "Bidding is not enabled for this product.")
                return redirect('product_detail', product_id=product_id)
                
            if product.bidding_end_time and timezone.now() > product.bidding_end_time:
                messages.error(request, "Bidding has ended for this product.")
                return redirect('product_detail', product_id=product_id)
            
            # Check if bid is higher than base price
            highest_bid = product.bids.order_by('-amount').first()
            # Use base_bid_price for auction, fallback to regular price
            auction_base = float(product.base_bid_price) if product.base_bid_price else float(product.price)
            min_bid = float(highest_bid.amount) if highest_bid else auction_base
            
            if amount <= min_bid:
                messages.error(request, f"Bid must be higher than ₹{min_bid}")
                return redirect('product_detail', product_id=product_id)
            
            Bid.objects.create(
                product=product,
                user=request.user,
                amount=amount
            )
            
            messages.success(request, "Bid placed successfully!")
            return redirect('product_detail', product_id=product_id)
            
        except Product.DoesNotExist:
            messages.error(request, "Product not found")
        except ValueError:
             messages.error(request, "Invalid amount")
             
    return redirect('marketplace')

@login_required
def buy_product(request, product_id):
    """Buy a product immediately (Dummy Payment)"""
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            
            # Create Order
            # Use Buyer's profile location
            buyer_profile = request.user.profile
            
            Order.objects.create(
                product=product,
                buyer=request.user,
                quantity=product.quantity, # Buying all? Assuming 1 unit per listing for simplicity or "quantity" string
                total_price=product.current_price,
                status='confirmed',
                payment_status=True,
                location=buyer_profile.place,
                latitude=buyer_profile.latitude,
                longitude=buyer_profile.longitude
            )
            
            # Send Invoice Emails
            send_invoice_emails(order)
            
            messages.success(request, f"Payment Successful! You bought {product.name}.")
            return redirect('marketplace')
            
        except Exception as e:
            messages.error(request, f"Purchase failed: {str(e)}")
            return redirect('product_detail', product_id=product_id)
            
    return redirect('marketplace')

@login_required
def my_orders(request):
    """Farmer: View incoming orders"""
    if request.user.profile.role != 'farmer':
        return redirect('index')
        
    # Get products by this farmer
    products = Product.objects.filter(farmer=request.user)
    # Get orders for these products
    orders = Order.objects.filter(product__in=products).order_by('-created_at')
    
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def optimize_route(request):
    """Generate Google Maps route for selected orders"""
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        orders = Order.objects.filter(id__in=order_ids)
        
        if not orders:
            messages.error(request, "No orders selected.")
            return redirect('my_orders')
        
        # Simple Nearest Neighbor Optimization
        # Start at Farmer Location
        farmer_profile = request.user.profile
        current_loc = (farmer_profile.latitude, farmer_profile.longitude)
        
        if not current_loc[0] or not current_loc[1]:
            messages.error(request, "Please set your farm location in profile first.")
            return redirect('my_orders')
            
        unvisited = []
        for o in orders:
            if o.latitude and o.longitude:
                unvisited.append({
                    'id': o.id, 
                    'lat': o.latitude, 
                    'lon': o.longitude, 
                    'obj': o
                })
        
        route = []
        
        while unvisited:
            # Find nearest
            nearest = None
            min_dist = float('inf')
            
            for point in unvisited:
                # Euclidean distance is approx okay for local small scale, 
                # or use Haversine. Let's use simple Euclidean for hackathon speed 
                # (lat/lon degrees are roughly grid-like locally)
                dist = (point['lat'] - current_loc[0])**2 + (point['lon'] - current_loc[1])**2
                if dist < min_dist:
                    min_dist = dist
                    nearest = point
            
            if nearest:
                route.append(nearest)
                current_loc = (nearest['lat'], nearest['lon'])
                unvisited.remove(nearest)
        
        # Construct Google Maps URL
        # https://www.google.com/maps/dir/?api=1&origin=LAT,LON&destination=LAT,LON&waypoints=LAT,LON|LAT,LON
        
        origin = f"{farmer_profile.latitude},{farmer_profile.longitude}"
        if route:
            destination = f"{route[-1]['lat']},{route[-1]['lon']}"
            waypoints = "|".join([f"{p['lat']},{p['lon']}" for p in route[:-1]])
            
            maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
            if waypoints:
                maps_url += f"&waypoints={waypoints}"
                
            return redirect(maps_url)
        else:
            messages.error(request, "No valid locations found in selected orders.")
            return redirect('my_orders')
            
    return redirect('my_orders')

# Weather API Endpoints
@login_required
@require_http_methods(["GET"])
def get_current_weather(request):
    """Get current weather for logged-in farmer"""
    try:
        profile = request.user.profile
        
        if profile.role != 'farmer':
            return JsonResponse({'error': 'Only farmers can access weather data'}, status=403)
        
        if not profile.latitude or not profile.longitude:
            return JsonResponse({
                'error': 'Location not set. Please update your profile with farm coordinates.',
                'weather': None,
                'alerts': []
            }, status=400)
        
        weather_service = WeatherService()
        data = weather_service.get_weather(profile.latitude, profile.longitude)
        
        # Add telegram status
        data['telegram_linked'] = bool(profile.telegram_chat_id)
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def send_test_alert(request):
    """Send a test alert for demo/hackathon purposes"""
    try:
        profile = request.user.profile
        
        if profile.role != 'farmer':
            return JsonResponse({'error': 'Only farmers can receive alerts'}, status=403)
        
        weather_service = WeatherService()
        telegram_service = TelegramService()
        
        # Create test alert
        test_alerts = weather_service.create_test_alert()
        
        messages_sent = {
            'telegram': False,
            'web': True  # Web notification handled by frontend
        }
        
        # Send to Telegram if linked
        if profile.telegram_chat_id and profile.telegram_enabled:
            result = telegram_service.send_test_alert(
                profile.telegram_chat_id,
                profile.language_preference
            )
            messages_sent['telegram'] = result.get('ok', False)
        
        return JsonResponse({
            'success': True,
            'message': 'Test alert triggered successfully!',
            'alerts': test_alerts,
            'messages_sent': messages_sent,
            'telegram_linked': bool(profile.telegram_chat_id)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def link_telegram(request):
    """Link Telegram account by saving chat ID"""
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        
        if not chat_id:
            return JsonResponse({'error': 'Chat ID required'}, status=400)
        
        profile = request.user.profile
        profile.telegram_chat_id = chat_id
        profile.telegram_enabled = True
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Telegram linked successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

import random
import string

# Store pending link codes (in production, use Redis/database)
pending_link_codes = {}

@login_required
@require_http_methods(["GET"])
def generate_telegram_code(request):
    """Generate a unique code for Telegram linking"""
    try:
        profile = request.user.profile
        
        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Store with user ID (expires conceptually, but simple for hackathon)
        pending_link_codes[code] = {
            'user_id': request.user.id,
            'farmer_name': request.user.first_name
        }
        
        return JsonResponse({
            'success': True,
            'code': code,
            'instructions': f'Send this code to @harvestsyncbot on Telegram: {code}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """Handle incoming Telegram bot updates (webhook mode)"""
    try:
        data = json.loads(request.body)
        
        if 'message' not in data:
            return JsonResponse({'ok': True})
        
        message = data['message']
        chat_id = str(message['chat']['id'])
        text = message.get('text', '').strip()
        
        telegram_service = TelegramService()
        
        # Handle /start command
        if text.startswith('/start'):
            telegram_service.send_message(
                chat_id,
                "🌾 <b>Welcome to Harvest Sync!</b>\n\n"
                "To link your account:\n"
                "1. Go to your Farmer Dashboard\n"
                "2. Click 'Get Link Code'\n"
                "3. Send the 6-digit code here\n\n"
                "Example: <code>123456</code>"
            )
            return JsonResponse({'ok': True})
        
        # Check if it's a 6-digit code
        if text.isdigit() and len(text) == 6:
            if text in pending_link_codes:
                user_data = pending_link_codes[text]
                user_id = user_data['user_id']
                farmer_name = user_data['farmer_name']
                
                # Link the account
                from django.contrib.auth.models import User
                user = User.objects.get(id=user_id)
                profile = user.profile
                profile.telegram_chat_id = chat_id
                profile.telegram_enabled = True
                profile.save()
                
                # Remove used code
                del pending_link_codes[text]
                
                telegram_service.send_message(
                    chat_id,
                    f"✅ <b>Account Linked Successfully!</b>\n\n"
                    f"Hello {farmer_name}! 👋\n\n"
                    f"You will now receive weather alerts and notifications here.\n\n"
                    f"🌾 Stay safe and protect your crops!"
                )
            else:
                telegram_service.send_message(
                    chat_id,
                    "❌ Invalid or expired code.\n\n"
                    "Please get a new code from your Dashboard."
                )
            return JsonResponse({'ok': True})
        
        # Default response
        telegram_service.send_message(
            chat_id,
            "🤔 I didn't understand that.\n\n"
            "Send your 6-digit link code or type /start for help."
        )
        
        return JsonResponse({'ok': True})
        
    except Exception as e:
        print(f"Telegram webhook error: {e}")
        return JsonResponse({'ok': True})

@require_http_methods(["GET"])
def check_telegram_updates(request):
    """Poll for Telegram updates and process them (for dev without webhook)"""
    try:
        telegram_service = TelegramService()
        updates = telegram_service.get_updates()
        
        if not updates.get('ok'):
            return JsonResponse({'error': 'Failed to get updates'}, status=500)
        
        results = updates.get('result', [])
        processed = 0
        
        for update in results:
            if 'message' not in update:
                continue
                
            message = update['message']
            chat_id = str(message['chat']['id'])
            text = message.get('text', '').strip()
            
            # Handle /start command
            if text.startswith('/start'):
                telegram_service.send_message(
                    chat_id,
                    "🌾 <b>Welcome to Harvest Sync!</b>\n\n"
                    "To link your account:\n"
                    "1. Go to your Farmer Dashboard\n"
                    "2. Click 'Get Link Code'\n"
                    "3. Send the 6-digit code here\n\n"
                    "Example: <code>123456</code>"
                )
                processed += 1
                continue
            
            # Check if it's a 6-digit code
            if text.isdigit() and len(text) == 6:
                if text in pending_link_codes:
                    user_data = pending_link_codes[text]
                    user_id = user_data['user_id']
                    farmer_name = user_data['farmer_name']
                    
                    # Link the account
                    from django.contrib.auth.models import User
                    user = User.objects.get(id=user_id)
                    profile = user.profile
                    profile.telegram_chat_id = chat_id
                    profile.telegram_enabled = True
                    profile.save()
                    
                    # Remove used code
                    del pending_link_codes[text]
                    
                    telegram_service.send_message(
                        chat_id,
                        f"✅ <b>Account Linked Successfully!</b>\n\n"
                        f"Hello {farmer_name}! 👋\n\n"
                        f"You will now receive weather alerts here."
                    )
                else:
                    telegram_service.send_message(
                        chat_id,
                        "❌ Invalid or expired code.\n\n"
                        "Please get a new code from your Dashboard."
                    )
                processed += 1
        
        return JsonResponse({
            'success': True,
            'updates': len(results),
            'processed': processed
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Product Management Views
@login_required
def my_products(request):
    """Farmer: View all their products"""
    if request.user.profile.role != 'farmer':
        messages.error(request, "Only farmers can access this page.")
        return redirect('index')
    
    products = Product.objects.filter(farmer=request.user).order_by('-created_at')
    
    context = {
        'products': products
    }
    return render(request, 'my_products.html', context)

@login_required
def edit_product(request, product_id):
    """Farmer: Edit an existing product"""
    try:
        product = Product.objects.get(id=product_id, farmer=request.user)
    except Product.DoesNotExist:
        messages.error(request, "Product not found or you don't have permission to edit it.")
        return redirect('my_products')
    
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.quantity = request.POST.get('quantity')
            product.price = request.POST.get('price')
            product.harvest_date = request.POST.get('harvest_date')
            product.expiry_date = request.POST.get('expiry_date')
            product.surplus_date = request.POST.get('surplus_date') or None
            product.surplus_rate = request.POST.get('surplus_rate') or None
            
            product.is_bidding = request.POST.get('is_bidding') == 'on'
            product.base_bid_price = request.POST.get('base_bid_price') or None
            
            # Handle bidding duration in hours
            bidding_duration_hours = request.POST.get('bidding_duration_hours')
            if product.is_bidding and bidding_duration_hours:
                from datetime import timedelta
                product.bidding_end_time = timezone.now() + timedelta(hours=int(bidding_duration_hours))
            else:
                product.bidding_end_time = None
            
            product.delivery_available = request.POST.get('delivery_available') == 'on'
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            
            messages.success(request, "Product updated successfully!")
            return redirect('my_products')
            
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
            return redirect('edit_product', product_id=product_id)
    
    context = {
        'product': product
    }
    return render(request, 'edit_product.html', context)

@login_required
def delete_product(request, product_id):
    """Farmer: Delete a product"""
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id, farmer=request.user)
            product_name = product.name
            product.delete()
            messages.success(request, f"Product '{product_name}' deleted successfully!")
        except Product.DoesNotExist:
            messages.error(request, "Product not found or you don't have permission to delete it.")
        except Exception as e:
            messages.error(request, f"Error deleting product: {str(e)}")
    
    return redirect('my_products')

@login_required
def analytics_view(request):
    """Analytics dashboard for farmers"""
    if request.user.profile.role != 'farmer':
        return redirect('index')
    return render(request, 'analytics.html')

# Cart Views
@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart"""
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
            
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()
            
            messages.success(request, f"{product.name} added to cart!")
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            
    return redirect('marketplace')

@login_required
def view_cart(request):
    """View items in cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        except CartItem.DoesNotExist:
            pass
    return redirect('view_cart')

@login_required
def checkout_cart(request):
    """Checkout all items in cart"""
    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            messages.error(request, "Cart is empty!")
            return redirect('view_cart')
            
        buyer_profile = request.user.profile
        
        # Create orders for each item
        for item in cart.items.all():
            Order.objects.create(
                product=item.product,
                buyer=request.user,
                quantity=f"{item.quantity} x {item.product.quantity}",
                total_price=item.total_price,
                status='confirmed',
                payment_status=True,
                location=buyer_profile.place,
                latitude=buyer_profile.latitude,
                longitude=buyer_profile.longitude
            )
            
        # Clear cart
        cart.items.all().delete()
        
        messages.success(request, "Checkout successful! Orders placed.")
        return redirect('marketplace')
            
    return redirect('view_cart')
