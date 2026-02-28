// src/components/Navbar.jsx
import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';

export default function Navbar({ categories }) {
  const { user, isLoggedIn, logout, cart, dispatch, cartOpen, searchOpen } = useApp();
  const [query, setQuery] = useState('');
  const [selectedCat, setSelectedCat] = useState('');
  const navigate = useNavigate();
  const searchRef = useRef(null);

  const cartCount = cart?.item_count || 0;

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/products?search=${encodeURIComponent(query.trim())}${selectedCat ? `&category=${selectedCat}` : ''}`);
      dispatch({ type: 'TOGGLE_SEARCH' }); // close mobile
    }
  };

  return (
    <>
      {/* Promo bar */}
      <div className="promo-bar">
        <i className="bi bi-truck"></i>
        We offer Countrywide Delivery &nbsp;|&nbsp;
        <i className="bi bi-lightning-charge-fill"></i>
        <span style={{ color: '#f5a623' }}>Flash Sale</span>
      </div>

      <nav className="navbar">
        <div className="navbar-inner">
          {/* Logo */}
          <Link to="/" className="navbar-logo" style={{ flexShrink: 0 }}>
            <span style={{ fontFamily: "'Syne',sans-serif", fontWeight: 800, fontSize: '1.25rem', color: 'var(--primary)', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <i className="bi bi-phone" style={{ fontSize: '1.4rem' }}></i>
              PhonePlace <span style={{ color: 'var(--text-dark)' }}>Kenya</span>
            </span>
          </Link>

          {/* Search – desktop */}
          <form
            className={`navbar-search${searchOpen ? ' visible' : ''}`}
            onSubmit={handleSearch}
          >
            <select value={selectedCat} onChange={e => setSelectedCat(e.target.value)}>
              <option value="">All Categories</option>
              {(categories || []).map(c => (
                <option key={c.id} value={c.slug}>{c.name}</option>
              ))}
            </select>
            <input
              ref={searchRef}
              type="text"
              placeholder="Search for products…"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
            <button type="submit">SEARCH</button>
          </form>

          {/* Actions */}
          <div className="navbar-actions">
            {/* Mobile search toggle */}
            <button
              className="navbar-icon-btn search-toggle"
              style={{ display: 'none' }}
              onClick={() => dispatch({ type: 'TOGGLE_SEARCH' })}
            >
              <i className="bi bi-search"></i>
              <span>Search</span>
            </button>

            {/* Need Help */}
            <a href="tel:0726526375" className="navbar-icon-btn" style={{ display: 'flex' }}>
              <i className="bi bi-telephone"></i>
              <span>0726526375</span>
            </a>

            {/* Account */}
            {isLoggedIn ? (
              <div style={{ position: 'relative' }} className="dropdown-wrap">
                <button className="navbar-icon-btn" onClick={() => navigate('/profile')}>
                  <i className="bi bi-person-circle"></i>
                  <span>{user?.first_name || 'Account'}</span>
                </button>
              </div>
            ) : (
              <button className="navbar-icon-btn" onClick={() => navigate('/login')}>
                <i className="bi bi-person"></i>
                <span>Login</span>
              </button>
            )}

            {/* Cart */}
            <button
              className="navbar-icon-btn"
              onClick={() => dispatch({ type: 'TOGGLE_CART' })}
              style={{ position: 'relative' }}
            >
              <i className="bi bi-bag"></i>
              <span>KSh {((cart?.total || 0)).toLocaleString()}</span>
              {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
            </button>
          </div>
        </div>
      </nav>
    </>
  );
}