from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ReviewViewSet, ProductViewSet, ProductImageViewSet, CartViewSet, CartitemsViewSet, SavedItemViewSet,OrderViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cartitems', CartitemsViewSet)
router.register(r'saveditems', SavedItemViewSet)
router.register(r'order', OrderViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:pk>/pay/', OrderViewSet.as_view({'post': 'pay'}), name='order-pay'),
    path('orders/<int:pk>/success-payment/', OrderViewSet.as_view({'get': 'success_payment'}), name='order-success-payment'),
]