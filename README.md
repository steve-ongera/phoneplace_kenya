# PhonePlace Kenya — Full-Stack E-Commerce Platform

> A full-featured e-commerce store for phones, gaming devices, content creator kits, storage, accessories, audio, smartwatches, smart glasses, cameras, and drones.
> Built with **Django REST Framework** (backend) + **React 18** (frontend).

---

## Project Structure

```
phoneplace/
├── backend/                          # Django REST API
│   ├── phoneplace/                   # Core Django project package
│   │   ├── __init__.py
│   │   ├── settings.py               # All settings: DB, JWT, CORS, M-Pesa, Email, Logging
│   │   ├── urls.py                   # Root URL config → /api/v1/ + /admin/
│   │   └── wsgi.py
│   ├── store/                        # Main store app
│   │   ├── migrations/               # Auto-generated DB migrations
│   │   ├── __init__.py
│   │   ├── admin.py                  # Django Admin: inline editing, list filters
│   │   ├── models.py                 # All data models (16 models)
│   │   ├── serializers.py            # DRF serializers (list/detail variants)
│   │   ├── views.py                  # ViewSets + APIViews + M-Pesa handlers
│   │   └── urls.py                   # Router + custom endpoints
│   ├── requirements.txt              # Python dependencies
│   └── manage.py
│
└── frontend/                         # React 18 SPA
    ├── public/
    │   ├── index.html
    │   └── placeholder.png           # Fallback product image
    ├── src/
    │   ├── global.css                # All global styles, CSS variables, responsive breakpoints
    │   ├── App.jsx                   # Root: BrowserRouter, Layout wrapper, all Routes
    │   ├── context/
    │   │   └── AppContext.jsx        # Auth + Cart + Wishlist + Toast global state (useReducer)
    │   ├── utils/
    │   │   └── api.js                # Centralised fetch utility, JWT refresh, all API methods
    │   ├── components/
    │   │   ├── Navbar.jsx            # Fixed top nav: logo, category search, cart icon, account
    │   │   ├── CategoryNav.jsx       # Sticky scrollable category bar below navbar
    │   │   ├── Footer.jsx            # 4-col footer: brand, links, brands, contacts + social
    │   │   ├── HeroBanner.jsx        # Auto-advancing hero image slider with dot controls
    │   │   ├── ProductCard.jsx       # Reusable card: image, badges, wishlist, price, add-to-cart
    │   │   ├── CartDrawer.jsx        # Slide-in cart sidebar with qty controls + checkout CTA
    │   │   └── Toast.jsx             # Stacked bottom-right toast notification system
    │   └── pages/
    │       ├── Home.jsx              # Landing: hero, 4 promo cards, category grid, brand product sections
    │       ├── Products.jsx          # Product list: sidebar filters (category/brand), sort, pagination
    │       ├── ProductDetail.jsx     # Detail page: gallery, variant picker, specs/desc/reviews tabs,
    │       │                         #   related products, recently viewed
    │       ├── Checkout.jsx          # 3-step: cart review → delivery form → M-Pesa STK push / cash
    │       ├── Auth.jsx              # Login (email+password) + Register pages
    │       ├── Orders.jsx            # Orders list + Order detail with progress timeline
    │       ├── Profile.jsx           # User profile editor (name, email, phone, address)
    │       └── CategoryPage.jsx      # Category list, Category detail, Brand list, Brand detail
    └── package.json
```

---

## Data Models (`store/models.py`)

| Model | Key Fields | Purpose |
|---|---|---|
| `Category` | name, slug, icon, parent (FK self), is_active, order | Hierarchical categories with subcategories |
| `Brand` | name, slug, logo, is_featured, is_active | Product brands with logo |
| `Product` | name, slug, sku, brand, category, description, is_hot, is_new, is_featured, tags | Core product entity |
| `ProductVariant` | product, name, storage, color, ram, price, sale_price, stock | Size/color/storage variants with individual pricing |
| `ProductImage` | product, image, is_primary, order | Multiple images per product |
| `ProductSpecification` | product, key, value, order | Key-value spec table (e.g. RAM: 8GB) |
| `Review` | product, user, rating (1–5), title, comment, is_verified_purchase | Customer reviews |
| `Banner` | title, image, link, position (hero/promo/section), badge_text | Homepage hero and promo banners |
| `Cart` | user (nullable), session_key | Guest + authenticated cart |
| `CartItem` | cart, product, variant, quantity | Items inside a cart |
| `Order` | order_number, user, status, payment_status, payment_method, shipping_address, subtotal, total | Full order record |
| `OrderItem` | order, product, variant, product_name (snapshot), price, quantity | Line items (price snapshot at time of order) |
| `UserProfile` | user (1-1), phone, avatar, address, city, county | Extended user data |
| `MpesaTransaction` | order, checkout_request_id, amount, phone, status, mpesa_receipt | M-Pesa STK push transaction log |
| `RecentlyViewed` | user/session_key, product, viewed_at | Tracks product views per user/session |
| `Wishlist` | user, product | Saved/favourite products |

