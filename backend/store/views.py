from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
import requests
import base64
import json
from datetime import datetime
from django.conf import settings
from decimal import Decimal

from .models import (
    Category, Brand, Product, ProductVariant, Review,
    Banner, Cart, CartItem, Order, OrderItem,
    RecentlyViewed, UserProfile, Wishlist, MpesaTransaction
)
from .serializers import (
    CategorySerializer, BrandSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductVariantSerializer, ReviewSerializer,
    BannerSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer,
    UserSerializer, RegisterSerializer,
    RecentlyViewedSerializer, WishlistSerializer,
    MpesaSTKPushSerializer
)


# ──────────────────────────────────────────────
# Category
# ──────────────────────────────────────────────
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True, parent=None).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=False, methods=['get'])
    def all_flat(self, request):
        """Return all categories including subcategories flat."""
        cats = Category.objects.filter(is_active=True)
        return Response(CategorySerializer(cats, many=True).data)


# ──────────────────────────────────────────────
# Brand
# ──────────────────────────────────────────────
class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    lookup_field = 'slug'

    @action(detail=False, methods=['get'])
    def featured(self, request):
        brands = self.queryset.filter(is_featured=True)
        return Response(BrandSerializer(brands, many=True).data)


# ──────────────────────────────────────────────
# Product
# ──────────────────────────────────────────────
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related(
        'images', 'variants', 'reviews'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand__slug', 'category__slug', 'is_featured', 'is_hot', 'is_new']
    search_fields = ['name', 'description', 'brand__name', 'tags']
    ordering_fields = ['created_at', 'min_price']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def retrieve(self, request, *args, **kwargs):
        """Override to track recently viewed."""
        instance = self.get_object()
        if request.user.is_authenticated:
            RecentlyViewed.objects.update_or_create(
                user=request.user, product=instance,
                defaults={'viewed_at': datetime.now()}
            )
        elif request.session.session_key:
            RecentlyViewed.objects.update_or_create(
                session_key=request.session.session_key, product=instance,
                defaults={'viewed_at': datetime.now()}
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """Products in same category, excluding current."""
        product = self.get_object()
        related = Product.objects.filter(
            is_active=True, category=product.category
        ).exclude(id=product.id)[:8]
        return Response(ProductListSerializer(related, many=True).data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        products = self.queryset.filter(is_featured=True)[:10]
        return Response(ProductListSerializer(products, many=True).data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        slug = request.query_params.get('slug')
        if not slug:
            return Response({'error': 'slug param required'}, status=400)
        try:
            cat = Category.objects.get(slug=slug)
            subcats = cat.subcategories.all()
            products = self.queryset.filter(
                Q(category=cat) | Q(category__in=subcats)
            )
            page = self.paginate_queryset(products)
            if page is not None:
                return self.get_paginated_response(ProductListSerializer(page, many=True).data)
            return Response(ProductListSerializer(products, many=True).data)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=404)

    @action(detail=False, methods=['get'])
    def by_brand(self, request):
        slug = request.query_params.get('slug')
        if not slug:
            return Response({'error': 'slug param required'}, status=400)
        products = self.queryset.filter(brand__slug=slug)
        page = self.paginate_queryset(products)
        if page is not None:
            return self.get_paginated_response(ProductListSerializer(page, many=True).data)
        return Response(ProductListSerializer(products, many=True).data)

    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        products = self.queryset.filter(is_hot=True)[:10]
        return Response(ProductListSerializer(products, many=True).data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        products = self.queryset.filter(is_new=True).order_by('-created_at')[:10]
        return Response(ProductListSerializer(products, many=True).data)

    @action(detail=True, methods=['post', 'get'], permission_classes=[IsAuthenticated])
    def reviews(self, request, slug=None):
        product = self.get_object()
        if request.method == 'GET':
            reviews = product.reviews.all()
            return Response(ReviewSerializer(reviews, many=True).data)
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# ──────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────
class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer

    @action(detail=False, methods=['get'])
    def hero(self, request):
        banners = self.queryset.filter(position='hero')
        return Response(BannerSerializer(banners, many=True).data)


# ──────────────────────────────────────────────
# Cart
# ──────────────────────────────────────────────
class CartViewSet(viewsets.ViewSet):
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        return Response(CartSerializer(cart).data)

    def create(self, request):
        """Add item to cart."""
        cart = self.get_cart(request)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cart=cart)
            return Response(CartSerializer(cart).data, status=201)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        """Remove item from cart."""
        cart = self.get_cart(request)
        try:
            item = CartItem.objects.get(id=pk, cart=cart)
            item.delete()
            return Response(CartSerializer(cart).data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)

    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        cart = self.get_cart(request)
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            if quantity <= 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()
            return Response(CartSerializer(cart).data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)


# ──────────────────────────────────────────────
# Order
# ──────────────────────────────────────────────
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Get cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart is empty'}, status=400)

        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        # Build order
        shipping_fee = Decimal('200.00')  # Flat rate
        subtotal = cart.total
        total = subtotal + shipping_fee

        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
            **serializer.validated_data
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                variant_name=cart_item.variant.name if cart_item.variant else '',
                price=cart_item.variant.effective_price if cart_item.variant else (cart_item.product.min_price or 0),
                quantity=cart_item.quantity
            )

        # Clear cart
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=201)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(OrderSerializer(instance).data)


# ──────────────────────────────────────────────
# M-Pesa STK Push
# ──────────────────────────────────────────────
class MpesaSTKPushView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_access_token(self):
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET

        if not consumer_key or not consumer_secret:
            raise ValueError(
                "MPESA_CONSUMER_KEY or MPESA_CONSUMER_SECRET is empty. "
                "Check your .env file and that load_dotenv() is called in settings.py."
            )

        auth = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

        try:
            r = requests.get(
                f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
                headers={"Authorization": f"Basic {auth}"},
                timeout=30,
            )
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"M-Pesa OAuth network error: {e}")

        if not r.text.strip():
            raise ValueError(
                f"Empty response from M-Pesa OAuth (HTTP {r.status_code}). "
                "Wrong credentials or base URL."
            )

        data = r.json()
        token = data.get('access_token')
        if not token:
            raise ValueError(f"No access_token in M-Pesa response: {data}")

        return token

    def post(self, request):
        serializer = MpesaSTKPushSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone = serializer.validated_data['phone']
        order_id = serializer.validated_data['order_id']

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        token = self._get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
        ).decode()

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(order.total),
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": order.order_number,
            "TransactionDesc": f"Payment for order {order.order_number}"
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        r = requests.post(
            f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
            json=payload, headers=headers
        )
        data = r.json()

        if data.get('ResponseCode') == '0':
            checkout_request_id = data['CheckoutRequestID']
            MpesaTransaction.objects.create(
                order=order,
                checkout_request_id=checkout_request_id,
                merchant_request_id=data.get('MerchantRequestID', ''),
                amount=order.total,
                phone=phone
            )
            order.mpesa_checkout_request_id = checkout_request_id
            order.mpesa_phone = phone
            order.save()
            return Response({'message': 'STK push sent. Check your phone.', 'checkout_request_id': checkout_request_id})
        return Response({'error': 'Failed to initiate payment', 'details': data}, status=400)


