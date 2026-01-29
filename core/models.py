from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('consumer', 'Consumer'),
        ('worker', 'Worker'),
        ('govt', 'Government Official'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='consumer')
    phone = models.CharField(max_length=15)
    place = models.CharField(max_length=100)
    
    # Farmer specific
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    land_area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Worker specific
    skills = models.JSONField(default=list, blank=True)
    
    # Notification preferences
    telegram_chat_id = models.CharField(max_length=100, null=True, blank=True)
    telegram_enabled = models.BooleanField(default=False)
    web_notifications_enabled = models.BooleanField(default=True)
    language_preference = models.CharField(max_length=5, default='en', choices=[('en', 'English'), ('ml', 'Malayalam')])
    last_weather_check = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Product(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50) # e.g., "10 kg"
    harvest_date = models.DateField()
    expiry_date = models.DateField()
    surplus_date = models.DateField(null=True, blank=True)
    surplus_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Base Price
    
    # Bidding
    is_bidding = models.BooleanField(default=False)
    base_bid_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Auction starting price
    bidding_end_time = models.DateTimeField(null=True, blank=True)
    
    # Delivery
    delivery_available = models.BooleanField(default=False)
    
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_surplus_active(self):
        from django.utils import timezone
        if self.surplus_date and timezone.now().date() >= self.surplus_date:
            return True
        return False

    @property
    def current_price(self):
        if self.is_surplus_active and self.surplus_rate:
            return self.surplus_rate
        return self.price

class Bid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} for {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    quantity = models.CharField(max_length=50) # Matching product quantity type for now
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.BooleanField(default=False) # False=Unpaid, True=Paid
    location = models.CharField(max_length=255) # Simplified location string
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.current_price * self.quantity
