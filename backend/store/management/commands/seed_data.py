"""
Django Management Command: seed_data
=====================================
Place this file at: yourapp/management/commands/seed_data.py

Usage:
    python manage.py seed_data
    python manage.py seed_data --images-dir "D:/gadaf/Documents/phone_place"
    python manage.py seed_data --clear

Images are mapped EXACTLY to the filenames discovered in phone_place.
"""

import os
import re
import shutil
from pathlib import Path
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.conf import settings


# ──────────────────────────────────────────────────────────────────
# Image helper — exact filename lookup (case-insensitive)
# ──────────────────────────────────────────────────────────────────

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def build_image_index(images_dir: str) -> dict:
    """Return {lowercase_filename: Path} for every image file in the dir."""
    base = Path(images_dir)
    index = {}
    if not base.exists():
        return index
    for f in base.iterdir():
        # index by full lowercase filename
        index[f.name.lower()] = f
    return index


def find_files(index: dict, *names) -> list:
    """Look up filenames case-insensitively and return matching Path objects."""
    seen = set()
    result = []
    for name in names:
        key = name.lower()
        if key in index and index[key] not in seen:
            seen.add(index[key])
            result.append(index[key])
    return result


# ──────────────────────────────────────────────────────────────────
# CATEGORIES
# ──────────────────────────────────────────────────────────────────

CATEGORIES = [
    {'name': 'Smartphones',   'icon': 'bi-phone',       'order': 1,
     'subcategories': ['Android Phones', 'iPhones', 'Budget Phones', 'Flagship Phones', 'Flip & Fold Phones']},
    {'name': 'Tablets',       'icon': 'bi-tablet',      'order': 2,
     'subcategories': ['Android Tablets', 'iPads']},
    {'name': 'Accessories',   'icon': 'bi-headphones',  'order': 3,
     'subcategories': ['Cases & Covers', 'Chargers & Cables', 'Screen Protectors',
                       'Earphones & Headphones', 'Power Banks', 'Microphones', 'Ring Lights']},
    {'name': 'Smartwatches',  'icon': 'bi-watch',       'order': 4, 'subcategories': []},
    {'name': 'Smart Glasses', 'icon': 'bi-eyeglasses',  'order': 5, 'subcategories': []},
    {'name': 'Gaming',        'icon': 'bi-controller',  'order': 6,
     'subcategories': ['Consoles', 'Gaming Accessories', 'Game Cards']},
    {'name': 'Laptops',       'icon': 'bi-laptop',      'order': 7, 'subcategories': []},
    {'name': 'Audio',         'icon': 'bi-speaker',     'order': 8,
     'subcategories': ['Speakers', 'Headphones']},
]

# ──────────────────────────────────────────────────────────────────
# BRANDS
# ──────────────────────────────────────────────────────────────────

BRANDS = [
    {'name': 'Samsung',    'is_featured': True,  'description': 'Leading global electronics and smartphone manufacturer.'},
    {'name': 'Apple',      'is_featured': True,  'description': 'Premium consumer electronics, software and services.'},
    {'name': 'Tecno',      'is_featured': True,  'description': 'Affordable smartphones designed for African markets.'},
    {'name': 'Infinix',    'is_featured': True,  'description': 'Trendy smartphones for the youth.'},
    {'name': 'Xiaomi',     'is_featured': True,  'description': 'Innovative technology at competitive prices.'},
    {'name': 'Redmi',      'is_featured': False, 'description': 'Value-focused sub-brand of Xiaomi.'},
    {'name': 'OPPO',       'is_featured': True,  'description': 'Premium camera smartphones.'},
    {'name': 'OnePlus',    'is_featured': False, 'description': 'Never Settle — flagship killers.'},
    {'name': 'Nothing',    'is_featured': False, 'description': 'Transparent design, pure experience.'},
    {'name': 'Google',     'is_featured': False, 'description': 'Pure Android experience with Tensor AI chips.'},
    {'name': 'Anker',      'is_featured': False, 'description': 'Leading charging and power accessories brand.'},
    {'name': 'JBL',        'is_featured': False, 'description': 'World-class audio products.'},
    {'name': 'Ray-Ban',    'is_featured': False, 'description': 'Iconic eyewear with Meta smart features.'},
    {'name': 'Xbox',       'is_featured': False, 'description': "Microsoft's gaming platform."},
    {'name': 'Sony',       'is_featured': False, 'description': 'PlayStation and premium electronics.'},
    {'name': 'Hollyland',  'is_featured': False, 'description': 'Professional wireless audio solutions.'},
    {'name': 'SkullCandy', 'is_featured': False, 'description': 'Bold audio for active lifestyles.'},
    {'name': 'Lenovo',     'is_featured': False, 'description': 'Innovative PCs and gaming devices.'},
    {'name': 'Green Lion', 'is_featured': False, 'description': 'Smart accessories and peripherals.'},
    {'name': 'Porodo',     'is_featured': False, 'description': 'Tech accessories for everyone.'},
    {'name': 'Meta',       'is_featured': False, 'description': 'Virtual and augmented reality devices.'},
]

# ──────────────────────────────────────────────────────────────────
# PRODUCTS
# 'images' lists exact filenames as they exist in phone_place folder.
# First filename = primary image.
# ──────────────────────────────────────────────────────────────────

