from django.contrib import admin
from .models import (
    Category, Brand, Product, ProductVariant, ProductImage,
    ProductSpecification, Review, Banner, Cart, CartItem,
    Order, OrderItem, UserProfile, Wishlist, MpesaTransaction
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'order']
    list_filter = ['is_active', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'is_active', 'is_featured', 'is_hot', 'is_new', 'created_at']
    list_filter = ['is_active', 'is_featured', 'is_hot', 'is_new', 'brand', 'category']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'sku', 'brand__name']
    inlines = [ProductVariantInline, ProductImageInline, ProductSpecInline]
    list_editable = ['is_active', 'is_featured', 'is_hot', 'is_new']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_name', 'price', 'quantity', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'status', 'payment_status', 'payment_method', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_editable = ['status']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'order']
    list_filter = ['position', 'is_active']
    list_editable = ['is_active', 'order']


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ['checkout_request_id', 'order', 'amount', 'phone', 'status', 'created_at']
    list_filter = ['status']
    readonly_fields = ['checkout_request_id', 'merchant_request_id', 'created_at', 'updated_at']


admin.site.register(Review)
admin.site.register(UserProfile)
admin.site.register(Wishlist)
admin.site.register(Cart)