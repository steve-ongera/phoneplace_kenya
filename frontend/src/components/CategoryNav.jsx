// src/components/CategoryNav.jsx
import { useNavigate, useLocation } from 'react-router-dom';

export default function CategoryNav({ categories }) {
  const navigate = useNavigate();
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const activeCat = params.get('category');

  const topCats = (categories || []).filter(c => !c.parent);

  return (
    <div className="cat-navbar">
      <div className="cat-navbar-inner container">
        <button
          className={`cat-nav-item${!activeCat ? ' active' : ''}`}
          onClick={() => navigate('/products')}
        >
          <i className="bi bi-grid-3x3-gap"></i> All
        </button>
        {topCats.map(cat => (
          <button
            key={cat.id}
            className={`cat-nav-item${activeCat === cat.slug ? ' active' : ''}`}
            onClick={() => navigate(`/products?category=${cat.slug}`)}
          >
            {cat.icon && <i className={`bi ${cat.icon}`}></i>}
            {cat.name}
          </button>
        ))}
      </div>
    </div>
  );
}