---

## API Endpoints (`/api/v1/`)

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register/` | Create account (returns JWT tokens) |
| POST | `/auth/login/` | Login with email + password (returns JWT tokens) |
| POST | `/auth/refresh/` | Refresh access token |
| GET/PATCH | `/auth/profile/` | Get or update current user profile |

### Products
| Method | Endpoint | Description |
|---|---|---|
| GET | `/products/` | Paginated product list (filter: brand__slug, category__slug, is_hot, is_new, is_featured; search: name, brand, tags; ordering: created_at, price) |
| GET | `/products/{slug}/` | Product detail (images, variants, specs, reviews) + tracks recently viewed |
| GET | `/products/{slug}/related/` | Related products in same category |
| GET | `/products/featured/` | Featured products |
| GET | `/products/best_sellers/` | HOT-flagged products |
| GET | `/products/new_arrivals/` | NEW-flagged products, sorted newest first |
| GET | `/products/by_category/?slug=` | Products filtered by category slug (includes subcategories) |
| GET | `/products/by_brand/?slug=` | Products filtered by brand slug |
| GET/POST | `/products/{slug}/reviews/` | Get or add reviews (POST requires auth) |

### Categories & Brands
| Method | Endpoint | Description |
|---|---|---|
| GET | `/categories/` | All root categories with subcategories |
| GET | `/categories/{slug}/` | Single category |
| GET | `/categories/all_flat/` | All categories flat (including subcategories) |
| GET | `/brands/` | All brands |
| GET | `/brands/{slug}/` | Single brand |
| GET | `/brands/featured/` | Featured brands only |

### Banners
| Method | Endpoint | Description |
|---|---|---|
| GET | `/banners/` | All active banners |
| GET | `/banners/hero/` | Hero-position banners only |

### Cart
| Method | Endpoint | Description |
|---|---|---|
| GET | `/cart/` | Get current cart (session or user) |
| POST | `/cart/` | Add item (`product_id`, `variant_id`, `quantity`) |
| DELETE | `/cart/{id}/` | Remove specific cart item |
| PATCH | `/cart/update_item/` | Update quantity (`item_id`, `quantity`) |
| DELETE | `/cart/clear/` | Clear entire cart |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| GET | `/orders/` | List current user's orders |
| POST | `/orders/` | Create order from current cart (requires auth) |
| GET | `/orders/{id}/` | Order detail |

### M-Pesa
| Method | Endpoint | Description |
|---|---|---|
| POST | `/mpesa/stk-push/` | Initiate M-Pesa STK push (`phone`, `order_id`) |
| POST | `/mpesa/callback/` | Safaricom callback — updates order payment status |

### Wishlist & Recently Viewed
| Method | Endpoint | Description |
|---|---|---|
| GET | `/wishlist/` | Get user's wishlist |
| POST | `/wishlist/` | Add product to wishlist (`product_id`) |
| DELETE | `/wishlist/{id}/` | Remove from wishlist |
| GET | `/recently-viewed/` | Get recently viewed products |

---

## Frontend Pages & Routes

| Route | Component | Description |
|---|---|---|
| `/` | `Home` | Hero banner, promo cards, category grid, Xiaomi/Oppo/iPhone/Infinix/Samsung deal sections |
| `/products` | `Products` | Full product listing with sidebar filters (category, brand), sort, pagination |
| `/products/:slug` | `ProductDetail` | Gallery, variant picker, qty, add-to-cart, specs tab, reviews tab, related & recently viewed |
| `/checkout` | `Checkout` | 3-step: cart review → delivery form → M-Pesa STK push or cash on delivery |
| `/login` | `Login` | Email + password login |
| `/register` | `Register` | New account creation |
| `/orders` | `Orders` | List of user's orders with status badges |
| `/orders/:id` | `OrderDetail` | Full order breakdown, progress timeline, payment info |
| `/profile` | `Profile` | Edit personal info, address, phone |
| `/categories` | `CategoryList` | All categories grid |
| `/categories/:slug` | `CategoryDetail` | Products in a specific category |
| `/brands` | `BrandList` | All brands grid with product count |
| `/brands/:slug` | `BrandDetail` | Products filtered by brand + brand info header |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

---

### Backend Setup

```bash
# 1. Navigate to backend
cd phoneplace/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE phoneplace_db;"

