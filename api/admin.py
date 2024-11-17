from django.contrib import admin
from .models import Category, Review, Product, ProductImage, Cart, Cartitems, SavedItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_id', 'slug', 'icon')
    search_fields = ('title', 'category_id')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'date_created', 'name')
    search_fields = ('product__name', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'category', 'price', 'inventory')
    search_fields = ('name', 'category__title')
    list_filter = ('category', 'discount', 'top_deal', 'flash_sales')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'created', 'completed', 'session_id')
    search_fields = ('cart_id', 'session_id')
    list_filter = ('completed',)

@admin.register(Cartitems)
class CartitemsAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subTotal')
    search_fields = ('cart__cart_id', 'product__name')

@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'added')
    search_fields = ('product__name', 'added')
    
    
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'pending_status', 'owner', 'total_price']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity']