from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/verify-otp/', views.verify_otp, name='verify_otp'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('farmer/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/analytics/', views.analytics_view, name='analytics'),
    path('farmer/marketplace/', views.farmer_marketplace, name='farmer_marketplace'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/bid/', views.place_bid, name='place_bid'),
    path('products/<int:product_id>/buy/', views.buy_product, name='buy_product'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/consumer/', views.consumer_orders, name='consumer_orders'),
    path('orders/bids/', views.consumer_bids, name='consumer_bids'),
    path('orders/route/', views.optimize_route, name='optimize_route'),
    
    # Product Management
    path('products/my/', views.my_products, name='my_products'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    
    # Weather API endpoints
    path('api/weather/current/', views.get_current_weather, name='get_current_weather'),
    path('api/weather/test-alert/', views.send_test_alert, name='send_test_alert'),
    path('api/telegram/link/', views.link_telegram, name='link_telegram'),
    path('api/telegram/generate-code/', views.generate_telegram_code, name='generate_telegram_code'),
    path('api/telegram/check-updates/', views.check_telegram_updates, name='check_telegram_updates'),
    path('api/telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    
    # Cart
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
]
