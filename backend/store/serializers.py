from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Brand, Product, ProductVariant, ProductImage,
    ProductSpecification, Review, Banner, Cart, CartItem,
    Order, OrderItem, RecentlyViewed, UserProfile, Wishlist
)


# ──────────────────────────────────────────────
# Category
# ──────────────────────────────────────────────
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'image']


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'image', 'parent', 'subcategories', 'is_active', 'order']


# ──────────────────────────────────────────────
# Brand
# ──────────────────────────────────────────────
class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description', 'is_featured', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


# ──────────────────────────────────────────────
# Product
# ──────────────────────────────────────────────
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductVariantSerializer(serializers.ModelSerializer):
    discount_percentage = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'storage', 'color', 'ram', 'price',
                  'sale_price', 'effective_price', 'discount_percentage', 'stock', 'is_active']


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ['key', 'value', 'order']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'title', 'comment',
                  'is_verified_purchase', 'created_at']
        read_only_fields = ['user', 'is_verified_purchase', 'created_at']

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing products."""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_image = ProductImageSerializer(read_only=True)
    min_price = serializers.ReadOnlyField()
    max_price = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand_name', 'category_name',
            'main_image', 'min_price', 'max_price', 'short_description',
            'is_featured', 'is_hot', 'is_new', 'average_rating', 'review_count',
            'created_at'
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for product detail page."""
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    min_price = serializers.ReadOnlyField()
    max_price = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'brand', 'category',
            'description', 'short_description', 'condition',
            'images', 'variants', 'specifications', 'reviews',
            'is_featured', 'is_hot', 'is_new',
            'min_price', 'max_price', 'average_rating', 'review_count',
            'tags', 'created_at'
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()


# ──────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────
class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'subtitle', 'image', 'mobile_image',
                  'link', 'position', 'badge_text', 'badge_color', 'order']


# ──────────────────────────────────────────────
# Cart
# ──────────────────────────────────────────────
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'variant', 'variant_id', 'quantity', 'subtotal', 'added_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        variant_id = validated_data.pop('variant_id', None)
        cart = validated_data['cart']

        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.get(id=variant_id) if variant_id else None

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={'quantity': validated_data.get('quantity', 1)}
        )
        if not created:
            item.quantity += validated_data.get('quantity', 1)
            item.save()
        return item


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'updated_at']


# ──────────────────────────────────────────────
# Order
# ──────────────────────────────────────────────
class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'variant_name', 'price', 'quantity', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'payment_method',
            'full_name', 'email', 'phone', 'shipping_address', 'city', 'county',
            'shipping_fee', 'subtotal', 'total', 'items',
            'mpesa_phone', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'status', 'payment_status',
                            'mpesa_checkout_request_id', 'mpesa_transaction_id']


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone', 'shipping_address',
            'city', 'county', 'payment_method', 'mpesa_phone', 'notes'
        ]


# ──────────────────────────────────────────────
# User & Profile
# ──────────────────────────────────────────────
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'avatar', 'address', 'city', 'county']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Email already registered.'})
        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        UserProfile.objects.create(user=user, phone=phone)
        return user


# ──────────────────────────────────────────────
# Recently Viewed & Wishlist
# ──────────────────────────────────────────────
class RecentlyViewedSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = RecentlyViewed
        fields = ['product', 'viewed_at']


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']


# ──────────────────────────────────────────────
# M-Pesa STK Push
# ──────────────────────────────────────────────
class MpesaSTKPushSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    order_id = serializers.UUIDField()

    def validate_phone(self, value):
        phone = value.replace('+', '').replace(' ', '').replace('-', '')
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('7') or phone.startswith('1'):
            phone = '254' + phone
        if not phone.startswith('254') or len(phone) != 12:
            raise serializers.ValidationError('Invalid Kenyan phone number.')
        return phone