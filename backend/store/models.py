from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Bootstrap icon class e.g. bi-phone")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    CONDITION_CHOICES = [('new', 'New'), ('refurbished', 'Refurbished'), ('used', 'Used')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_hot = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"PPK-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def min_price(self):
        variants = self.variants.filter(is_active=True)
        if variants.exists():
            prices = [v.sale_price or v.price for v in variants]
            return min(prices)
        return None

    @property
    def max_price(self):
        variants = self.variants.filter(is_active=True)
        if variants.exists():
            prices = [v.sale_price or v.price for v in variants]
            return max(prices)
        return None

    @property
    def main_image(self):
        img = self.images.filter(is_primary=True).first()
        if img:
            return img
        return self.images.first()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100, help_text="e.g. 128GB Black, 256GB Blue")
    storage = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price']

    @property
    def effective_price(self):
        return self.sale_price if self.sale_price else self.price

    @property
    def discount_percentage(self):
        if self.sale_price and self.price > 0:
            return round((1 - self.sale_price / self.price) * 100)
        return 0

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name}: {self.key}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} review on {self.product.name}"


class Banner(models.Model):
    POSITION_CHOICES = [('hero', 'Hero Slider'), ('promo', 'Promo Strip'), ('section', 'Section Banner')]
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')
    mobile_image = models.ImageField(upload_to='banners/', blank=True, null=True)
    link = models.CharField(max_length=500, blank=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='hero')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    badge_text = models.CharField(max_length=50, blank=True, help_text="e.g. NEW INSTOCK, FRESH DEAL")
    badge_color = models.CharField(max_length=20, default='green')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user or self.session_key}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']

    @property
    def subtotal(self):
        price = self.variant.effective_price if self.variant else (self.product.min_price or 0)
        return price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [('mpesa', 'M-Pesa'), ('card', 'Card'), ('cash', 'Cash on Delivery')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='mpesa')

    # Customer info
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Shipping
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    # M-Pesa
    mpesa_checkout_request_id = models.CharField(max_length=200, blank=True)
    mpesa_transaction_id = models.CharField(max_length=200, blank=True)
    mpesa_phone = models.CharField(max_length=20, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random, string
            self.order_number = 'PPK-' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='recently_viewed')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.product.name} viewed"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class MpesaTransaction(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='mpesa_transactions')
    checkout_request_id = models.CharField(max_length=200, unique=True)
    merchant_request_id = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_code = models.CharField(max_length=10, blank=True)
    result_desc = models.TextField(blank=True)
    mpesa_receipt = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"M-Pesa {self.checkout_request_id} - {self.status}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"