# 5. Configure environment variables — create a .env file
cat > .env << 'EOF'
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=phoneplace_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
FRONTEND_URL=http://localhost:3000
MPESA_CONSUMER_KEY=your-daraja-consumer-key
MPESA_CONSUMER_SECRET=your-daraja-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/v1/mpesa/callback/
EOF

# 6. Run migrations
python manage.py makemigrations store
python manage.py migrate

# 7. Create superuser for admin
python manage.py createsuperuser

# 8. Create media/static/logs directories
mkdir -p media staticfiles logs

# 9. Start development server
python manage.py runserver
```

Backend available at: `http://localhost:8000`
Admin panel at: `http://localhost:8000/admin/`

---

### Frontend Setup

```bash
# 1. Navigate to frontend
cd phoneplace/frontend

# 2. Install dependencies
npm install

# 3. Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env

# 4. Start development server
npm start
```

Frontend available at: `http://localhost:3000`

---

## M-Pesa Integration (Daraja API)

The platform uses **Lipa Na M-Pesa Online (STK Push)** for payments.

### How it works
1. Customer places order → order record created in `pending` state
2. Customer enters M-Pesa phone number on payment step
3. Frontend calls `POST /api/v1/mpesa/stk-push/` with `{ phone, order_id }`
4. Backend requests STK push from Safaricom Daraja API
5. Customer receives PIN prompt on their phone
6. Safaricom sends result to `POST /api/v1/mpesa/callback/`
7. Callback handler updates `MpesaTransaction` status and sets `Order.payment_status = 'paid'`

