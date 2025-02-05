from django.shortcuts import render, get_object_or_404
from itertools import product
from urllib import response
from api.filters import ProductFilter
from rest_framework.decorators import api_view, action
from api.serializers import *
from storeapp.models import *
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import requests
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def initiate_payment(amount, email, order_id):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Example Product',
                        'description': 'Description of the product',
                    },
                    'unit_amount': int(amount * 100),
                },
                'quantity': 1,
            }],
            metadata={'order_id': order_id},
            customer_email=email,
            mode='payment',
            success_url=f'http://127.0.0.1:8000/orders/{order_id}/success-payment/',
            cancel_url=f'http://127.0.0.1:8000/orders/{order_id}/cancel-payment/',
        )
        # Returning the session URL to redirect the user
        return session.url
    except Exception as e:
        return None  # Return None on error to handle the failure case

class ProductsViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['old_price']
    pagination_class = PageNumberPagination


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])
    
    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]
    
    def get_queryset(self):
        return Cartitems.objects.filter(cart_id=self.kwargs["cart_pk"])
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    @action(detail=True, methods=['POST'])
    def pay(self, request, pk):
        order = self.get_object()
        amount = order.total_price
        email = request.user.email
        order_id = str(order.id)
        session_url = initiate_payment(amount, email, order_id)
        
        if session_url:
            return Response({'session_url': session_url})
        else:
            return Response({'error': 'Payment initiation failed'}, status=status.HTTP_400_BAD_REQUEST)
    
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
    

class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        Profile.objects.create(
            name=request.data["name"],
            bio=request.data["bio"],
            picture=request.data["picture"]
        )
        return Response("Profile created successfully", status=status.HTTP_200_OK)
