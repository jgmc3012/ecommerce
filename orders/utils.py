from .models import Order

from django.urls import reverse

def get_or_create_order(request, cart):
    order = cart.order

    if not order and request.user.is_authenticated:
        order = Order.objects.create(cart=cart, user=request.user)
    
    request.session['order_id'] = order.order_id

    return order

def breadcrumb(products=True, address=False, payment=False, confirmation=False):
    return [
        {'title': 'Productos', 'active': products, 'url': reverse('orders:order')},
        {'title': 'Direccion', 'active': address, 'url': reverse('orders:address')},
        {'title': 'Pago', 'active': payment, 'url': reverse('index')},
        {'title': 'Confirmación', 'active': confirmation, 'url': reverse('orders:confirm')},
    ]

def destroy_order(request):
    request.session['order_id'] = None