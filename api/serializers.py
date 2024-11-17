from rest_framework import serializers
from .models import Category, Review, Product, ProductImage, Cart, Cartitems, SavedItem,Order,OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class SimpleProductSerializers(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','price','name']

class CartitemsSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cartitems
        fields = ['id', 'cart', 'product', 'quantity', 'total_price']
        extra_kwargs = {'cart': {'required': False, 'allow_null': True}}

    def get_total_price(self, instance):
        if instance.product and instance.product.price:
            return instance.quantity * instance.product.price
        return 0

class CartSerializer(serializers.ModelSerializer):
    card_id = serializers.UUIDField(read_only=True)
    items = CartitemsSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['card_id', 'items', 'grand_total']
        
    def get_grand_total(self, cart):
        items = cart.items.all()
        total = sum([item.quantity * item.product.price for item in items if item.product and item.product.price])
        return total
    
class SavedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedItem
        fields = '__all__'
        
class OrderItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializers()
    class Meta:
        model = OrderItem
        fields = '__all__'
        


class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
        
          
from django.db import transaction
from rest_framework import serializers
from .models import Order, Cartitems, OrderItem

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    @transaction.atomic
    def save(self, **kwargs):
        cart_id = self.validated_data.get('cart_id')
        user_id = self.context.get('user_id')
        
        order = Order.objects.create(owner_id=user_id)
        cart_items = Cartitems.objects.filter(cart_id=cart_id)
        
        order_items = [
            OrderItem(order=order, product=item.product, quantity=item.quantity)
            for item in cart_items
        ]
        
        OrderItem.objects.bulk_create(order_items)
        Cart.objects.get(cart_id=cart_id).delete()
        
        return order
    