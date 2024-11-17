from rest_framework import viewsets
from .models import Category, Review, Product, ProductImage, Cart, Cartitems, SavedItem
from .serializers import CategorySerializer, ReviewSerializer, ProductSerializer, CreateOrderSerializer,ProductImageSerializer,OrderItemSerializer, CartSerializer, CartitemsSerializer, SavedItemSerializer,OrderSerializer
from .filter import *
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import stripe
from django.conf import settings


import stripe
from django.conf import settings
from rest_framework.response import Response

# Set the Stripe API key from Django settings
stripe.api_key = settings.STRIPE_SECRET_KEY

def initiate_payment(amount, email, order_id):
    try:
        # Create payment session in Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # Replace with the required currency code
                    'product_data': {
                        'name': 'Example Product',
                        'description': 'Description of the product',
                    },
                    'unit_amount': int(amount * 100),  # Convert amount to cents or smallest unit of the currency
                },
                'quantity': 1,
            }],
            metadata={
                'order_id': order_id,
            },
            customer_email=email,
            mode='payment',
            success_url='http://127.0.0.1:8000/order/{}/success-payment/'.format(order_id),
            cancel_url='http://127.0.0.1:8000/order/{}/cancel-payment/'.format(order_id),  # Add a cancel URL if needed
        )
        
        return Response({'session_url': session.url})
    except Exception as e:
        print(f"Error creating Stripe session: {e}")
        return Response({'error': str(e)}, status=500)



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class=ProductFilter
    search_fields=['name','description']
    ordering_fields=['old_price']
    pagination_class=PageNumberPagination

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from .models import Cart
from .serializers import CartSerializer

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    class CartViewSet(viewsets.ViewSet):
        
        def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
        
        # Retrieve the cart_id from the newly created Cart object
            cart_id = None
            if hasattr(serializer.instance, 'id'):
                cart_id = serializer.instance.id
        
        # Customize the JSON response here
            response_data = {
                "message": "Cart created successfully",
                "cart_id": cart_id,
                "data": serializer.data
            }
        
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
class CartitemsViewSet(viewsets.ModelViewSet):
    queryset = Cartitems.objects.all()
    serializer_class = CartitemsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class SavedItemViewSet(viewsets.ModelViewSet):
    queryset = SavedItem.objects.all()
    serializer_class = SavedItemSerializer



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    
    @action(detail=True, methods=['POST'])
    def pay(self, request, pk):
        order = self.get_object()
        amount = order.total_price
        email = request.user.email
        order_id = str(order.id)
        return initiate_payment(amount, email, order_id)
    
    @action(detail=True, methods=['GET'])
    def success_payment(self, request, pk=None):
        order = self.get_object()
        order.pending_status = 'C'  # Assuming 'C' represents a completed status
        order.save()
        
        serializer = OrderSerializer(order)
        data = {
            'msg': 'Payment Successful',
            'data': serializer.data
        }
        
        return Response(data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user_id': self.request.user.id})
        return context
    
    
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    
    
    
    

