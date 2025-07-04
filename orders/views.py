from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import FoodItem, Cart, Order, OrderItem, UserAddress
import json
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def home(request):
    food_items = FoodItem.objects.all()
    food_item = food_items.filter(id=1).first()  # Safely get the first matching object
    if food_item:
        print(food_item.image.url)  # Access the image URL only if the object exists
    return render(request, 'home.html', {'food_items': food_items})

@csrf_exempt  # Temporarily disable CSRF for testing (use CSRF token in production)
def add_to_cart(request, food_id):
    if request.method == 'POST':
        try:
            food_item = FoodItem.objects.get(id=food_id)
            cart_item, created = Cart.objects.get_or_create(
                food_item=food_item,
                defaults={'quantity': 1}  # Ensure quantity is set for new items
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            return JsonResponse({'message': 'Item added to cart!'})
        except FoodItem.DoesNotExist:
            return JsonResponse({'message': 'Food item not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

def view_cart(request):
    cart_items = Cart.objects.all()
    for item in cart_items:
        item.total_price = item.food_item.price * item.quantity
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        # Get address from session
        address = request.session.get('delivery_address', '')
        cart_items = Cart.objects.all()
        if not cart_items:
            return JsonResponse({'message': 'Cart is empty!'}, status=400)
        total_price = sum(item.food_item.price * item.quantity for item in cart_items)
        order = Order.objects.create(address=address, total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(order=order, food_item=item.food_item, quantity=item.quantity)
        cart_items.delete()
        # Optionally clear the address from session
        request.session.pop('delivery_address', None)
        # Redirect to my orders page after placing order
        return JsonResponse({'redirect_url': '/my-orders/'})
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def update_cart_quantity(request, cart_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            if quantity < 1:
                return JsonResponse({'message': 'Quantity must be at least 1.'}, status=400)
            cart_item = Cart.objects.get(id=cart_id)
            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({'message': 'Quantity updated!'})
        except Cart.DoesNotExist:
            return JsonResponse({'message': 'Cart item not found!'}, status=404)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def delete_cart_item(request, cart_id):
    if request.method == 'POST':
        try:
            cart_item = Cart.objects.get(id=cart_id)
            cart_item.delete()
            return JsonResponse({'message': 'Item removed from cart!'})
        except Cart.DoesNotExist:
            return JsonResponse({'message': 'Cart item not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@login_required
def my_orders(request):
    orders = Order.objects.all().order_by('-created_at')  # or filter by user if needed
    return render(request, 'my_orders.html', {'orders': orders})

@csrf_exempt
def delete_order(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            return JsonResponse({'message': 'Order deleted successfully!'})
        except Order.DoesNotExist:
            return JsonResponse({'message': 'Order not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@csrf_exempt
def create_stripe_session(request):
    if request.method == 'POST':
        cart_items = Cart.objects.all()
        if not cart_items:
            return JsonResponse({'message': 'Cart is empty!'}, status=400)
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': item.food_item.name,
                    },
                    'unit_amount': int(item.food_item.price * 100),
                },
                'quantity': item.quantity,
            })
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri('/cart/'),
                cancel_url=request.build_absolute_uri('/cart/'),
            )
            return JsonResponse({'session_url': session.url})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    return JsonResponse({'message': 'Invalid request method!'}, status=400)

@login_required
def address(request):
    previous_addresses = UserAddress.objects.filter(user=request.user)
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address')
        if selected_address_id:
            address_obj = UserAddress.objects.get(id=selected_address_id, user=request.user)
            address_data = {
                'name': address_obj.name,
                'phone': address_obj.phone,
                'area': address_obj.area,
                'city': address_obj.city,
                'landmark': address_obj.landmark,
                'district': address_obj.district,
                'zipcode': address_obj.zipcode,
            }
        else:
            address_data = {
                'name': request.POST.get('name'),
                'phone': request.POST.get('phone'),
                'area': request.POST.get('area'),
                'city': request.POST.get('city'),
                'landmark': request.POST.get('landmark', ''),
                'district': request.POST.get('district'),
                'zipcode': request.POST.get('zipcode'),
            }
            # Save new address for future use
            UserAddress.objects.create(user=request.user, **address_data)
        request.session['delivery_address'] = address_data
        return redirect('confirm_order')
    return render(request, 'address.html', {'previous_addresses': previous_addresses})

@login_required
def confirm_order(request):
    address = request.session.get('delivery_address')
    if not address:
        return redirect('address')
    return render(request, 'confirm_order.html', {'address': address})

@require_POST
@login_required
def delete_address(request, address_id):
    try:
        address = UserAddress.objects.get(id=address_id, user=request.user)
        address.delete()
        return JsonResponse({'success': True, 'message': 'Address deleted.'})
    except UserAddress.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Address not found.'}, status=404)
from django.contrib import messages
from django.urls import reverse

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect(reverse('login'))
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
from .models import UserProfile
from .models import UserProfile

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {'profile': profile})
from django.contrib.auth import logout
from django.shortcuts import redirect

# def logout_view(request):
#     logout(request)
#     return redirect('home')