import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Send OTP execution email"""
    subject = 'Verify your email - Harvest Sync'
    message = f'Your OTP for verification is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    try:
        send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_invoice_emails(order):
    """Send invoice emails to buyer and seller"""
    try:
        # 1. Email to Buyer
        buyer_subject = f'Order Confirmation - Order #{order.id}'
        buyer_message = f"""
Dear {order.buyer.first_name},

Thank you for your order!

Order Details:
----------------
Order ID: #{order.id}
Product: {order.product.name}
Quantity: {order.quantity}
Total Price: ₹{order.total_price}
Status: {order.status}

Seller: {order.product.farmer.profile.place}
----------------

Your order has been confirmed and will be processed soon.

Best regards,
Harvest Sync Team
        """
        
        send_mail(
            buyer_subject,
            buyer_message,
            settings.EMAIL_HOST_USER,
            [order.buyer.email],
            fail_silently=False,
        )

        # 2. Email to Farmer (Seller)
        seller_subject = f'New Order Received - Order #{order.id}'
        seller_message = f"""
Dear {order.product.farmer.first_name},

You have received a new order!

Order Details:
----------------
Order ID: #{order.id}
Product: {order.product.name}
Quantity: {order.quantity}
Total Price: ₹{order.total_price}

Buyer Details:
Name: {order.buyer.first_name}
Email: {order.buyer.email}
Location: {order.location}
----------------

Please check your dashboard to process this order.

Best regards,
Harvest Sync Team
        """
        
        send_mail(
            seller_subject,
            seller_message,
            settings.EMAIL_HOST_USER,
            [order.product.farmer.email],
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending invoice emails: {e}")
        return False

def send_new_bid_email(bid):
    """Send email to farmer when a new bid is placed"""
    try:
        product = bid.product
        farmer = product.farmer
        bidder = bid.user
        
        subject = f'New Bid on {product.name} - Harvest Sync'
        message = f"""
Dear {farmer.first_name},

You have received a new bid on your product!

Product: {product.name}
Bid Amount: ₹{bid.amount}
Bidder: {bidder.first_name}

Current Status:
- Base Price: ₹{product.base_bid_price or product.price}
- Bidding Ends: {product.bidding_end_time.strftime('%B %d, %Y at %I:%M %p') if product.bidding_end_time else 'Soon'}

Check your dashboard for more details.

Best regards,
Harvest Sync Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [farmer.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending new bid email: {e}")
        return False

def send_bid_won_email(bid):
    """Send email to consumer when they win a bid"""
    try:
        product = bid.product
        winner = bid.user
        farmer = product.farmer
        
        subject = f'🎉 You Won the Bid for {product.name}! - Harvest Sync'
        message = f"""
Dear {winner.first_name},

Congratulations! You have won the auction!

Product: {product.name}
Winning Bid: ₹{bid.amount}
Seller: {farmer.first_name}
Location: {farmer.profile.place}

Please login to your account to complete the purchase.

Best regards,
Harvest Sync Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [winner.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending bid won email: {e}")
        return False
