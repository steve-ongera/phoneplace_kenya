// src/pages/Home.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import HeroBanner from '../components/HeroBanner';
import ProductCard from '../components/ProductCard';

const PROMO_CARDS = [
  { slug: 'samsung', label: 'Galaxy S25 Series', sub: '2 years Warranty', badge: 'MAKE THE UPGRADE', badgeClass: 'badge-dark', img: null },
  { slug: 'infinix', label: 'Infinix Hot Offers', sub: 'Up to 10% OFF', badge: 'NEW INSTOCK', badgeClass: 'badge-green', img: null },
  { slug: 'tecno', label: 'CAMON 40 Series', sub: 'Up to 10% OFF', badge: 'FRESH DEAL', badgeClass: 'badge-accent', img: null },
  { slug: 'apple', label: 'iPhone 17 Series', sub: 'UP TO 10% OFF', badge: 'ONE MORE DEAL', badgeClass: 'badge-red', img: null },
];

const CAT_CARDS = [
  { icon: 'bi-phone', name: 'Smartphones', links: ['Samsung Phones', 'iPhone', 'Tecno Phones', 'Google Pixel'], slug: 'smartphones' },
  { icon: 'bi-controller', name: 'Gaming', links: ['Accessories', 'Gaming Console', 'Gaming Controllers', 'Gaming Headsets'], slug: 'gaming' },
  { icon: 'bi-headphones', name: 'Audio', links: ['Buds', 'Headphones', 'Speakers', 'Soundbar'], slug: 'audio' },
  { icon: 'bi-smartwatch', name: 'Smartwatch', links: ['Smartwatches', 'Apple Watch', 'Galaxy Watch', 'Smart Bands'], slug: 'smartwatch' },
  { icon: 'bi-bag', name: 'Accessories', links: ['Apple Accessories', 'Samsung Accessories', 'Chargers', 'Powerbank'], slug: 'accessories' },
  { icon: 'bi-device-hdd', name: 'Storage', links: ['Flash Drives', 'Hard Drives', 'Memory Cards', 'USB Hubs'], slug: 'storage' },
];

function SectionProducts({ title, slug, products, viewAllHref }) {
  if (!products?.length) return null;
  return (
    <section className="section">
      <div className="section-header">
        <h2>{title}</h2>
        <Link to={viewAllHref || `/products?brand=${slug}`}>Shop More <i className="bi bi-arrow-right"></i></Link>
      </div>
      <div className="products-grid">
        {products.slice(0, 10).map(p => <ProductCard key={p.id} product={p} />)}
      </div>
    </section>
  );
}

