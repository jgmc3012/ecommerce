import uuid
import decimal

from django.db import models

from users.models import User
from products.models import Product

from orders.common import OrderStatus

from django.db.models.signals import pre_save
from django.db.models.signals import m2m_changed  
from django.db.models.signals import post_save

class Cart(models.Model):
    cart_id = models.CharField( max_length=100, null=False, blank=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartProducts')
    subtotal = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)
    total = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    FEE = 0.05

    def __str__(self):
        return self.cart_id

    def update_totals(self):
        self.update_subtotals()
        self.update_total()

        if self.order:
            self.order.update_total()
    
    def update_subtotals(self):
        self.subtotal = sum(
            [ cp.product.price * cp.quantity for cp in self.products_related() ]
        )
        self.save()

    def update_total(self):
        self.total = self.subtotal + (self.subtotal * decimal.Decimal(Cart.FEE))
        self.save()

    def products_related(self):
        return self.cartproducts_set.select_related('product')

    @property
    def order(self):
        return self.order_set.filter(status=OrderStatus.CREATED).first()

def set_card_id(sender, instance, *args, **kwargs):
    if not instance.cart_id:
        instance.cart_id = str(uuid.uuid4())

class CardProductsManager(models.Manager):
    def create_or_update_quantity(self, cart, product, quantity=1):
        object, created = self.get_or_create(cart=cart, product=product)
        if not created:
            quantity += object.quantity

        object.update_quantity(quantity)
        return object

class CartProducts(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CardProductsManager()

    def update_quantity(self, quantity=1):
        self.quantity = quantity
        self.save()

def updater_totals(sender, instance, action, *args, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        instance.update_totals()

def post_save_update_totals(sender, instance, *args, **kwargs):
    instance.cart.update_totals()

pre_save.connect(set_card_id, sender=Cart)
post_save.connect(post_save_update_totals, sender=CartProducts)
m2m_changed.connect(updater_totals, sender=Cart.products.through)