class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        stk = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk.get('CheckoutRequestID')
        result_code = str(stk.get('ResultCode', ''))
        result_desc = stk.get('ResultDesc', '')

        try:
            tx = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
            tx.result_code = result_code
            tx.result_desc = result_desc

            if result_code == '0':
                items = {i['Name']: i.get('Value', '') for i in stk.get('CallbackMetadata', {}).get('Item', [])}
                tx.mpesa_receipt = items.get('MpesaReceiptNumber', '')
                tx.status = 'success'
                tx.order.payment_status = 'paid'
                tx.order.status = 'confirmed'
                tx.order.mpesa_transaction_id = tx.mpesa_receipt
                tx.order.save()
            else:
                tx.status = 'failed'
            tx.save()
        except MpesaTransaction.DoesNotExist:
            pass

        return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})


# ──────────────────────────────────────────────
# Auth Views
# ──────────────────────────────────────────────
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '')
        password = request.data.get('password', '')

        # Allow login via email or username
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = email  # Fallback to username

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            })
        return Response({'error': 'Invalid credentials'}, status=401)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        # Update user fields
        for field in ['first_name', 'last_name', 'email']:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()

        # Update profile fields
        profile, _ = UserProfile.objects.get_or_create(user=user)
        for field in ['phone', 'address', 'city', 'county']:
            if field in request.data:
                setattr(profile, field, request.data[field])
        profile.save()

        return Response(UserSerializer(user).data)


# ──────────────────────────────────────────────
# Recently Viewed & Wishlist
# ──────────────────────────────────────────────
class RecentlyViewedView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            items = RecentlyViewed.objects.filter(user=request.user).select_related('product')[:10]
        elif request.session.session_key:
            items = RecentlyViewed.objects.filter(session_key=request.session.session_key).select_related('product')[:10]
        else:
            items = []
        return Response(RecentlyViewedSerializer(items, many=True).data)


class WishlistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        items = Wishlist.objects.filter(user=request.user).select_related('product')
        return Response(WishlistSerializer(items, many=True).data)

    def create(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
            return Response(WishlistSerializer(item).data, status=201 if created else 200)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

    def destroy(self, request, pk=None):
        try:
            Wishlist.objects.get(id=pk, user=request.user).delete()
            return Response(status=204)
        except Wishlist.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)