export default function Home() {
  const [heroBanners, setHeroBanners] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [bestSellers, setBestSellers] = useState([]);
  const [newArrivals, setNewArrivals] = useState([]);
  const [xiaomiProducts, setXiaomiProducts] = useState([]);
  const [oppoProducts, setOppoProducts] = useState([]);
  const [iphoneProducts, setIphoneProducts] = useState([]);
  const [infinixProducts, setInfinixProducts] = useState([]);
  const [samsungProducts, setSamsungProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [banners, feat, best, fresh, xiaomi, oppo, iphone, infinix, samsung] = await Promise.allSettled([
          api.getHeroBanners(),
          api.getFeatured(),
          api.getBestSellers(),
          api.getNewArrivals(),
          api.getByBrand('xiaomi'),
          api.getByBrand('oppo'),
          api.getByBrand('apple'),
          api.getByBrand('infinix'),
          api.getByBrand('samsung'),
        ]);
        if (banners.status === 'fulfilled') setHeroBanners(banners.value);
        if (feat.status === 'fulfilled') setFeatured(feat.value?.results || feat.value || []);
        if (best.status === 'fulfilled') setBestSellers(best.value?.results || best.value || []);
        if (fresh.status === 'fulfilled') setNewArrivals(fresh.value?.results || fresh.value || []);
        if (xiaomi.status === 'fulfilled') setXiaomiProducts(xiaomi.value?.results || xiaomi.value || []);
        if (oppo.status === 'fulfilled') setOppoProducts(oppo.value?.results || oppo.value || []);
        if (iphone.status === 'fulfilled') setIphoneProducts(iphone.value?.results || iphone.value || []);
        if (infinix.status === 'fulfilled') setInfinixProducts(infinix.value?.results || infinix.value || []);
        if (samsung.status === 'fulfilled') setSamsungProducts(samsung.value?.results || samsung.value || []);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div>
      {/* Hero + Promo cards */}
      <div style={{ background: 'var(--bg-white)', paddingBottom: '1rem' }}>
        <div className="container">
          <div style={{ paddingTop: '1rem' }}>
            <HeroBanner banners={heroBanners} />
          </div>

          {/* 4-promo cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
            {PROMO_CARDS.map(card => (
              <Link key={card.slug} to={`/brands/${card.slug}`} style={{
                background: 'var(--text-dark)', borderRadius: 'var(--radius)', padding: '1.1rem',
                minHeight: 140, display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
                transition: 'transform 0.2s', overflow: 'hidden', position: 'relative'
              }}
                onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-3px)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'none'}
              >
                <span className={`badge ${card.badgeClass}`} style={{ width: 'fit-content', marginBottom: '0.4rem' }}>
                  {card.badge}
                </span>
                <div>
                  <h3 style={{ color: '#fff', fontSize: '0.95rem', lineHeight: 1.2, marginBottom: '0.25rem' }}>{card.label}</h3>
                  <p style={{ color: 'var(--accent)', fontSize: '0.78rem', fontWeight: 600 }}>{card.sub}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Category cards */}
      <section className="section" style={{ background: '#fff' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            {CAT_CARDS.map(cat => (
              <Link key={cat.slug} to={`/categories/${cat.slug}`} className="card" style={{ display: 'flex', gap: '1rem', padding: '1rem', alignItems: 'flex-start' }}>
                <div style={{ background: 'var(--primary-light)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', flexShrink: 0 }}>
                  <i className={`bi ${cat.icon}`} style={{ fontSize: '1.8rem', color: 'var(--primary)' }}></i>
                </div>
                <div>
                  <h4 style={{ marginBottom: '0.4rem', fontSize: '0.95rem' }}>{cat.name}</h4>
                  {cat.links.map(l => (
                    <p key={l} style={{ fontSize: '0.8rem', color: 'var(--text-mid)', lineHeight: 1.6 }}>{l}</p>
                  ))}
                  <span style={{ color: 'var(--primary)', fontSize: '0.8rem', fontWeight: 600, marginTop: '0.3rem', display: 'inline-block' }}>
                    Shop More &raquo;
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Product sections */}
      <div className="container">
        <SectionProducts title="Xiaomi Deals" slug="xiaomi" products={xiaomiProducts} viewAllHref="/brands/xiaomi" />
        <SectionProducts title="Oppo Deals" slug="oppo" products={oppoProducts} viewAllHref="/brands/oppo" />
        <SectionProducts title="iPhone Deals" slug="apple" products={iphoneProducts} viewAllHref="/brands/apple" />
        <SectionProducts title="Infinix Deals" slug="infinix" products={infinixProducts} viewAllHref="/brands/infinix" />
        <SectionProducts title="This Week's Best-sellers" slug="" products={bestSellers} viewAllHref="/products?is_hot=true" />
        <SectionProducts title="Samsung Galaxy" slug="samsung" products={samsungProducts} viewAllHref="/brands/samsung" />

        {/* New arrivals */}
        {newArrivals.length > 0 && (
          <section className="section">
            <div className="section-header">
              <h2>See What's New</h2>
              <Link to="/products?is_new=true">View All <i className="bi bi-arrow-right"></i></Link>
            </div>
            <div className="products-grid">
              {newArrivals.slice(0, 10).map(p => <ProductCard key={p.id} product={p} />)}
            </div>
          </section>
        )}

        {/* Featured */}
        {featured.length > 0 && (
          <section className="section">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
              {[
                { icon: 'bi-headphones', title: 'New Headphones', sub: 'UP TO 10% OFF', bg: '#1a7a3e', badge: 'NEW PRODUCT' },
                { icon: 'bi-laptop', title: 'Macbook Sale', sub: "TODAY'S SUPER OFFER", bg: '#0f1923', badge: 'BIG SALE' },
                { icon: 'bi-controller', title: 'Gaming Deals', sub: 'UP TO 20% OFF', bg: '#374151', badge: 'DEALS & SALES' },
              ].map(b => (
                <div key={b.title} style={{ background: b.bg, borderRadius: 'var(--radius)', padding: '1.25rem 1.5rem', minHeight: 120, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', cursor: 'pointer' }}>
                  <span className="badge badge-green" style={{ width: 'fit-content', fontSize: '0.65rem' }}>{b.badge}</span>
                  <div>
                    <h3 style={{ color: '#fff', fontSize: '1.1rem', marginBottom: '0.25rem' }}>{b.title}</h3>
                    <p style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{b.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>

      {/* Responsive promo card fix */}
      <style>{`
        @media (max-width: 768px) {
          .promo-4-grid { grid-template-columns: repeat(2, 1fr) !important; }
          .cat-3-grid { grid-template-columns: repeat(2, 1fr) !important; }
        }
        @media (max-width: 480px) {
          .promo-4-grid { grid-template-columns: repeat(2, 1fr) !important; }
          .cat-3-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}