// src/components/ProductCard.jsx
import { Link } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { BASE_URL } from '../utils/api';

function Stars({ rating }) {
  return (
    <div className="stars">
      {[1,2,3,4,5].map(n => (
        <i key={n} className={`bi bi-star${n <= Math.round(rating) ? '-fill star-filled' : ' star-empty'}`}></i>
      ))}
    </div>
  );
}

export default function ProductCard({ product }) {
  const { addToCart, wishlistIds, toggleWishlist } = useApp();
  if (!product) return null;

  const imgSrc = product.main_image?.image
    ? (product.main_image.image.startsWith('http') ? product.main_image.image : `${BASE_URL.replace('/api/v1', '')}${product.main_image.image}`)
    : '/placeholder.png';

  const inWishlist = wishlistIds.includes(product.id);
  const hasDiscount = product.max_price && product.min_price && product.max_price > product.min_price;

  return (
    <div className="product-card">
      {/* Image */}
      <div className="product-card__image-wrap">
        <Link to={`/products/${product.slug}`}>
          <img src={imgSrc} alt={product.name} loading="lazy" />
        </Link>

        {/* Badges */}
        <div className="product-badges">
          {product.is_hot && <span className="badge badge-red">HOT</span>}
          {product.is_new && <span className="badge badge-new">NEW</span>}
          {product.is_featured && <span className="badge badge-green">OFFER</span>}
          {hasDiscount && (
            <span className="badge badge-orange">
              {Math.round((1 - product.min_price / product.max_price) * 100)}% OFF
            </span>
          )}
        </div>

        {/* Wishlist */}
        <button
          className={`wishlist-btn${inWishlist ? ' active' : ''}`}
          onClick={() => toggleWishlist(product.id)}
          title={inWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
        >
          <i className={`bi bi-heart${inWishlist ? '-fill' : ''}`}></i>
        </button>

        {/* Quick view */}
        <Link to={`/products/${product.slug}`} className="quick-view-btn">
          <i className="bi bi-eye"></i> Quick View
        </Link>
      </div>

      {/* Body */}
      <div className="product-card__body">
        <p className="product-card__brand">{product.brand_name}</p>
        <Link to={`/products/${product.slug}`}>
          <h3 className="product-card__name">{product.name}</h3>
        </Link>

        {product.average_rating > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.4rem' }}>
            <Stars rating={product.average_rating} />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-light)' }}>({product.review_count})</span>
          </div>
        )}

        <div className="product-card__price">
          <span className="price-current">
            KSh {product.min_price?.toLocaleString()}
            {product.max_price !== product.min_price && ` – KSh ${product.max_price?.toLocaleString()}`}
          </span>
        </div>

        <div className="product-card__actions">
          <button
            className="btn btn-dark btn-full btn-sm"
            onClick={() => addToCart(product.id)}
          >
            <i className="bi bi-bag-plus"></i> BUY NOW
          </button>
        </div>
      </div>
    </div>
  );
}