PRODUCTS = [

    # ════════════════ SAMSUNG ════════════════
    {
        'name': 'Samsung Galaxy S25 Ultra',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Next-gen Galaxy AI with titanium build and 200MP camera.',
        'description': (
            'The Samsung Galaxy S25 Ultra raises the bar with a titanium frame, built-in S Pen, '
            'and 200MP quad-camera driven by Galaxy AI. Powered by Snapdragon 8 Elite with 12GB RAM.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'samsung,galaxy,s25,ultra,flagship,spen,200mp,5g',
        'variants': [
            {'name': '256GB Titanium Black',  'storage': '256GB', 'color': 'Titanium Black',  'ram': '12GB', 'price': 189999, 'sale_price': 179999, 'stock': 10},
            {'name': '512GB Titanium Grey',   'storage': '512GB', 'color': 'Titanium Grey',   'ram': '12GB', 'price': 219999, 'sale_price': None,   'stock': 6},
            {'name': '1TB Titanium Silver',   'storage': '1TB',   'color': 'Titanium Silver', 'ram': '12GB', 'price': 249999, 'sale_price': None,   'stock': 3},
        ],
        'specs': [
            ('Display', '6.9" Dynamic AMOLED 2X, 3088x1440, 120Hz'),
            ('Processor', 'Snapdragon 8 Elite'),
            ('RAM', '12GB'),
            ('Rear Camera', '200MP + 50MP + 10MP + 10MP'),
            ('Front Camera', '12MP'),
            ('Battery', '5000mAh, 45W'),
            ('S Pen', 'Built-in'),
            ('Water Resistance', 'IP68'),
            ('OS', 'Android 15, One UI 7'),
        ],
        'images': [
            'Samsung-Galaxy-S25-Ultra-a.jpg.jpeg',
            'Samsung-Galaxy-S25-Ultra-b.jpg.jpeg',
        ],
    },
    {
        'name': 'Samsung Galaxy S25 Plus 5G',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Large flagship display with Galaxy AI and Snapdragon 8 Elite.',
        'description': (
            'The Galaxy S25+ brings a 6.7" Dynamic AMOLED display, triple cameras, and '
            'Snapdragon 8 Elite in a sleeker form factor with Galaxy AI features.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'samsung,s25plus,flagship,5g,galaxy ai',
        'variants': [
            {'name': '256GB Icy Blue',    'storage': '256GB', 'color': 'Icy Blue',    'ram': '12GB', 'price': 149999, 'sale_price': 144999, 'stock': 12},
            {'name': '512GB Silver Shadow','storage': '512GB','color': 'Silver Shadow','ram': '12GB', 'price': 169999, 'sale_price': None,   'stock': 7},
        ],
        'specs': [
            ('Display', '6.7" Dynamic AMOLED 2X, 120Hz'),
            ('Processor', 'Snapdragon 8 Elite'),
            ('RAM', '12GB'),
            ('Rear Camera', '50MP + 10MP + 12MP'),
            ('Battery', '4900mAh, 45W'),
            ('Water Resistance', 'IP68'),
        ],
        'images': ['Samsung-Galaxy-S25-Plus-5G.jpg.jpeg'],
    },
    {
        'name': 'Samsung Galaxy S26 Ultra',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'The future of Samsung flagships — S26 Ultra.',
        'description': 'The upcoming Samsung Galaxy S26 Ultra is expected to push AI further with upgraded chip, improved S Pen, and enhanced cameras.',
        'condition': 'new', 'is_featured': True, 'is_hot': False, 'is_new': True,
        'tags': 'samsung,s26,ultra,upcoming,flagship',
        'variants': [
            {'name': '256GB Titanium Black', 'storage': '256GB', 'color': 'Titanium Black', 'ram': '12GB', 'price': 219999, 'sale_price': None, 'stock': 5},
        ],
        'specs': [('Note', 'Pre-order — specs subject to change')],
        'images': ['Samsung-Galaxy-S26-Ultra.webp'],
    },
    {
        'name': 'Samsung Galaxy S26 5G',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Next-gen Samsung standard flagship.',
        'description': 'The Samsung Galaxy S26 is the upcoming standard flagship in the next S-series lineup.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'samsung,s26,flagship,5g,upcoming',
        'variants': [
            {'name': '128GB Black', 'storage': '128GB', 'color': 'Black', 'ram': '8GB', 'price': 129999, 'sale_price': None, 'stock': 8},
        ],
        'specs': [('Note', 'Pre-order — specs subject to change')],
        'images': ['Samsung-Galaxy-S26-5G.webp'],
    },
    {
        'name': 'Samsung Galaxy S26 Plus',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Samsung Galaxy S26+ — upcoming mid-flagship.',
        'description': 'The Galaxy S26+ is the upcoming mid-flagship in Samsung\'s next S-series generation.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'samsung,s26plus,flagship,5g,upcoming',
        'variants': [
            {'name': '256GB Silver', 'storage': '256GB', 'color': 'Silver', 'ram': '12GB', 'price': 159999, 'sale_price': None, 'stock': 6},
        ],
        'specs': [('Note', 'Pre-order — specs subject to change')],
        'images': ['samsung-Galaxy-s26-plus.webp'],
    },
    {
        'name': 'Samsung Galaxy Z TriFold',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Flip & Fold Phones',
        'short_description': 'Samsung\'s revolutionary triple-fold display phone.',
        'description': 'The Samsung Galaxy Z TriFold introduces a groundbreaking three-panel foldable display — tablet-like screen real estate that fits in your pocket.',
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'samsung,trifold,foldable,z fold',
        'variants': [
            {'name': '512GB Black', 'storage': '512GB', 'color': 'Black', 'ram': '12GB', 'price': 299999, 'sale_price': None, 'stock': 4},
        ],
        'specs': [('Display', 'Triple-fold AMOLED'), ('Form Factor', 'Tri-fold')],
        'images': ['Samsung-Galaxy-Z-TriFold.webp'],
    },
    {
        'name': 'Samsung Galaxy A26 5G',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Affordable 5G with Super AMOLED and long battery life.',
        'description': 'Galaxy A26 5G brings 5G connectivity and Super AMOLED display to the mid-budget segment, with a 5000mAh battery.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'samsung,a26,5g,amoled,midrange',
        'variants': [
            {'name': '128GB Blue Black', 'storage': '128GB', 'color': 'Blue Black', 'ram': '6GB', 'price': 38999, 'sale_price': 34999, 'stock': 20},
            {'name': '256GB White',      'storage': '256GB', 'color': 'White',      'ram': '6GB', 'price': 44999, 'sale_price': None,  'stock': 15},
        ],
        'specs': [
            ('Display', '6.7" Super AMOLED, 120Hz'),
            ('Processor', 'Exynos 1380'),
            ('Rear Camera', '50MP + 8MP + 2MP'),
            ('Battery', '5000mAh, 25W'),
            ('5G', 'Yes'),
        ],
        'images': [
            'Samsung-Galaxy-A26-5G.jpg.jpeg',
            'Samsung-Galaxy-A26-5G-A.jpg.jpeg',
        ],
    },
    {
        'name': 'Samsung Galaxy A16 4G',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Entry-level Samsung with 50MP camera and 5000mAh battery.',
        'description': 'Galaxy A16 4G offers reliable Samsung quality at entry-level pricing with a 50MP camera and 6.7" display.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'samsung,a16,budget,entry level',
        'variants': [
            {'name': '128GB Black', 'storage': '128GB', 'color': 'Black', 'ram': '4GB', 'price': 22999, 'sale_price': 19999, 'stock': 30},
            {'name': '128GB Blue',  'storage': '128GB', 'color': 'Blue',  'ram': '4GB', 'price': 22999, 'sale_price': None,  'stock': 25},
        ],
        'specs': [
            ('Display', '6.7" PLS LCD, 90Hz'),
            ('Processor', 'Helio G85'),
            ('Rear Camera', '50MP + 5MP + 2MP'),
            ('Battery', '5000mAh, 25W'),
        ],
        'images': [
            'Samsung-Galaxy-A16-4G.jpg.jpeg',
            'Samsung-Galaxy-A16-4G-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Samsung Galaxy A06',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Stylish budget Samsung with large 6.7" display.',
        'description': 'Galaxy A06 is Samsung\'s most accessible smartphone, offering a large 6.7" display and essential features at a pocket-friendly price.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'samsung,a06,budget,affordable',
        'variants': [
            {'name': '64GB Black',  'storage': '64GB',  'color': 'Black',  'ram': '4GB', 'price': 14999, 'sale_price': 12999, 'stock': 40},
            {'name': '128GB Green', 'storage': '128GB', 'color': 'Green',  'ram': '4GB', 'price': 16999, 'sale_price': None,  'stock': 30},
        ],
        'specs': [
            ('Display', '6.7" PLS LCD'),
            ('Processor', 'Helio G85'),
            ('Rear Camera', '50MP + 2MP'),
            ('Battery', '5000mAh'),
        ],
        'images': [
            'Samsung-Galaxy-A06.jpg.jpeg',
            'Samsung-Galaxy-A06-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Samsung Galaxy M36 5G',
        'brand': 'Samsung', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Mid-range 5G powerhouse with 6000mAh battery.',
        'description': 'Galaxy M36 5G is built for heavy users with a massive 6000mAh battery, 5G connectivity and 50MP camera.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'samsung,m36,5g,battery,midrange',
        'variants': [
            {'name': '128GB Jade Black', 'storage': '128GB', 'color': 'Jade Black', 'ram': '6GB', 'price': 35999, 'sale_price': 32999, 'stock': 18},
            {'name': '256GB Mint Green', 'storage': '256GB', 'color': 'Mint Green', 'ram': '8GB', 'price': 41999, 'sale_price': None,  'stock': 12},
        ],
        'specs': [
            ('Display', '6.7" Super AMOLED, 120Hz'),
            ('Processor', 'Snapdragon 6 Gen 3'),
            ('Rear Camera', '50MP + 8MP + 2MP'),
            ('Battery', '6000mAh, 25W'),
            ('5G', 'Yes'),
        ],
        'images': [
            'Samsung-Galaxy-M36-5G.jpg.jpeg',
            'Samsung-Galaxy-M36-5G-a.jpg.jpeg',
        ],
    },

    # ════════════════ APPLE ════════════════
    {
        'name': 'Apple iPhone 16',
        'brand': 'Apple', 'category': 'Smartphones', 'subcategory': 'iPhones',
        'short_description': 'Camera Control, A18 chip, and Apple Intelligence.',
        'description': (
            'iPhone 16 introduces Camera Control — a dedicated button for photography. '
            'Powered by A18 with Apple Intelligence for smarter everyday experiences.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'apple,iphone16,camera control,apple intelligence,a18',
        'variants': [
            {'name': '128GB Black',      'storage': '128GB', 'color': 'Black',      'ram': '8GB', 'price': 129999, 'sale_price': 124999, 'stock': 15},
            {'name': '256GB Pink',       'storage': '256GB', 'color': 'Pink',       'ram': '8GB', 'price': 149999, 'sale_price': None,   'stock': 10},
            {'name': '512GB Ultramarine','storage': '512GB', 'color': 'Ultramarine','ram': '8GB', 'price': 179999, 'sale_price': None,   'stock': 5},
        ],
        'specs': [
            ('Display', '6.1" Super Retina XDR OLED, 60Hz'),
            ('Processor', 'A18'),
            ('Rear Camera', '48MP Fusion + 12MP Ultra Wide'),
            ('Front Camera', '12MP TrueDepth'),
            ('Camera Control', 'Yes'),
            ('Connector', 'USB-C'),
            ('Water Resistance', 'IP68'),
            ('OS', 'iOS 18'),
        ],
        'images': [
            'Apple-iPhone-16-1.jpg.jpeg',
            'Apple-iPhone-16-a.jpg.jpeg',
            'Apple-iPhone-16-1-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Apple iPhone 16 Plus',
        'brand': 'Apple', 'category': 'Smartphones', 'subcategory': 'iPhones',
        'short_description': 'Larger iPhone 16 with all-day battery and Camera Control.',
        'description': 'iPhone 16 Plus offers Camera Control and A18 chip with a larger 6.7" display and even longer battery life.',
        'condition': 'new', 'is_featured': True, 'is_hot': False, 'is_new': True,
        'tags': 'apple,iphone16plus,large screen,camera control',
        'variants': [
            {'name': '128GB Black',      'storage': '128GB', 'color': 'Black',      'ram': '8GB', 'price': 144999, 'sale_price': 139999, 'stock': 10},
            {'name': '256GB Ultramarine','storage': '256GB', 'color': 'Ultramarine','ram': '8GB', 'price': 164999, 'sale_price': None,   'stock': 7},
        ],
        'specs': [
            ('Display', '6.7" Super Retina XDR OLED, 60Hz'),
            ('Processor', 'A18'),
            ('Battery', 'Up to 27hr video'),
            ('Connector', 'USB-C'),
            ('Water Resistance', 'IP68'),
        ],
        'images': [
            'Apple-iPhone-16-Plus-c.jpg.jpeg',
            'Apple-iPhone-16-Plus-d.jpg.jpeg',
            'Apple-iPhone-16-Plus-c-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Apple iPhone 16 Pro',
        'brand': 'Apple', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'A18 Pro chip, ProRes 4K 120fps, titanium design.',
        'description': (
            'iPhone 16 Pro features A18 Pro with 6-core GPU, ProRes 4K 120fps video, '
            '48MP Ultra Wide, and a titanium frame that is lightweight yet strong.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'apple,iphone16pro,titanium,a18pro,prores',
        'variants': [
            {'name': '128GB Black Titanium',  'storage': '128GB', 'color': 'Black Titanium',  'ram': '8GB', 'price': 164999, 'sale_price': 159999, 'stock': 10},
            {'name': '256GB Desert Titanium', 'storage': '256GB', 'color': 'Desert Titanium', 'ram': '8GB', 'price': 184999, 'sale_price': None,   'stock': 7},
            {'name': '512GB White Titanium',  'storage': '512GB', 'color': 'White Titanium',  'ram': '8GB', 'price': 214999, 'sale_price': None,   'stock': 4},
        ],
        'specs': [
            ('Display', '6.3" Super Retina XDR ProMotion, 120Hz'),
            ('Processor', 'A18 Pro'),
            ('Rear Camera', '48MP + 48MP Ultra Wide + 12MP 5x Telephoto'),
            ('Battery', 'Up to 27hr video'),
            ('Frame', 'Grade-5 Titanium'),
            ('Water Resistance', 'IP68'),
        ],
        'images': [
            'Apple-iPhone-16-Pro-b.jpg.jpeg',
            'Apple-iPhone-16-Pro-c.jpg.jpeg',
            'Apple-iPhone-16-Pro-b-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Apple iPhone 16 Pro Max',
        'brand': 'Apple', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'The biggest, most powerful iPhone ever made.',
        'description': (
            'iPhone 16 Pro Max features a massive 6.9" ProMotion display, A18 Pro chip, '
            '5x optical zoom, and the longest battery life ever in an iPhone.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'apple,iphone16promax,flagship,a18pro,5x zoom',
        'variants': [
            {'name': '256GB Black Titanium',  'storage': '256GB', 'color': 'Black Titanium',  'ram': '8GB', 'price': 199999, 'sale_price': 194999, 'stock': 8},
            {'name': '512GB Desert Titanium', 'storage': '512GB', 'color': 'Desert Titanium', 'ram': '8GB', 'price': 229999, 'sale_price': None,   'stock': 5},
            {'name': '1TB Natural Titanium',  'storage': '1TB',   'color': 'Natural Titanium','ram': '8GB', 'price': 259999, 'sale_price': None,   'stock': 3},
        ],
        'specs': [
            ('Display', '6.9" Super Retina XDR ProMotion, 120Hz'),
            ('Processor', 'A18 Pro'),
            ('Rear Camera', '48MP + 48MP Ultra Wide + 12MP 5x Telephoto'),
            ('Battery', 'Up to 33hr video'),
            ('Frame', 'Grade-5 Titanium'),
            ('Water Resistance', 'IP68'),
        ],
        'images': [
            'iPhone-16-Pro-Max-1.jpg.jpeg',
            'iPhone-16-Pro-Max-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Apple iPhone 16e',
        'brand': 'Apple', 'category': 'Smartphones', 'subcategory': 'iPhones',
        'short_description': 'Apple Intelligence in an affordable, compact package.',
        'description': 'iPhone 16e brings Apple Intelligence and A16 Bionic at a more accessible price, making it the most affordable way into the Apple ecosystem.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'apple,iphone16e,affordable,apple intelligence',
        'variants': [
            {'name': '128GB Black', 'storage': '128GB', 'color': 'Black', 'ram': '8GB', 'price': 89999, 'sale_price': 84999, 'stock': 20},
            {'name': '256GB White', 'storage': '256GB', 'color': 'White', 'ram': '8GB', 'price': 109999, 'sale_price': None, 'stock': 15},
        ],
        'specs': [
            ('Display', '6.1" Super Retina XDR OLED'),
            ('Processor', 'A16 Bionic'),
            ('Rear Camera', '48MP Fusion'),
            ('Battery', 'Up to 26hr video'),
            ('Connector', 'USB-C'),
            ('Water Resistance', 'IP68'),
        ],
        'images': [
            'Apple-iPhone-16e.jpg.jpeg',
            'Apple-iPhone-16e-a.jpg.jpeg',
            'Apple-iPhone-16e-768x768.jpg.jpeg',
            'Apple-iPhone-16e-800x800.jpg.jpeg',
        ],
    },
    {
        'name': 'Apple iPhone 15',
        'brand': 'Apple', 'category': 'Smartphones', 'subcategory': 'iPhones',
        'short_description': 'Dynamic Island, 48MP camera, and USB-C.',
        'description': 'iPhone 15 brings the Dynamic Island to the standard lineup with a 48MP Main camera and USB-C. A16 Bionic ensures lasting performance.',
        'condition': 'new', 'is_featured': True, 'is_hot': False, 'is_new': False,
        'tags': 'apple,iphone15,dynamic island,usbc',
        'variants': [
            {'name': '128GB Black', 'storage': '128GB', 'color': 'Black', 'ram': '6GB', 'price': 109999, 'sale_price': 99999, 'stock': 12},
            {'name': '256GB Pink',  'storage': '256GB', 'color': 'Pink',  'ram': '6GB', 'price': 129999, 'sale_price': None,  'stock': 8},
        ],
        'specs': [
            ('Display', '6.1" Super Retina XDR OLED, 60Hz'),
            ('Processor', 'A16 Bionic'),
            ('Rear Camera', '48MP + 12MP'),
            ('Connector', 'USB-C'),
            ('Water Resistance', 'IP68'),
        ],
        'images': [
            'iPhone-15.jpg.jpeg',
            'iPhone-15-a.jpg.jpeg',
        ],
    },

    # ════════════════ INFINIX ════════════════
    {
        'name': 'Infinix GT 30',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Gaming smartphone with 144Hz AMOLED and shoulder triggers.',
        'description': (
            'Infinix GT 30 is built for mobile gamers. With a 144Hz AMOLED display, '
            'shoulder triggers, and Dimensity 8350, it dominates casual and competitive gaming.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'infinix,gt30,gaming,144hz,dimensity',
        'variants': [
            {'name': '256GB Cyber Black', 'storage': '256GB', 'color': 'Cyber Black', 'ram': '8GB',  'price': 35999, 'sale_price': 32999, 'stock': 20},
            {'name': '256GB Cyber White', 'storage': '256GB', 'color': 'Cyber White', 'ram': '12GB', 'price': 39999, 'sale_price': None,  'stock': 15},
        ],
        'specs': [
            ('Display', '6.78" AMOLED, 144Hz'),
            ('Processor', 'Dimensity 8350'),
            ('Rear Camera', '108MP + 2MP'),
            ('Battery', '5000mAh, 45W'),
            ('Gaming Triggers', 'Yes'),
        ],
        'images': [
            'Infinix-GT-30.png',
            'Infinix-GT-30-768x768.png',
            'Infinix-GT-30-Pro-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Infinix Note 50 Pro 4G',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Curved AMOLED with industry-leading 180W fast charging.',
        'description': (
            'Infinix Note 50 Pro 4G features a curved AMOLED display, 180W ultra-fast charging '
            'that fills 5000mAh in under 15 minutes, and a versatile 108MP camera system.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'infinix,note50pro,180w,curved amoled,fast charge',
        'variants': [
            {'name': '256GB Starshine Gold', 'storage': '256GB', 'color': 'Starshine Gold', 'ram': '8GB', 'price': 34999, 'sale_price': 31999, 'stock': 18},
            {'name': '256GB Obsidian Black', 'storage': '256GB', 'color': 'Obsidian Black', 'ram': '8GB', 'price': 34999, 'sale_price': None,  'stock': 14},
        ],
        'specs': [
            ('Display', '6.78" Curved AMOLED, 120Hz'),
            ('Processor', 'Helio G100 Ultra'),
            ('Rear Camera', '108MP + 50MP + 2MP'),
            ('Battery', '5000mAh, 180W'),
        ],
        'images': [
            'Infinix-Note-50-Pro-4G-1.jpg.jpeg',
            'Infinix-Note-50-Pro-4G-b.jpg.jpeg',
            'Infinix-Note-50-Pro-4G-1-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Infinix Note Edge',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Curved edge display with 144Hz AMOLED and Dimensity chipset.',
        'description': 'Infinix Note Edge sports a unique curved edge display, AMOLED with 144Hz, and powerful Dimensity chipset blending style with performance.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'infinix,note edge,curved,amoled,144hz',
        'variants': [
            {'name': '256GB Misty Grey', 'storage': '256GB', 'color': 'Misty Grey', 'ram': '8GB', 'price': 39999, 'sale_price': 37999, 'stock': 12},
        ],
        'specs': [
            ('Display', '6.78" Curved AMOLED, 144Hz'),
            ('Processor', 'Dimensity 8350'),
            ('Battery', '5000mAh, 45W'),
        ],
        'images': [
            'Infinix-Note-Edge-a.webp',
            'Infinix-Note-Edge-b.webp',
            'Infinix-Note-Edge-a-768x768.webp',
        ],
    },
    {
        'name': 'Infinix Hot 60 Pro 4G',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': '108MP camera and 5000mAh battery on a budget.',
        'description': 'Infinix Hot 60 Pro 4G delivers a large display, capable 108MP camera, and long-lasting battery without breaking the bank.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'infinix,hot60pro,budget,108mp',
        'variants': [
            {'name': '128GB Dusk Black',  'storage': '128GB', 'color': 'Dusk Black',  'ram': '8GB', 'price': 22999, 'sale_price': 20999, 'stock': 25},
            {'name': '128GB Sakura Gold', 'storage': '128GB', 'color': 'Sakura Gold', 'ram': '8GB', 'price': 22999, 'sale_price': None,  'stock': 20},
        ],
        'specs': [
            ('Display', '6.78" IPS LCD, 120Hz'),
            ('Rear Camera', '108MP + 2MP'),
            ('Battery', '5000mAh, 33W'),
        ],
        'images': [
            'Infinix-Hot-60-Pro-4G.webp',
            'Infinix-Hot-60-Pro-4G-b.webp',
            'Infinix-Hot-60-Pro-4G-768x768.webp',
        ],
    },
    {
        'name': 'Infinix Hot 60 Pro Plus',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Hot 60 Pro+ with more RAM, storage and bigger battery.',
        'description': 'Infinix Hot 60 Pro Plus steps up with more RAM, storage, and a bigger battery than the standard Pro.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'infinix,hot60,plus,budget',
        'variants': [
            {'name': '256GB Dusk Black', 'storage': '256GB', 'color': 'Dusk Black', 'ram': '12GB', 'price': 25999, 'sale_price': None, 'stock': 18},
        ],
        'specs': [
            ('Display', '6.78" IPS LCD, 120Hz'),
            ('Battery', '5000mAh, 45W'),
        ],
        'images': [
            'Infinix-Hot-60-Pro-Plus-a-768x768.jpg.jpeg',
            'Infinix-Hot-60-Pro-Plus-d.jpg.jpeg',
        ],
    },
    {
        'name': 'Infinix Hot 60i',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Ultra-affordable daily driver with big battery.',
        'description': 'Infinix Hot 60i delivers essential smartphone features at the lowest possible price.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'infinix,hot60i,budget,entry level',
        'variants': [
            {'name': '64GB Starlight Black', 'storage': '64GB', 'color': 'Starlight Black', 'ram': '4GB', 'price': 14999, 'sale_price': 12999, 'stock': 35},
        ],
        'specs': [('Display', '6.7" IPS LCD'), ('Battery', '5000mAh')],
        'images': [
            'Infinix-Hot-60i.jpg.jpeg',
            'Infinix-Hot-60i-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Infinix Zero Flip 5G',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Flip & Fold Phones',
        'short_description': 'Affordable clamshell flip phone with 5G and AMOLED display.',
        'description': (
            'Infinix Zero Flip 5G brings the stylish clamshell flip form factor at a fraction of '
            'flagship foldable prices. 6.9" inner AMOLED display and 3.64" cover screen.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'infinix,zero flip,5g,foldable,clamshell',
        'variants': [
            {'name': '256GB Blossom Glow', 'storage': '256GB', 'color': 'Blossom Glow', 'ram': '8GB', 'price': 64999, 'sale_price': 59999, 'stock': 10},
            {'name': '256GB Rock Black',   'storage': '256GB', 'color': 'Rock Black',   'ram': '8GB', 'price': 64999, 'sale_price': None,  'stock': 8},
        ],
        'specs': [
            ('Display', '6.9" AMOLED inner + 3.64" cover screen'),
            ('Processor', 'Dimensity 8020'),
            ('Battery', '4720mAh, 45W'),
            ('5G', 'Yes'),
        ],
        'images': [
            'Infinix-Zero-Flip-5G-2.jpg.jpeg',
            'Infinix-Zero-Flip-5G-a-1.jpg.jpeg',
            'Infinix-Zero-Flip-5G-2-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Infinix Smart 10',
        'brand': 'Infinix', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Entry-level Smart series with long battery life.',
        'description': 'Infinix Smart 10 is designed for first-time smartphone users and those seeking a reliable secondary device at an unbeatable price.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'infinix,smart10,entry level,budget',
        'variants': [
            {'name': '64GB Timber Black', 'storage': '64GB', 'color': 'Timber Black', 'ram': '4GB', 'price': 11999, 'sale_price': 9999, 'stock': 40},
        ],
        'specs': [('Display', '6.6" IPS LCD'), ('Battery', '5000mAh'), ('Rear Camera', '13MP')],
        'images': [
            'Infinix-Smart-10-a.jpg.jpeg',
            'Infinix-Smart-10-c.jpg.jpeg',
        ],
    },

    # ════════════════ OPPO ════════════════
    {
        'name': 'OPPO Reno 15 Pro 5G',
        'brand': 'OPPO', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Premium curved AMOLED with Hasselblad-inspired cameras.',
        'description': 'OPPO Reno 15 Pro features Hasselblad-inspired cameras, 6.7" curved AMOLED 120Hz, and 80W SUPERVOOC charging.',
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'oppo,reno15pro,hasselblad,5g,curved amoled',
        'variants': [
            {'name': '256GB Luminous Grey', 'storage': '256GB', 'color': 'Luminous Grey', 'ram': '12GB', 'price': 79999, 'sale_price': 74999, 'stock': 10},
            {'name': '512GB Graphite Grey', 'storage': '512GB', 'color': 'Graphite Grey', 'ram': '12GB', 'price': 94999, 'sale_price': None,  'stock': 6},
        ],
        'specs': [
            ('Display', '6.7" Curved AMOLED, 120Hz'),
            ('Processor', 'Dimensity 8350'),
            ('Rear Camera', '50MP + 50MP + 8MP'),
            ('Battery', '5800mAh, 80W'),
            ('5G', 'Yes'),
        ],
        'images': [
            'Oppo-Reno15-Pro-3.webp',
            'Oppo-Reno15-Pro-a.webp',
            'Oppo-Reno15-Pro-3-768x768.webp',
        ],
    },
    {
        'name': 'OPPO Reno 15 5G',
        'brand': 'OPPO', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Sleek 5G with 50MP AI Portrait camera and SUPERVOOC.',
        'description': 'OPPO Reno 15 5G features a slim AMOLED display, 50MP AI Portrait camera and 67W SUPERVOOC fast charging.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'oppo,reno15,5g,portrait,amoled',
        'variants': [
            {'name': '256GB Misty Lavender', 'storage': '256GB', 'color': 'Misty Lavender', 'ram': '8GB', 'price': 59999, 'sale_price': 55999, 'stock': 14},
            {'name': '256GB Graphite Grey',  'storage': '256GB', 'color': 'Graphite Grey',  'ram': '8GB', 'price': 59999, 'sale_price': None,  'stock': 10},
        ],
        'specs': [
            ('Display', '6.7" AMOLED, 120Hz'),
            ('Rear Camera', '50MP + 8MP + 2MP'),
            ('Battery', '5000mAh, 67W'),
            ('5G', 'Yes'),
        ],
        'images': [
            'Oppo-Reno15-5G.webp',
            'Oppo-Reno15-5G-a.webp',
            'Oppo-Reno15-5G-768x768.webp',
        ],
    },
    {
        'name': 'OPPO Reno 15F 5G',
        'brand': 'OPPO', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Feature-packed mid-range 5G with 64MP camera.',
        'description': 'OPPO Reno15 F 5G balances performance and affordability with a 64MP main camera and 5G connectivity.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'oppo,reno15f,5g,midrange,64mp',
        'variants': [
            {'name': '128GB Sparkle Black', 'storage': '128GB', 'color': 'Sparkle Black', 'ram': '8GB', 'price': 44999, 'sale_price': 41999, 'stock': 16},
        ],
        'specs': [
            ('Display', '6.7" AMOLED, 120Hz'),
            ('Rear Camera', '64MP + 8MP + 2MP'),
            ('Battery', '5000mAh, 45W'),
        ],
        'images': [
            'Oppo-Reno15-F-5G-1.webp',
            'Oppo-Reno15-F-5G.webp',
            'Oppo-Reno15-F-5G-1-768x768.webp',
        ],
    },
    {
        'name': 'OPPO Reno 14F 5G',
        'brand': 'OPPO', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Stylish mid-range 5G with 50MP camera and 45W charging.',
        'description': 'OPPO Reno14 F 5G is a stylish mid-range smartphone with capable cameras and reliable 5G performance.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'oppo,reno14f,5g,midrange',
        'variants': [
            {'name': '128GB Dazzling Blue', 'storage': '128GB', 'color': 'Dazzling Blue', 'ram': '8GB', 'price': 39999, 'sale_price': 36999, 'stock': 18},
        ],
        'specs': [
            ('Display', '6.7" AMOLED, 120Hz'),
            ('Rear Camera', '50MP + 8MP + 2MP'),
            ('Battery', '5000mAh, 45W'),
        ],
        'images': [
            'Oppo-Reno14-F-5G-1.jpg.jpeg',
            'Oppo-Reno14-F-5G-a.jpg.jpeg',
            'Oppo-Reno14-F-5G-1-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'OPPO A6 Pro 5G',
        'brand': 'OPPO', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Affordable 5G with 108MP camera.',
        'description': 'OPPO A6 Pro 5G brings 5G connectivity and a 108MP camera to the budget segment.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'oppo,a6pro,5g,budget,108mp',
        'variants': [
            {'name': '128GB Midnight Black', 'storage': '128GB', 'color': 'Midnight Black', 'ram': '6GB', 'price': 29999, 'sale_price': 27999, 'stock': 20},
        ],
        'specs': [
            ('Display', '6.67" IPS LCD, 90Hz'),
            ('Rear Camera', '108MP + 2MP'),
            ('Battery', '5000mAh, 33W'),
            ('5G', 'Yes'),
        ],
        'images': [
            'Oppo-A6-Pro-5G.jpg.jpeg',
            'Oppo-A6-Pro-5G-a.jpg.jpeg',
            'Oppo-A6-Pro-5G-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'OPPO A6x 4G',
        'brand': 'OPPO', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Budget OPPO with large display and good battery.',
        'description': 'OPPO A6x 4G is a reliable budget smartphone with essential features for everyday use.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'oppo,a6x,budget,4g',
        'variants': [
            {'name': '128GB Black', 'storage': '128GB', 'color': 'Black', 'ram': '6GB', 'price': 24999, 'sale_price': 22999, 'stock': 22},
        ],
        'specs': [('Display', '6.67" IPS LCD'), ('Battery', '5000mAh')],
        'images': [
            'Oppo-A6x-4G.webp',
            'Oppo-A6x-4G-a.webp',
        ],
    },

    # ════════════════ XIAOMI / REDMI ════════════════
    {
        'name': 'Xiaomi 15T Pro',
        'brand': 'Xiaomi', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Leica cameras, Snapdragon 8 Gen 3, 144Hz, 120W charging.',
        'description': (
            'Xiaomi 15T Pro pairs Leica-tuned lenses with Snapdragon 8 Gen 3, a 144Hz AMOLED display, '
            '120W HyperCharge, and IP68 rating — a true flagship at mid-flagship price.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'xiaomi,15t pro,leica,snapdragon,144hz,120w',
        'variants': [
            {'name': '256GB Black', 'storage': '256GB', 'color': 'Black', 'ram': '12GB', 'price': 109999, 'sale_price': 99999, 'stock': 10},
            {'name': '512GB White', 'storage': '512GB', 'color': 'White', 'ram': '12GB', 'price': 129999, 'sale_price': None,  'stock': 6},
        ],
        'specs': [
            ('Display', '6.67" LTPO AMOLED, 2712x1220, 144Hz'),
            ('Processor', 'Snapdragon 8 Gen 3'),
            ('Rear Camera', '50MP Leica + 50MP + 50MP'),
            ('Battery', '5000mAh, 120W'),
            ('Water Resistance', 'IP68'),
        ],
        'images': [
            'Xiaomi-15T-Pro.jpg.jpeg',
            'Xiaomi-15T-Pro-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Xiaomi POCO F7',
        'brand': 'Xiaomi', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Snapdragon 8s Gen 4 performance at mid-range price.',
        'description': 'POCO F7 is built for performance-hungry users — Snapdragon 8s Gen 4, 120Hz AMOLED, and 90W charging at an aggressive price.',
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'xiaomi,poco,f7,snapdragon,gaming,value flagship',
        'variants': [
            {'name': '256GB Black', 'storage': '256GB', 'color': 'Black', 'ram': '8GB',  'price': 59999, 'sale_price': 54999, 'stock': 15},
            {'name': '512GB White', 'storage': '512GB', 'color': 'White', 'ram': '12GB', 'price': 74999, 'sale_price': None,  'stock': 8},
        ],
        'specs': [
            ('Display', '6.67" AMOLED, 120Hz'),
            ('Processor', 'Snapdragon 8s Gen 4'),
            ('Rear Camera', '50MP + 8MP'),
            ('Battery', '5110mAh, 90W'),
        ],
        'images': [
            'Xiaomi-POCO-F7.jpg.jpeg',
            'Xiaomi-POCO-F7-a.jpg.jpeg',
            'Xiaomi-POCO-F7-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Xiaomi POCO F7 Ultra',
        'brand': 'Xiaomi', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Ultimate POCO with Snapdragon 8 Elite and Leica camera.',
        'description': 'POCO F7 Ultra brings Snapdragon 8 Elite, Leica-tuned cameras and 120W charging to the POCO lineup.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'xiaomi,poco f7 ultra,leica,snapdragon 8 elite,flagship',
        'variants': [
            {'name': '512GB Black', 'storage': '512GB', 'color': 'Black', 'ram': '12GB', 'price': 89999, 'sale_price': 84999, 'stock': 8},
        ],
        'specs': [
            ('Processor', 'Snapdragon 8 Elite'),
            ('Rear Camera', '50MP Leica + 50MP'),
            ('Battery', '5300mAh, 120W'),
        ],
        'images': [
            'Xiaomi-Poco-F7-Ultra-a.jpg.jpeg',
            'Xiaomi-Poco-F7-Ultra-a-768x768.jpg.jpeg',
        ],
    },
    {
        'name': 'Redmi Note 15 Pro 4G',
        'brand': 'Redmi', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': '200MP OIS camera with AMOLED display and 45W fast charging.',
        'description': 'Redmi Note 15 Pro 4G introduces a 200MP OIS camera, vivid AMOLED display, and 45W charging to the mid-range.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'redmi,note15pro,200mp,amoled,ois',
        'variants': [
            {'name': '256GB Phantom Black', 'storage': '256GB', 'color': 'Phantom Black', 'ram': '8GB', 'price': 39999, 'sale_price': 36999, 'stock': 18},
            {'name': '256GB Midnight Blue', 'storage': '256GB', 'color': 'Midnight Blue', 'ram': '8GB', 'price': 39999, 'sale_price': None,  'stock': 14},
        ],
        'specs': [
            ('Display', '6.67" AMOLED, 120Hz'),
            ('Rear Camera', '200MP OIS + 8MP + 2MP'),
            ('Battery', '5030mAh, 45W'),
        ],
        'images': [
            'Redmi-Note-15-Pro-4G.webp',
            'Redmi-Note-15-Pro-4G-a.webp',
            'Redmi-Note-15-Pro-4G-768x768.webp',
        ],
    },
    {
        'name': 'Redmi 15 4G',
        'brand': 'Redmi', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Reliable Redmi with 50MP camera and 5030mAh battery.',
        'description': 'Redmi 15 4G continues delivering great value with a large display, capable camera and solid battery life.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'redmi,15,budget,50mp,4g',
        'variants': [
            {'name': '128GB Midnight Black', 'storage': '128GB', 'color': 'Midnight Black', 'ram': '6GB', 'price': 19999, 'sale_price': 17999, 'stock': 30},
            {'name': '128GB Ocean Blue',     'storage': '128GB', 'color': 'Ocean Blue',     'ram': '6GB', 'price': 19999, 'sale_price': None,  'stock': 25},
        ],
        'specs': [
            ('Display', '6.79" IPS LCD, 90Hz'),
            ('Rear Camera', '50MP + 2MP'),
            ('Battery', '5030mAh, 18W'),
        ],
        'images': [
            'Redmi-15-4G.webp',
            'Redmi-15-4G-a-1.webp',
            'Redmi-15-4G-768x768.webp',
        ],
    },
    {
        'name': 'Redmi 15C 4G',
        'brand': 'Redmi', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Entry-level Redmi with solid display and battery.',
        'description': 'Redmi 15C 4G is the ideal first smartphone for budget-conscious users who want Xiaomi quality at an entry-level price.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'redmi,15c,budget,entry level',
        'variants': [
            {'name': '128GB Midnight Black', 'storage': '128GB', 'color': 'Midnight Black', 'ram': '4GB', 'price': 15999, 'sale_price': 13999, 'stock': 35},
        ],
        'specs': [('Display', '6.88" IPS LCD'), ('Battery', '5160mAh')],
        'images': [
            'Redmi-15C-4G.jpg.jpeg',
            'Redmi-15C-4G-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Redmi Note 15 4G',
        'brand': 'Redmi', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Note 15 with AMOLED display and 50MP triple cameras.',
        'description': 'Redmi Note 15 4G offers a beautiful AMOLED display and triple camera system at a competitive mid-range price.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'redmi,note15,amoled,50mp,4g',
        'variants': [
            {'name': '128GB Midnight Black', 'storage': '128GB', 'color': 'Midnight Black', 'ram': '6GB', 'price': 25999, 'sale_price': 23999, 'stock': 22},
        ],
        'specs': [
            ('Display', '6.67" AMOLED, 120Hz'),
            ('Rear Camera', '50MP + 8MP + 2MP'),
            ('Battery', '5030mAh, 33W'),
        ],
        'images': [
            'Redmi-Note-15-4G.webp',
            'Redmi-Note-15-4G-c-2.webp',
        ],
    },

    # ════════════════ NOTHING ════════════════
    {
        'name': 'Nothing Phone 3',
        'brand': 'Nothing', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Iconic Glyph Interface in the most powerful Nothing yet.',
        'description': 'Nothing Phone 3 pushes the Glyph Interface further with interactive zones, flagship Snapdragon chipset, and refined transparent design.',
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'nothing,phone3,glyph,transparent,flagship',
        'variants': [
            {'name': '256GB Black', 'storage': '256GB', 'color': 'Black', 'ram': '12GB', 'price': 99999, 'sale_price': 94999, 'stock': 8},
            {'name': '512GB White', 'storage': '512GB', 'color': 'White', 'ram': '12GB', 'price': 119999, 'sale_price': None, 'stock': 5},
        ],
        'specs': [
            ('Display', '6.67" LTPO AMOLED, 120Hz'),
            ('Processor', 'Snapdragon 8 Gen 4'),
            ('Glyph Interface', 'Advanced interactive Glyph zones'),
            ('Battery', '5150mAh, 65W'),
        ],
        'images': [
            'Nothing-Phone-3.jpg.jpeg',
            'Nothing-Phone-3_1.jpg.jpeg',
        ],
    },
    {
        'name': 'Nothing Phone 3a Pro',
        'brand': 'Nothing', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Mid-range Nothing with Essential Camera and Glyph.',
        'description': 'Nothing Phone 3a Pro brings the Glyph Interface, Essential Camera, and clean Nothing OS in a competitive mid-range package.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'nothing,phone 3a pro,glyph,essential camera',
        'variants': [
            {'name': '256GB Black', 'storage': '256GB', 'color': 'Black', 'ram': '8GB', 'price': 59999, 'sale_price': 55999, 'stock': 12},
            {'name': '256GB White', 'storage': '256GB', 'color': 'White', 'ram': '8GB', 'price': 59999, 'sale_price': None,  'stock': 10},
        ],
        'specs': [
            ('Display', '6.77" AMOLED, 120Hz'),
            ('Processor', 'Snapdragon 7s Gen 3'),
            ('Rear Camera', '50MP + 50MP + 8MP'),
            ('Battery', '5000mAh, 50W'),
        ],
        'images': [
            'Nothing-Phone-3a-Pro-a.jpg.jpeg',
            'Nothing-Phone-3a-Pro-Black.jpg.jpeg',
        ],
    },
    {
        'name': 'Nothing Phone 3a',
        'brand': 'Nothing', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Standard Nothing 3a with Glyph and clean Android.',
        'description': 'Nothing Phone 3a brings the iconic Glyph Interface and clean Nothing OS to an accessible mid-range price point.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'nothing,phone 3a,glyph,mid-range',
        'variants': [
            {'name': '128GB Black', 'storage': '128GB', 'color': 'Black', 'ram': '8GB', 'price': 44999, 'sale_price': 41999, 'stock': 15},
        ],
        'specs': [
            ('Display', '6.77" AMOLED, 120Hz'),
            ('Processor', 'Snapdragon 7s Gen 3'),
            ('Battery', '5000mAh, 50W'),
        ],
        'images': [
            'Nothing-Phone-3a-a.jpg.jpeg',
            'Nothing-Phone-3a-b.jpg.jpeg',
        ],
    },

    # ════════════════ GOOGLE ════════════════
    {
        'name': 'Google Pixel 9 Pro XL 5G',
        'brand': 'Google', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Google AI at its best — Tensor G4, 5x zoom, Video Boost.',
        'description': (
            'Google Pixel 9 Pro XL features Tensor G4 optimised for AI, a 6.8" LTPO display, '
            'and the most advanced Google Camera with Video Boost and 5x optical zoom.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'google,pixel9,tensor,ai,camera,5g',
        'variants': [
            {'name': '256GB Obsidian', 'storage': '256GB', 'color': 'Obsidian', 'ram': '16GB', 'price': 149999, 'sale_price': 144999, 'stock': 8},
            {'name': '512GB Porcelain','storage': '512GB', 'color': 'Porcelain','ram': '16GB', 'price': 174999, 'sale_price': None,   'stock': 5},
        ],
        'specs': [
            ('Display', '6.8" LTPO OLED, 120Hz'),
            ('Processor', 'Tensor G4'),
            ('RAM', '16GB'),
            ('Rear Camera', '50MP + 48MP + 48MP 5x Telephoto'),
            ('Battery', '5060mAh, 30W'),
            ('Water Resistance', 'IP68'),
        ],
        'images': [
            'Google-Pixel-9-Pro-XL-5G-1.jpg.jpeg',
            'Google-Pixel-9-Pro-XL-5G-a-1.jpg.jpeg',
            'Google-Pixel-9-Pro-XL-5G-1-800x800.jpg.jpeg',
        ],
    },

    # ════════════════ ONEPLUS ════════════════
    {
        'name': 'OnePlus 13 5G',
        'brand': 'OnePlus', 'category': 'Smartphones', 'subcategory': 'Flagship Phones',
        'short_description': 'Hasselblad cameras, 100W SUPERVOOC, IP69 water resistance.',
        'description': (
            'OnePlus 13 5G brings the best Hasselblad-tuned camera system yet, Snapdragon 8 Elite, '
            '100W SUPERVOOC charging, and a stunning 2K AMOLED display.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'oneplus,13,hasselblad,100w,snapdragon,5g',
        'variants': [
            {'name': '256GB Midnight Ocean', 'storage': '256GB', 'color': 'Midnight Ocean', 'ram': '12GB', 'price': 109999, 'sale_price': 99999, 'stock': 10},
            {'name': '512GB Arctic Dawn',    'storage': '512GB', 'color': 'Arctic Dawn',    'ram': '16GB', 'price': 129999, 'sale_price': None,  'stock': 6},
        ],
        'specs': [
            ('Display', '6.82" LTPO AMOLED, 2K, 120Hz'),
            ('Processor', 'Snapdragon 8 Elite'),
            ('Rear Camera', '50MP Hasselblad + 50MP + 50MP'),
            ('Battery', '6000mAh, 100W'),
            ('Water Resistance', 'IP69'),
        ],
        'images': [
            'OnePlus-13-5G-a.jpg.jpeg',
            'OnePlus-13-5G-b.jpg.jpeg',
            'OnePlus-13-5G-a-800x800.jpg.jpeg',
        ],
    },

    # ════════════════ TECNO ════════════════
    {
        'name': 'Tecno Camon 50 Ultra',
        'brand': 'Tecno', 'category': 'Smartphones', 'subcategory': 'Android Phones',
        'short_description': 'Tecno\'s most premium Camon with ultra-clear cameras.',
        'description': 'Tecno Camon 50 Ultra delivers professional-level photography with its advanced camera system and AMOLED display.',
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'tecno,camon50,ultra,camera,amoled',
        'variants': [
            {'name': '256GB Orbit Black', 'storage': '256GB', 'color': 'Orbit Black', 'ram': '8GB', 'price': 39999, 'sale_price': 36999, 'stock': 15},
        ],
        'specs': [
            ('Display', '6.78" AMOLED, 144Hz'),
            ('Rear Camera', '108MP + 50MP + 2MP'),
            ('Battery', '5000mAh, 45W'),
        ],
        'images': ['Tecno-Camon-50-Ultra.webp'],
    },
    {
        'name': 'Tecno Spark 40 4G',
        'brand': 'Tecno', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Budget champion with big display and dual cameras.',
        'description': 'Tecno Spark 40 4G is the ideal affordable smartphone for everyday use with a large display and reliable performance.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'tecno,spark40,budget,4g',
        'variants': [
            {'name': '128GB Magic Black', 'storage': '128GB', 'color': 'Magic Black', 'ram': '8GB', 'price': 18999, 'sale_price': 16999, 'stock': 30},
            {'name': '128GB Amber Gold',  'storage': '128GB', 'color': 'Amber Gold',  'ram': '8GB', 'price': 18999, 'sale_price': None,  'stock': 25},
        ],
        'specs': [
            ('Display', '6.78" IPS LCD, 120Hz'),
            ('Battery', '5000mAh, 18W'),
        ],
        'images': [
            'Tecno-Spark-40-4G.jpg.jpeg',
            'Tecno-Spark-40-4G-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Tecno Pop 10',
        'brand': 'Tecno', 'category': 'Smartphones', 'subcategory': 'Budget Phones',
        'short_description': 'Entry-level Tecno with large display.',
        'description': 'Tecno Pop 10 is designed for first-time smartphone users offering essential features at a very accessible price.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'tecno,pop10,entry level,budget',
        'variants': [
            {'name': '64GB Black', 'storage': '64GB', 'color': 'Black', 'ram': '3GB', 'price': 9999, 'sale_price': 8499, 'stock': 40},
        ],
        'specs': [('Display', '6.56" IPS LCD'), ('Battery', '5000mAh')],
        'images': ['Tecno-Pop-10-a.jpg.jpeg'],
    },

    # ════════════════ SMARTWATCHES ════════════════
    {
        'name': 'Apple Watch Series 10 46mm',
        'brand': 'Apple', 'category': 'Smartwatches',
        'short_description': 'Thinnest Apple Watch with the biggest display yet.',
        'description': (
            'Apple Watch Series 10 is the thinnest and lightest Apple Watch ever. '
            'The wider display and advanced health sensors track your wellbeing around the clock.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'apple,watch,series10,health,fitness',
        'variants': [
            {'name': '46mm Jet Black Aluminium', 'storage': '', 'color': 'Jet Black', 'ram': '', 'price': 59999, 'sale_price': 54999, 'stock': 15},
            {'name': '46mm Rose Gold Aluminium', 'storage': '', 'color': 'Rose Gold', 'ram': '', 'price': 59999, 'sale_price': None,  'stock': 10},
        ],
        'specs': [
            ('Display', '46mm Always-On Retina LTPO OLED'),
            ('Chip', 'S10'),
            ('Health', 'ECG, Blood Oxygen, Sleep Apnea Detection'),
            ('Battery', '18hr'),
            ('Water Resistance', '50m'),
        ],
        'images': [
            'Apple-Watch-Series-10-46mm.jpg.jpeg',
            'Apple-Watch-Series-10-46mm-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Apple Watch Ultra 3',
        'brand': 'Apple', 'category': 'Smartwatches',
        'short_description': 'The most rugged Apple Watch for extreme adventures.',
        'description': (
            'Apple Watch Ultra 3 features a titanium case, 49mm always-on display, '
            '60hr battery with low-power mode, and dual-frequency GPS for adventurers.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'apple,watch ultra 3,titanium,gps,adventure,sports',
        'variants': [
            {'name': 'Natural Titanium Orange Alpine', 'storage': '', 'color': 'Natural Titanium', 'ram': '', 'price': 119999, 'sale_price': None, 'stock': 8},
            {'name': 'Black Titanium Black Trail',     'storage': '', 'color': 'Black Titanium',   'ram': '', 'price': 119999, 'sale_price': None, 'stock': 6},
        ],
        'specs': [
            ('Display', '49mm Always-On Retina LTPO OLED'),
            ('Case', 'Grade-5 Titanium'),
            ('Battery', '60hr'),
            ('GPS', 'Dual-frequency L1 & L5'),
            ('Depth Rating', '100m'),
        ],
        'images': [
            'Apple-Watch-Ultra-3.jpg.jpeg',
            'Apple-Watch-Ultra-3-1.jpg.jpeg',
        ],
    },
    {
        'name': 'Apple Watch SE 3 40mm',
        'brand': 'Apple', 'category': 'Smartwatches',
        'short_description': 'Most affordable Apple Watch with essential health features.',
        'description': 'Apple Watch SE 3 gives you essential Apple Watch features — crash detection, heart rate, and workout tracking — at the best price.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'apple,watch se,affordable,health,fitness',
        'variants': [
            {'name': '40mm Midnight', 'storage': '', 'color': 'Midnight', 'ram': '', 'price': 34999, 'sale_price': 29999, 'stock': 20},
            {'name': '40mm Starlight','storage': '', 'color': 'Starlight','ram': '', 'price': 34999, 'sale_price': None,  'stock': 15},
        ],
        'specs': [
            ('Display', '40mm Retina LTPO OLED'),
            ('Chip', 'S9'),
            ('Battery', '18hr'),
            ('Water Resistance', '50m'),
        ],
        'images': [
            'Apple-Watch-SE-3-40mm.jpg.jpeg',
            'Apple-Watch-SE-3-40mm-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Infinix XBand XW4B Smart Band',
        'brand': 'Infinix', 'category': 'Smartwatches',
        'short_description': 'Affordable fitness tracker with heart rate and SpO2.',
        'description': 'Infinix XBand XW4B tracks heart rate, SpO2, and sleep at an accessible price point.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'infinix,xband,fitness,tracker',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 3999, 'sale_price': 3499, 'stock': 30},
        ],
        'specs': [
            ('Sensors', 'Heart Rate, SpO2, Sleep'),
            ('Battery', '7 days'),
            ('Water Resistance', 'IP68'),
        ],
        'images': ['Infinix-XBand-XW4B-Smart-Band.webp'],
    },

    # ════════════════ SMART GLASSES ════════════════
    {
        'name': 'Ray-Ban Meta Wayfarer Gen 2 Smart Glasses',
        'brand': 'Ray-Ban', 'category': 'Smart Glasses',
        'short_description': 'Iconic Wayfarer with Meta AI, camera, and open-ear audio.',
        'description': (
            'Ray-Ban Meta Wayfarer Gen 2 blends iconic style with hands-free Meta AI, '
            'open-ear speakers, and a 12MP camera. Live stream to Instagram and Facebook.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'ray-ban,meta,smart glasses,wayfarer,ai,camera',
        'variants': [
            {'name': 'Matte Black Polarized Graphite', 'storage': '', 'color': 'Matte Black', 'ram': '', 'price': 34999, 'sale_price': None, 'stock': 10},
            {'name': 'Shiny Black G15 Green',          'storage': '', 'color': 'Shiny Black', 'ram': '', 'price': 34999, 'sale_price': None, 'stock': 8},
        ],
        'specs': [
            ('Camera', '12MP ultra-wide'),
            ('Audio', 'Open-ear speakers'),
            ('AI', 'Meta AI voice assistant'),
            ('Battery', '4hr use, 36hr with case'),
            ('Connectivity', 'Bluetooth 5.3'),
        ],
        'images': [
            'Ray-Ban-Meta-Wayfarer-RW4012-Smart-Glasses-Gen-2-601-ST.webp',
            'Ray-Ban-Meta-Wayfarer-RW4012-Smart-Glasses-Gen-2-Matte-Black-Polarized-Gradient-Graphite.webp',
        ],
    },
    {
        'name': 'Ray-Ban Meta Skyler Gen 2 Smart Glasses',
        'brand': 'Ray-Ban', 'category': 'Smart Glasses',
        'short_description': 'Skyler frame with Meta AI and improved audio quality.',
        'description': 'Ray-Ban Meta Skyler Gen 2 brings smart tech to the Skyler frame with improved Meta AI, better audio, and updated 12MP camera.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'ray-ban,meta,skyler,smart glasses,ai',
        'variants': [
            {'name': 'Shiny Black Clear', 'storage': '', 'color': 'Shiny Black', 'ram': '', 'price': 34999, 'sale_price': None, 'stock': 8},
        ],
        'specs': [
            ('Camera', '12MP ultra-wide'),
            ('AI', 'Meta AI voice assistant'),
            ('Battery', '4hr use, 36hr with case'),
        ],
        'images': [
            'Ray-Ban-Meta-Skyler-RW4010-Smart-Glasses-Gen-2-800x800.webp',
            'Ray-Ban-Meta-Skyler-RW4010-Smart-Glasses-Gen-2-1024x1024.webp',
        ],
    },

    # ════════════════ GAMING ════════════════
    {
        'name': 'Xbox Series X',
        'brand': 'Xbox', 'category': 'Gaming', 'subcategory': 'Consoles',
        'short_description': 'The most powerful Xbox ever — 4K 120fps gaming.',
        'description': (
            'Xbox Series X delivers 12 teraflops of GPU power, true 4K gaming at up to 120fps, '
            'DirectX raytracing, and Quick Resume to jump between multiple games instantly.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': False,
        'tags': 'xbox,series x,4k,gaming,console,microsoft',
        'variants': [
            {'name': '1TB Carbon Black', 'storage': '1TB', 'color': 'Carbon Black', 'ram': '', 'price': 69999, 'sale_price': 64999, 'stock': 10},
        ],
        'specs': [
            ('CPU', 'Custom Zen 2, 3.8GHz 8-core'),
            ('GPU', '12 teraflops RDNA 2'),
            ('RAM', '16GB GDDR6'),
            ('Storage', '1TB Custom NVMe SSD'),
            ('Resolution', 'Up to 4K 120fps'),
            ('Disc Drive', 'UHD 4K Blu-Ray'),
        ],
        'images': [
            'Xbox-Series-X-1-768x768.jpg.jpeg',
            'Xbox-Series-X-a.jpg.jpeg',
        ],
    },
    {
        'name': 'Meta Quest 3S Xbox Edition',
        'brand': 'Meta', 'category': 'Gaming', 'subcategory': 'Consoles',
        'short_description': 'Mixed reality VR headset in exclusive Xbox edition.',
        'description': 'Meta Quest 3S Xbox Edition brings mixed reality gaming with Xbox design aesthetic. Play VR titles and access Xbox Game Pass Ultimate wirelessly.',
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': True,
        'tags': 'meta,quest 3s,vr,mixed reality,xbox,gaming',
        'variants': [
            {'name': '128GB Xbox Edition', 'storage': '128GB', 'color': 'Xbox Green', 'ram': '', 'price': 79999, 'sale_price': 74999, 'stock': 5},
        ],
        'specs': [
            ('Processor', 'Snapdragon XR2 Gen 2'),
            ('Display', '4K+ LCD per eye'),
            ('Storage', '128GB'),
            ('Mixed Reality', 'Full-colour passthrough'),
            ('Battery', '2.5hr gaming'),
        ],
        'images': [
            'Meta-Quest-3S-Xbox-Edition.jpg.jpeg',
            'Meta-Quest-3S-Xbox-Edition-768x768.jpg.jpeg',
        ],
    },

    # ════════════════ LAPTOPS ════════════════
    {
        'name': 'Infinix INBOOK X2 Gen11',
        'brand': 'Infinix', 'category': 'Laptops',
        'short_description': 'Slim 14" Intel Core i5 laptop with 16GB RAM.',
        'description': (
            'Infinix INBOOK X2 Gen11 is a slim, stylish laptop for productivity. '
            'Intel Core i5 Gen 11, 16GB RAM, and a full-HD IPS display at a competitive price.'
        ),
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'infinix,laptop,inbook,i5,slim',
        'variants': [
            {'name': '512GB Space Grey',  'storage': '512GB', 'color': 'Space Grey',  'ram': '16GB', 'price': 69999, 'sale_price': 64999, 'stock': 8},
            {'name': '512GB Aurora Green','storage': '512GB', 'color': 'Aurora Green','ram': '16GB', 'price': 69999, 'sale_price': None,  'stock': 6},
        ],
        'specs': [
            ('Display', '14" IPS FHD, 100% sRGB'),
            ('Processor', 'Intel Core i5 Gen 11'),
            ('RAM', '16GB DDR4'),
            ('Storage', '512GB NVMe SSD'),
            ('Battery', '55Wh, up to 12hr'),
            ('OS', 'Windows 11'),
        ],
        'images': ['Infinix-INBOOK-X2-GEN11.jpg.jpeg'],
    },

    # ════════════════ AUDIO ════════════════
    {
        'name': 'JBL Bar 1000',
        'brand': 'JBL', 'category': 'Audio', 'subcategory': 'Speakers',
        'short_description': '7.1.4 Dolby Atmos soundbar with detachable wireless surrounds.',
        'description': (
            'JBL Bar 1000 delivers 7.1.4-channel Dolby Atmos audio. Detachable surround speakers '
            'are rechargeable for a truly wireless surround experience. 880W total power.'
        ),
        'condition': 'new', 'is_featured': True, 'is_hot': True, 'is_new': False,
        'tags': 'jbl,soundbar,dolby atmos,7.1.4,surround sound',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 89999, 'sale_price': 79999, 'stock': 6},
        ],
        'specs': [
            ('Channels', '7.1.4'),
            ('Total Power', '880W'),
            ('Dolby Atmos', 'Yes'),
            ('DTS:X', 'Yes'),
            ('Wireless Surrounds', 'Detachable rechargeable'),
            ('Subwoofer', '10" wireless'),
        ],
        'images': [
            'JBL-Bar-1000.jpg.jpeg',
            'JBL-Bar-1000-A.jpg.jpeg',
        ],
    },
    {
        'name': 'JBL Tune 680NC Wireless Headphones',
        'brand': 'JBL', 'category': 'Audio', 'subcategory': 'Headphones',
        'short_description': 'Over-ear ANC headphones with 70hr battery.',
        'description': 'JBL Tune 680NC delivers Active Noise Cancelling in a comfortable over-ear design with 70 hours total battery life.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': False,
        'tags': 'jbl,tune 680,anc,wireless,headphones,70hr',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 12999, 'sale_price': 10999, 'stock': 20},
            {'name': 'Blue',  'storage': '', 'color': 'Blue',  'ram': '', 'price': 12999, 'sale_price': None,  'stock': 15},
        ],
        'specs': [
            ('ANC', 'Yes'),
            ('Battery', '70hr total'),
            ('Bluetooth', '5.3'),
        ],
        'images': [
            'JBL-Tune-680NC.webp',
            'JBL-Tune-680NC-b.webp',
        ],
    },
    {
        'name': 'JBL Tune 530BT Wireless Headphones',
        'brand': 'JBL', 'category': 'Audio', 'subcategory': 'Headphones',
        'short_description': 'Affordable on-ear wireless with 57hr battery.',
        'description': 'JBL Tune 530BT delivers JBL Pure Bass Sound in a lightweight on-ear design with 57 hours battery and hands-free calling.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'jbl,tune 530,bluetooth,on-ear,wireless',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 7999, 'sale_price': 6499, 'stock': 25},
            {'name': 'White', 'storage': '', 'color': 'White', 'ram': '', 'price': 7999, 'sale_price': None, 'stock': 20},
        ],
        'specs': [
            ('Battery', '57hr'),
            ('Bluetooth', '5.3'),
            ('Type', 'On-ear'),
        ],
        'images': [
            'JBL-Tune-530BT.webp',
            'JBL-Tune-530BT-a.webp',
        ],
    },
    {
        'name': 'SkullCandy Method 360 ANC Headphones',
        'brand': 'SkullCandy', 'category': 'Audio', 'subcategory': 'Headphones',
        'short_description': 'Over-ear ANC with 40hr battery and Skull-iQ smart features.',
        'description': 'SkullCandy Method 360 ANC delivers immersive noise cancelling with 40hr battery and Skull-iQ smart features.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'skullcandy,method 360,anc,headphones,wireless',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 14999, 'sale_price': 12999, 'stock': 15},
        ],
        'specs': [
            ('ANC', 'Active Noise Cancelling'),
            ('Battery', '40hr'),
            ('Bluetooth', '5.2'),
        ],
        'images': [
            'SkullCandy-Method-360-ANC-c.webp',
            'SkullCandy-Method-360-ANC-b.webp',
            'SkullCandy-Method-360-ANC-c-768x768.webp',
        ],
    },

    # ════════════════ ACCESSORIES ════════════════
    {
        'name': 'Anker Nano 75W Car Charger + 240W Cable',
        'brand': 'Anker', 'category': 'Accessories', 'subcategory': 'Chargers & Cables',
        'short_description': '75W car charger with free 240W braided USB-C cable.',
        'description': 'Anker Nano 75W Car Charger charges your laptop and phone from the car. Comes with a premium 240W braided USB-C cable.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'anker,car charger,75w,usbc,fast charge',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 4999, 'sale_price': 3999, 'stock': 30},
        ],
        'specs': [
            ('Output', '75W USB-C'),
            ('Cable', '240W USB-C braided included'),
        ],
        'images': ['Anker-Nano-75W-Car-Charger-and-Anker-Prime-USB-C-to-USB-C-Cable-240W-Upcycled-Braided.jpg.jpeg'],
    },
    {
        'name': 'Anker 335 67W Car Charger',
        'brand': 'Anker', 'category': 'Accessories', 'subcategory': 'Chargers & Cables',
        'short_description': 'Compact 67W car charger with dual USB-C ports.',
        'description': 'Anker 335 delivers 67W from dual USB-C ports in a slim car charger form factor.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'anker,car charger,67w,usbc',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 3499, 'sale_price': 2999, 'stock': 25},
        ],
        'specs': [('Output', '67W USB-C'), ('Ports', '2x USB-C')],
        'images': ['Anker-335-67W-Car-Charger.jpg.jpeg'],
    },
    {
        'name': 'Anker Laptop Charger 140W 4-Port',
        'brand': 'Anker', 'category': 'Accessories', 'subcategory': 'Chargers & Cables',
        'short_description': '140W GaN charger — charge laptop + 3 devices at once.',
        'description': 'Anker 140W 4-Port GaN Charger supports PD 3.1 and powers a MacBook Pro plus three other devices simultaneously.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': False,
        'tags': 'anker,140w,gan,laptop charger,4 port,usbc',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 8999, 'sale_price': 7499, 'stock': 18},
        ],
        'specs': [
            ('Output', '140W total'),
            ('Ports', '2x USB-C + 2x USB-A'),
            ('Standards', 'PD 3.1, QC 4+'),
            ('GaN', 'Yes'),
        ],
        'images': ['Anker-Laptop-Charger-140W-4-Port-PD-3.1-with-USB-C-Cable.jpg.jpeg'],
    },
    {
        'name': 'Anker Zolo Powerbank 20000mAh 22.5W',
        'brand': 'Anker', 'category': 'Accessories', 'subcategory': 'Power Banks',
        'short_description': '20000mAh power bank with 22.5W fast charging.',
        'description': 'Keep all your devices charged on the go. 22.5W fast charging ensures your phone is back to full quickly.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'anker,power bank,20000mah,22.5w,fast charge',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 5999, 'sale_price': 4999, 'stock': 25},
        ],
        'specs': [
            ('Capacity', '20000mAh'),
            ('Output', '22.5W'),
            ('Ports', 'USB-C + 2x USB-A'),
        ],
        'images': ['Anker-Zolo-Powerbank-20000mAh-22.5W-Fast-Charging-Power-Bank.webp'],
    },
    {
        'name': 'Hollyland LARK MAX 2 Wireless Microphone',
        'brand': 'Hollyland', 'category': 'Accessories', 'subcategory': 'Microphones',
        'short_description': 'Professional wireless lavalier mic for content creators.',
        'description': 'Hollyland LARK MAX 2 is a professional wireless microphone for creators and journalists. Crystal-clear 48kHz audio, 250m range.',
        'condition': 'new', 'is_featured': False, 'is_hot': True, 'is_new': True,
        'tags': 'hollyland,lark max,microphone,wireless,creator,lavalier',
        'variants': [
            {'name': 'Black', 'storage': '', 'color': 'Black', 'ram': '', 'price': 21999, 'sale_price': 19999, 'stock': 12},
            {'name': 'White', 'storage': '', 'color': 'White', 'ram': '', 'price': 21999, 'sale_price': None,  'stock': 10},
        ],
        'specs': [
            ('Range', '250m'),
            ('Audio', '48kHz/32-bit float'),
            ('Battery', '7hr per transmitter'),
            ('Noise Cancellation', 'AI-powered'),
        ],
        'images': [
            'Hollyland-LARK-MAX-2.webp',
            'Hollyland-LARK-MAX-2-a.webp',
        ],
    },
    {
        'name': 'Green Lion GLR 22 LED Ring Light',
        'brand': 'Green Lion', 'category': 'Accessories', 'subcategory': 'Ring Lights',
        'short_description': '22" professional ring light for creators and streaming.',
        'description': 'Green Lion GLR 22 provides even, flattering lighting for content creation, live streaming, video calls, and photography.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': False,
        'tags': 'green lion,ring light,led,creator,streaming',
        'variants': [
            {'name': 'White', 'storage': '', 'color': 'White', 'ram': '', 'price': 6999, 'sale_price': 5999, 'stock': 20},
        ],
        'specs': [
            ('Size', '22 inches'),
            ('Color Temperature', '2700K–6500K'),
            ('Brightness', 'Dimmable 1%–100%'),
        ],
        'images': ['Green-Lion-GLR-22-LED-Ring-Light.jpg.jpeg'],
    },
    {
        'name': 'iPhone 17 Pro TechWoven Case with MagSafe',
        'brand': 'Apple', 'category': 'Accessories', 'subcategory': 'Cases & Covers',
        'short_description': 'Official Apple woven case for iPhone 17 Pro with MagSafe.',
        'description': 'Apple TechWoven Case for iPhone 17 Pro features durable woven exterior and built-in MagSafe magnets.',
        'condition': 'new', 'is_featured': False, 'is_hot': False, 'is_new': True,
        'tags': 'apple,iphone17 pro,case,magsafe,woven',
        'variants': [
            {'name': 'Natural', 'storage': '', 'color': 'Natural', 'ram': '', 'price': 7999, 'sale_price': None, 'stock': 20},
            {'name': 'Black',   'storage': '', 'color': 'Black',   'ram': '', 'price': 7999, 'sale_price': None, 'stock': 18},
        ],
        'specs': [
            ('Material', 'TechWoven fabric'),
            ('MagSafe', 'Built-in magnets'),
            ('Compatibility', 'iPhone 17 Pro'),
        ],
        'images': [
            'iPhone-17-Pro-TechWoven-Case-with-MagSafe.webp',
            'iPhone-17-Pro-TechWoven-Case-with-MagSafe-a.webp',
        ],
    },
]

# ──────────────────────────────────────────────────────────────────
# BANNERS — exact filenames
# ──────────────────────────────────────────────────────────────────

BANNERS = [
    {
        'title': 'Samsung Galaxy S25 Ultra — Galaxy AI',
        'subtitle': 'The most intelligent Galaxy ever. Now in Kenya.',
        'position': 'hero', 'badge_text': 'NEW INSTOCK', 'badge_color': 'blue',
        'link': '/products/samsung-galaxy-s25-ultra/', 'order': 1,
        'images': ['X6855_NOTE50-Pro_Phoneplace-Banner-02-scaled.jpg.jpeg'],
    },
    {
        'title': 'Infinix Note 50 Pro — 180W Charge',
        'subtitle': 'Full battery in under 15 minutes. Experience the future.',
        'position': 'hero', 'badge_text': 'FRESH DEAL', 'badge_color': 'green',
        'link': '/products/infinix-note-50-pro-4g/', 'order': 2,
        'images': ['X6855_NOTE50-Pro_Phoneplace-Banner-02-1536x387.jpg.jpeg'],
    },
    {
        'title': 'Infinix GT 30 Pro — Built for Gaming',
        'subtitle': '144Hz AMOLED. Shoulder triggers. Dominate every match.',
        'position': 'hero', 'badge_text': 'HOT DEAL', 'badge_color': 'red',
        'link': '/products/infinix-gt-30/', 'order': 3,
        'images': ['GT-30Pro_Phoneplace-Banner.png'],
    },
    {
        'title': 'Apple Watch — Track Every Moment',
        'subtitle': 'Series 10, Ultra 3, SE 3 — all available now.',
        'position': 'hero', 'badge_text': 'NEW ARRIVAL', 'badge_color': 'purple',
        'link': '/category/smartwatches/', 'order': 4,
        'images': [
            'CCB002_CGA_Adhoc_Q2_24_iWatch_Banner_Update_Desktop_2000x.webp',
            'CCB002_CGA_Adhoc_Q2_24_iWatch_Banner_Update_Desktop_2000x-1536x400.webp',
        ],
    },
    {
        'title': 'PhonePlace Kenya — Your No.1 Phone Shop',
        'subtitle': 'Genuine products. Best prices. Nationwide delivery.',
        'position': 'promo', 'badge_text': 'TRUSTED STORE', 'badge_color': 'green',
        'link': '/', 'order': 5,
        'images': ['PhonePlace-kenya.jpg.jpeg'],
    },
    {
        'title': 'PhonePlace Corporate Solutions',
        'subtitle': 'Bulk orders for businesses. Contact us for quotes.',
        'position': 'section', 'badge_text': 'CORPORATE', 'badge_color': 'blue',
        'link': '/contact/', 'order': 6,
        'images': [
            'corporate-web-update.jpg.jpeg',
            'corporate.jpg.jpeg',
        ],
    },
]


# ──────────────────────────────────────────────────────────────────
# Management Command
# ──────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Seed DB with categories, brands, products, images and banners.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--images-dir',
            default=r'D:\gadaf\Documents\phone_place',
            help='Directory containing product/banner images.',
        )
        parser.add_argument('--clear', action='store_true', help='Wipe seed data first.')
        parser.add_argument('--no-images', action='store_true', help='Skip image assignment.')

    def handle(self, *args, **options):
        # ── Change 'store' to your actual Django app name ──────────
        from store.models import (
            Category, Brand, Product, ProductVariant,
            ProductImage, ProductSpecification, Banner,
        )

        images_dir = options['images_dir']
        use_images = not options['no_images']

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing seed data...'))
            for M in [Banner, ProductSpecification, ProductImage, ProductVariant, Product, Brand, Category]:
                M.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('  ✓ Done.'))

        img_index = {}
        if use_images:
            img_index = build_image_index(images_dir)
            count = sum(1 for k in img_index if not k.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')))
            self.stdout.write(self.style.SUCCESS(f'Image index built from: {images_dir}'))

        # ── Categories ──────────────────────────────────────────────
        self.stdout.write('\nSeeding categories...')
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data.get('icon', ''), 'order': cat_data.get('order', 0), 'is_active': True},
            )
            cat_map[cat_data['name']] = cat
            self.stdout.write(f'  {"+" if created else "="} {cat.name}')
            for sub_name in cat_data.get('subcategories', []):
                sub, created = Category.objects.get_or_create(
                    name=sub_name,
                    defaults={'parent': cat, 'is_active': True, 'order': 0},
                )
                cat_map[sub_name] = sub
                self.stdout.write(f'      {"+" if created else "="} {sub.name}')

        # ── Brands ──────────────────────────────────────────────────
        self.stdout.write('\nSeeding brands...')
        brand_map = {}
        for b in BRANDS:
            obj, created = Brand.objects.get_or_create(
                name=b['name'],
                defaults={
                    'description': b.get('description', ''),
                    'is_featured': b.get('is_featured', False),
                    'is_active': True,
                },
            )
            brand_map[b['name']] = obj
            self.stdout.write(f'  {"+" if created else "="} {obj.name}')

        # ── Products ────────────────────────────────────────────────
        self.stdout.write('\nSeeding products...')
        for prod_data in PRODUCTS:
            brand = brand_map.get(prod_data['brand'])
            subcategory = prod_data.get('subcategory')
            category = cat_map.get(subcategory) if subcategory else None
            if not category:
                category = cat_map.get(prod_data['category'])

            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'brand': brand,
                    'category': category,
                    'description': prod_data.get('description', ''),
                    'short_description': prod_data.get('short_description', ''),
                    'condition': prod_data.get('condition', 'new'),
                    'is_featured': prod_data.get('is_featured', False),
                    'is_hot': prod_data.get('is_hot', False),
                    'is_new': prod_data.get('is_new', False),
                    'tags': prod_data.get('tags', ''),
                    'is_active': True,
                },
            )
            self.stdout.write(f'  {"+" if created else "="} {product.name}')

            if created:
                for v in prod_data.get('variants', []):
                    ProductVariant.objects.create(
                        product=product,
                        name=v['name'],
                        storage=v.get('storage', ''),
                        color=v.get('color', ''),
                        ram=v.get('ram', ''),
                        price=Decimal(str(v['price'])),
                        sale_price=Decimal(str(v['sale_price'])) if v.get('sale_price') else None,
                        stock=v.get('stock', 0),
                        is_active=True,
                    )
                for order, (key, value) in enumerate(prod_data.get('specs', [])):
                    ProductSpecification.objects.create(
                        product=product, key=key, value=value, order=order,
                    )

            # Attach images (if product has none yet)
            if use_images and img_index and not product.images.exists():
                attached = 0
                for idx, filename in enumerate(prod_data.get('images', [])):
                    paths = find_files(img_index, filename)
                    if paths:
                        _attach_image(product, paths[0], is_primary=(idx == 0), order=idx)
                        attached += 1
                if attached:
                    self.stdout.write(f'      → {attached} image(s) attached')
                else:
                    self.stdout.write(self.style.WARNING(
                        f'      ⚠ No images found: {prod_data.get("images", [])}'
                    ))

        # ── Banners ─────────────────────────────────────────────────
        self.stdout.write('\nSeeding banners...')
        for b_data in BANNERS:
            banner, created = Banner.objects.get_or_create(
                title=b_data['title'],
                defaults={
                    'subtitle': b_data.get('subtitle', ''),
                    'position': b_data.get('position', 'hero'),
                    'badge_text': b_data.get('badge_text', ''),
                    'badge_color': b_data.get('badge_color', 'green'),
                    'link': b_data.get('link', ''),
                    'order': b_data.get('order', 0),
                    'is_active': True,
                },
            )
            if created and use_images and img_index:
                img_attached = False
                for filename in b_data.get('images', []):
                    paths = find_files(img_index, filename)
                    if paths:
                        rel = _copy_to_media(paths[0], 'banners')
                        banner.image = str(rel)
                        banner.save(update_fields=['image'])
                        self.stdout.write(f'  + {banner.title}  [{paths[0].name}]')
                        img_attached = True
                        break
                if not img_attached:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ No image for banner: {banner.title}'
                    ))
            else:
                self.stdout.write(f'  {"+" if created else "="} {banner.title}')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeding complete! '
            f'{len(PRODUCTS)} products | {len(BANNERS)} banners | '
            f'{len(CATEGORIES)} categories | {len(BRANDS)} brands'
        ))


# ──────────────────────────────────────────────────────────────────
# File helpers
# ──────────────────────────────────────────────────────────────────

def _copy_to_media(src: Path, subfolder: str) -> Path:
    dest_dir = Path(settings.MEDIA_ROOT) / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if not dest.exists():
        shutil.copy2(src, dest)
    return Path(subfolder) / src.name


def _attach_image(product, img_path: Path, is_primary: bool, order: int):
    from store.models import ProductImage  # ← change 'store' if needed
    rel = _copy_to_media(img_path, 'products')
    ProductImage.objects.create(
        product=product,
        image=str(rel),
        alt_text=product.name,
        is_primary=is_primary,
        order=order,
    )