### Getting Daraja API credentials
1. Register at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create an app → get Consumer Key & Consumer Secret
3. For testing, use the **sandbox** shortcode `174379` and test credentials
4. For production, change `MPESA_BASE_URL` in `settings.py` to `https://api.safaricom.co.ke`
5. Your `MPESA_CALLBACK_URL` must be publicly accessible (use [ngrok](https://ngrok.com) for local testing)

### Testing M-Pesa locally with ngrok
```bash
# Expose local port 8000 to internet
ngrok http 8000

# Update your .env with the ngrok URL
MPESA_CALLBACK_URL=https://abc123.ngrok.io/api/v1/mpesa/callback/
```

---

## Product Categories

The store supports the following product categories (set up via Django Admin):

| Category | Icon | Subcategories |
|---|---|---|
| Smartphones | `bi-phone` | Samsung Phones, iPhone, Tecno, Google Pixel, Xiaomi, Infinix, Oppo, Nothing |
| Gaming | `bi-controller` | Gaming Consoles, Controllers, Accessories, Headsets |
| Audio | `bi-headphones` | Earbuds, Headphones, Speakers, Soundbars |
| Smartwatches | `bi-smartwatch` | Apple Watch, Galaxy Watch, Smart Bands |
| Accessories | `bi-bag` | Phone Covers, Chargers, Cables, Power Banks |
| Storage | `bi-device-hdd` | Flash Drives, Hard Drives, Memory Cards, USB Hubs |
| Tablets | `bi-tablet` | iPad, Android Tablets |
| Content Creator Kit | `bi-camera-video` | Gimbals, Ring Lights, Microphones, Tripods |
| Smart Glasses | `bi-eyeglasses` | Ray-Ban Meta, Smart AR glasses |
| Cameras | `bi-camera` | Action Cameras, DSLR Accessories |
| Drones | `bi-airplane` | Consumer Drones, Drone Accessories |

---

## Key Features

### Backend
- ✅ JWT authentication (access + refresh tokens)
- ✅ Login via email or username
- ✅ Guest cart (session-based) + authenticated cart (user-based)
- ✅ Cart auto-merges on login
- ✅ Order creation from cart with automatic cart clearing
- ✅ M-Pesa STK push + callback handler with transaction logging
- ✅ Product variants (storage, color, RAM) with per-variant pricing
- ✅ Product specifications key-value table
- ✅ Recently viewed tracking (per user or session)
- ✅ Wishlist per user
- ✅ Verified purchase badge on reviews
- ✅ Banner management for hero slides and promo sections
- ✅ Django Admin with inline editing for variants, images, specs
- ✅ Pagination on all list endpoints (20 items/page)
- ✅ Search across name, description, brand, tags
- ✅ Filtering by category, brand, is_hot, is_new, is_featured
- ✅ Ordering by date, price

### Frontend
- ✅ Responsive design — works on mobile, tablet, desktop
- ✅ Bootstrap Icons throughout (no external icon library install needed)
- ✅ CSS variables for consistent theming
- ✅ Auto-advancing hero banner slider
- ✅ Slide-in cart drawer with quantity controls
- ✅ Global toast notification system
- ✅ Skeleton loading states for product grids
- ✅ Product quick view hover effect
- ✅ Variant selector with out-of-stock handling
- ✅ 3-step checkout with M-Pesa STK push
- ✅ Order progress timeline
- ✅ Recently viewed products on detail page
- ✅ Related products section
- ✅ Wishlist (heart) on every product card
- ✅ JWT auto-refresh (transparent to user)
- ✅ Breadcrumb navigation on all inner pages
- ✅ Sticky category navbar
- ✅ Mobile search toggle

---

## Styling System

All styles live in `src/global.css` using CSS custom properties:

```css
--primary: #1a7a3e          /* PhonePlace green */
--accent: #f5a623           /* Gold accent */
--red: #e63946              /* Prices / sale badges */
--text-dark: #0f1923        /* Primary text */
--navbar-h: 70px            /* Navbar height (60px on mobile) */
```

**Fonts:** Syne (headings, prices) + DM Sans (body) — loaded from Google Fonts  
**Icons:** Bootstrap Icons 1.11 — loaded from jsDelivr CDN

### Responsive Breakpoints
| Breakpoint | Behaviour |
|---|---|
| `> 1024px` | Full 3-column footer, 5-col product grid |
| `768px–1024px` | 2-column footer, 4-col product grid, sidebar hidden |
| `< 768px` | Search bar collapses to toggle button, 2-col product grid |
| `< 480px` | Single-column footer, 2-col product grid (small cards) |

---

## Deployment (Production)

### Backend (e.g. Ubuntu VPS / Railway / Render)

```bash
# Collect static files
python manage.py collectstatic

# Set production environment variables
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=strong-random-secret
MPESA_BASE_URL=https://api.safaricom.co.ke   # Live M-Pesa

# Run with gunicorn
gunicorn phoneplace.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Frontend (e.g. Vercel / Netlify / S3)

```bash
# Set production API URL
echo "REACT_APP_API_URL=https://api.yourdomain.com/api/v1" > .env.production

# Build
npm run build

# Deploy the /build folder to your static host
```

### Nginx config snippet (serve Django + React)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # React SPA
    location / {
        root /var/www/phoneplace/build;
        try_files $uri /index.html;
    }

    # Django API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Django Admin & Media
    location /admin/ { proxy_pass http://127.0.0.1:8000; }
    location /media/ { alias /var/www/phoneplace/media/; }
    location /static/ { alias /var/www/phoneplace/staticfiles/; }
}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | Django 5.0 + Django REST Framework 3.15 |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL (via psycopg2) |
| Image handling | Pillow |
| CORS | `django-cors-headers` |
| Filtering | `django-filter` |
| Payment | Safaricom Daraja API (M-Pesa STK Push) |
| Frontend framework | React 18 + React Router DOM v6 |
| Styling | Pure CSS (no Tailwind, no MUI) + Bootstrap Icons |
| Fonts | Google Fonts (Syne + DM Sans) |
| State management | React Context + useReducer |
| HTTP client | Native Fetch API (no axios) |
| Production server | Gunicorn + Nginx |

---

## Contact & Store Info

**PhonePlace Kenya**  
Bazaar Plaza, Mezzanine 1 unit 5, Moi Avenue, Nairobi  
📧 info@phoneplacekenya.com | corporates@phoneplacekenya.com  
📞 Sales: 0726 526375 | Repairs: 0745 063030 | Corporate: 0708 465290  
🌐 [phoneplacekenya.com](https://phoneplacekenya.com)