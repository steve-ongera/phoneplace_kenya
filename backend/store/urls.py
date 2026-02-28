from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BrandViewSet, ProductViewSet,
    BannerViewSet, CartViewSet, OrderViewSet,
    MpesaSTKPushView, MpesaCallbackView,
    RegisterView, LoginView, ProfileView,
    RecentlyViewedView, WishlistViewSet
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),

    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),

    # M-Pesa
    path('mpesa/stk-push/', MpesaSTKPushView.as_view(), name='mpesa_stk_push'),
    path('mpesa/callback/', MpesaCallbackView.as_view(), name='mpesa_callback'),

    # Recently Viewed
    path('recently-viewed/', RecentlyViewedView.as_view(), name='recently_viewed'),
]