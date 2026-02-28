// src/components/CategoryNav.jsx
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function CategoryNav({ categories }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const params = new URLSearchParams(location.search);
  const activeCat = params.get('category');

  const topCats = (categories || []).filter(c => !c.parent);

  const handleNav = (slug) => {
    navigate(slug ? `/products?category=${slug}` : '/products');
    setDrawerOpen(false);
  };

  return (
    <>
      {/* ── Desktop / tablet horizontal bar ── */}
      <div className="cat-navbar">
        <div className="cat-navbar-inner container">
          {/* Mobile hamburger trigger */}
          <button
            className="cat-menu-trigger"
            onClick={() => setDrawerOpen(true)}
            aria-label="Browse categories"
          >
            <i className="bi bi-list"></i>
            <span>Categories</span>
          </button>

          {/* Desktop pills */}
          <div className="cat-pills">
            <button
              className={`cat-nav-item${!activeCat ? ' active' : ''}`}
              onClick={() => handleNav(null)}
            >
              <i className="bi bi-grid-3x3-gap"></i> All
            </button>
            {topCats.map(cat => (
              <button
                key={cat.id}
                className={`cat-nav-item${activeCat === cat.slug ? ' active' : ''}`}
                onClick={() => handleNav(cat.slug)}
              >
                {cat.icon && <i className={`bi ${cat.icon}`}></i>}
                {cat.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Mobile Sidebar Drawer ── */}
      {drawerOpen && (
        <div className="cat-drawer-overlay" onClick={() => setDrawerOpen(false)}>
          <nav className="cat-drawer" onClick={e => e.stopPropagation()}>
            <div className="cat-drawer-header">
              <span><i className="bi bi-grid-3x3-gap"></i> Browse Categories</span>
              <button onClick={() => setDrawerOpen(false)} aria-label="Close">
                <i className="bi bi-x-lg"></i>
              </button>
            </div>
            <div className="cat-drawer-body">
              <button
                className={`cat-drawer-item${!activeCat ? ' active' : ''}`}
                onClick={() => handleNav(null)}
              >
                <span className="cat-drawer-icon">
                  <i className="bi bi-grid-3x3-gap"></i>
                </span>
                <span>All Products</span>
              </button>
              {topCats.map(cat => (
                <button
                  key={cat.id}
                  className={`cat-drawer-item${activeCat === cat.slug ? ' active' : ''}`}
                  onClick={() => handleNav(cat.slug)}
                >
                  <span className="cat-drawer-icon">
                    <i className={`bi ${cat.icon || 'bi-tag'}`}></i>
                  </span>
                  <span>{cat.name}</span>
                  <i className="bi bi-chevron-right cat-drawer-arrow"></i>
                </button>
              ))}
            </div>
          </nav>
        </div>
      )}
    </>
  );
}