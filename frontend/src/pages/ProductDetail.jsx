// src/pages/ProductDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../utils/api';
import { useApp } from '../context/AppContext';
import ProductCard from '../components/ProductCard';
import { BASE_URL } from '../utils/api';

function Stars({ rating, size = '0.9rem' }) {
  return (
    <div className="stars">
      {[1,2,3,4,5].map(n => (
        <i key={n} style={{ fontSize: size }} className={`bi bi-star${n <= Math.round(rating) ? '-fill star-filled' : ' star-empty'}`}></i>
      ))}
    </div>
  );
}

export default function ProductDetail() {
  const { slug } = useParams();
  const { addToCart, wishlistIds, toggleWishlist } = useApp();
  const [product, setProduct] = useState(null);
  const [related, setRelated] = useState([]);
  const [recentlyViewed, setRecentlyViewed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [qty, setQty] = useState(1);
  const [activeImg, setActiveImg] = useState(0);
  const [activeTab, setActiveTab] = useState('specs');

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [prod, rel, rv] = await Promise.allSettled([
          api.getProduct(slug),
          api.getRelated(slug),
          api.getRecentlyViewed(),
        ]);
        if (prod.status === 'fulfilled') {
          setProduct(prod.value);
          if (prod.value.variants?.length) setSelectedVariant(prod.value.variants[0]);
        }
        if (rel.status === 'fulfilled') setRelated(rel.value || []);
        if (rv.status === 'fulfilled') setRecentlyViewed(rv.value?.map(r => r.product) || []);
      } finally {
        setLoading(false);
        window.scrollTo(0, 0);
      }
    }
    load();
  }, [slug]);

  if (loading) return (
    <div className="container loading-center" style={{ paddingTop: '2rem', minHeight: '60vh' }}>
      <div className="spinner"></div>
    </div>
  );

  if (!product) return (
    <div className="container empty-state" style={{ paddingTop: '3rem' }}>
      <i className="bi bi-exclamation-circle"></i>
      <h3>Product not found</h3>
      <Link to="/products" className="btn btn-primary btn-sm" style={{ marginTop: '0.75rem' }}>Browse Products</Link>
    </div>
  );

  const images = product.images || [];
  const price = selectedVariant
    ? (selectedVariant.sale_price || selectedVariant.price)
    : (product.min_price || 0);
  const origPrice = selectedVariant?.sale_price ? selectedVariant.price : null;
  const inWishlist = wishlistIds.includes(product.id);

  const imgSrc = (img) => img?.image
    ? (img.image.startsWith('http') ? img.image : `${BASE_URL.replace('/api/v1', '')}${img.image}`)
    : '/placeholder.png';

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '3rem' }}>
      {/* Breadcrumb */}
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <i className="bi bi-chevron-right"></i>
        <Link to="/products">Products</Link>
        {product.category && (
          <><i className="bi bi-chevron-right"></i>
            <Link to={`/products?category=${product.category.slug}`}>{product.category.name}</Link>
          </>
        )}
        <i className="bi bi-chevron-right"></i>
        <span>{product.name}</span>
      </nav>

      {/* Main product section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', alignItems: 'start' }}>
        {/* Images */}
        <div>
          <div style={{ border: '1.5px solid var(--border)', borderRadius: 'var(--radius)', overflow: 'hidden', background: '#f9f9f9', aspectRatio: '1', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img
              src={images[activeImg] ? imgSrc(images[activeImg]) : '/placeholder.png'}
              alt={product.name}
              style={{ maxHeight: 420, maxWidth: '100%', objectFit: 'contain', padding: '1.5rem' }}
            />
          </div>
          {images.length > 1 && (
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {images.map((img, i) => (
                <button key={i} onClick={() => setActiveImg(i)}
                  style={{ width: 60, height: 60, border: `2px solid ${i === activeImg ? 'var(--primary)' : 'var(--border)'}`, borderRadius: 'var(--radius-sm)', overflow: 'hidden', background: '#f5f5f5', padding: 4, cursor: 'pointer', flexShrink: 0 }}>
                  <img src={imgSrc(img)} alt="" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div>
          {product.brand && (
            <Link to={`/brands/${product.brand.slug}`} style={{ color: 'var(--primary)', fontWeight: 600, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              {product.brand.name}
            </Link>
          )}
          <h1 style={{ marginTop: '0.3rem', marginBottom: '0.75rem' }}>{product.name}</h1>

          {/* Rating */}
          {product.average_rating > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <Stars rating={product.average_rating} size="1rem" />
              <span style={{ color: 'var(--text-light)', fontSize: '0.85rem' }}>
                {product.average_rating} ({product.review_count} reviews)
              </span>
            </div>
          )}

          {/* Price */}
          <div style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'baseline', gap: '0.75rem', flexWrap: 'wrap' }}>
            <span style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: '2rem', color: 'var(--red)' }}>
              KSh {Number(price).toLocaleString()}
            </span>
            {origPrice && (
              <span style={{ fontSize: '1rem', color: 'var(--text-light)', textDecoration: 'line-through' }}>
                KSh {Number(origPrice).toLocaleString()}
              </span>
            )}
            {selectedVariant?.discount_percentage > 0 && (
              <span className="badge badge-red">{selectedVariant.discount_percentage}% OFF</span>
            )}
          </div>

          {/* Variants */}
          {product.variants?.length > 0 && (
            <div style={{ marginBottom: '1.25rem' }}>
              <p style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text-mid)' }}>
                Options: <span style={{ fontWeight: 400 }}>{selectedVariant?.name}</span>
              </p>
              <div className="variant-options">
                {product.variants.map(v => (
                  <button
                    key={v.id}
                    className={`variant-opt${selectedVariant?.id === v.id ? ' selected' : ''}${v.stock === 0 ? ' out-of-stock' : ''}`}
                    onClick={() => v.stock > 0 && setSelectedVariant(v)}
                  >
                    {v.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Qty + Add to Cart */}
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <div className="qty-selector">
              <button onClick={() => setQty(q => Math.max(1, q - 1))}>−</button>
              <input type="number" value={qty} min="1" onChange={e => setQty(Math.max(1, parseInt(e.target.value) || 1))} />
              <button onClick={() => setQty(q => q + 1)}>+</button>
            </div>
            <button
              className="btn btn-primary btn-lg"
              style={{ flex: 1 }}
              onClick={() => addToCart(product.id, selectedVariant?.id, qty)}
            >
              <i className="bi bi-bag-plus"></i> Add to Cart
            </button>
            <button
              className={`btn btn-outline${inWishlist ? ' btn-accent' : ''}`}
              onClick={() => toggleWishlist(product.id)}
              title={inWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
            >
              <i className={`bi bi-heart${inWishlist ? '-fill' : ''}`}></i>
            </button>
          </div>

          {/* Stock */}
          {selectedVariant && (
            <div style={{ marginBottom: '1rem' }}>
              {selectedVariant.stock > 0 ? (
                <span style={{ color: 'var(--primary)', fontWeight: 600, fontSize: '0.85rem' }}>
                  <i className="bi bi-check-circle-fill"></i> In Stock ({selectedVariant.stock} available)
                </span>
              ) : (
                <span style={{ color: 'var(--red)', fontWeight: 600, fontSize: '0.85rem' }}>
                  <i className="bi bi-x-circle-fill"></i> Out of Stock
                </span>
              )}
            </div>
          )}

          {/* Short description */}
          {product.short_description && (
            <p style={{ color: 'var(--text-mid)', fontSize: '0.9rem', lineHeight: 1.7, marginBottom: '1rem' }}>
              {product.short_description}
            </p>
          )}

          {/* Trust icons */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', padding: '0.75rem', background: 'var(--bg)', borderRadius: 'var(--radius-sm)' }}>
            {[
              { icon: 'bi-shield-check', text: 'Genuine Product' },
              { icon: 'bi-truck', text: 'Countrywide Delivery' },
              { icon: 'bi-arrow-return-left', text: 'Easy Returns' },
              { icon: 'bi-credit-card', text: 'Secure Payment' },
            ].map(t => (
              <div key={t.text} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-mid)' }}>
                <i className={`bi ${t.icon}`} style={{ color: 'var(--primary)' }}></i> {t.text}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ marginTop: '2.5rem' }}>
        <div className="tabs">
          {['specs', 'description', 'reviews'].map(tab => (
            <button key={tab} className={`tab-btn${activeTab === tab ? ' active' : ''}`} onClick={() => setActiveTab(tab)}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === 'reviews' && ` (${product.review_count || 0})`}
            </button>
          ))}
        </div>

        {activeTab === 'specs' && (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
              <tbody>
                {(product.specifications || []).map((spec, i) => (
                  <tr key={i} style={{ background: i % 2 === 0 ? 'var(--bg)' : '#fff' }}>
                    <td style={{ padding: '0.65rem 1rem', fontWeight: 600, color: 'var(--text-mid)', width: '35%', borderBottom: '1px solid var(--border)' }}>{spec.key}</td>
                    <td style={{ padding: '0.65rem 1rem', borderBottom: '1px solid var(--border)' }}>{spec.value}</td>
                  </tr>
                ))}
                {!product.specifications?.length && (
                  <tr><td colSpan={2} style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-light)' }}>No specifications available</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'description' && (
          <div style={{ lineHeight: 1.8, color: 'var(--text-mid)', fontSize: '0.92rem' }}>
            {product.description ? (
              <div dangerouslySetInnerHTML={{ __html: product.description }} />
            ) : (
              <p style={{ color: 'var(--text-light)' }}>No description available.</p>
            )}
          </div>
        )}

        {activeTab === 'reviews' && (
          <div>
            {product.reviews?.length > 0 ? product.reviews.map(r => (
              <div key={r.id} style={{ padding: '1rem 0', borderBottom: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.4rem' }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--primary)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.9rem' }}>
                    {r.user_name?.[0]?.toUpperCase()}
                  </div>
                  <div>
                    <p style={{ fontWeight: 600, fontSize: '0.88rem' }}>{r.user_name}</p>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      <Stars rating={r.rating} />
                      {r.is_verified_purchase && <span className="badge badge-green" style={{ fontSize: '0.62rem' }}>Verified</span>}
                    </div>
                  </div>
                  <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--text-light)' }}>
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </div>
                {r.title && <p style={{ fontWeight: 600, marginBottom: '0.3rem' }}>{r.title}</p>}
                <p style={{ fontSize: '0.9rem', color: 'var(--text-mid)' }}>{r.comment}</p>
              </div>
            )) : (
              <p style={{ color: 'var(--text-light)', padding: '1.5rem 0' }}>No reviews yet. Be the first!</p>
            )}
          </div>
        )}
      </div>

      {/* Related products */}
      {related.length > 0 && (
        <section className="section" style={{ marginTop: '1.5rem' }}>
          <div className="section-header">
            <h2>Related Products</h2>
          </div>
          <div className="products-grid">
            {related.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
        </section>
      )}

      {/* Recently Viewed */}
      {recentlyViewed.filter(p => p.id !== product.id).length > 0 && (
        <section className="section">
          <div className="section-header">
            <h2>Recently Viewed</h2>
          </div>
          <div className="products-grid">
            {recentlyViewed.filter(p => p.id !== product.id).slice(0, 5).map(p => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {/* Responsive */}
      <style>{`
        @media (max-width: 768px) {
          .product-detail-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}