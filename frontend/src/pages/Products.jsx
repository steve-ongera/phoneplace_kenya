// src/pages/Products.jsx
import { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import api from '../utils/api';
import ProductCard from '../components/ProductCard';

function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-img"></div>
      <div style={{ padding: '0.85rem' }}>
        <div className="skeleton skeleton-text short" style={{ marginBottom: 6 }}></div>
        <div className="skeleton skeleton-text"></div>
        <div className="skeleton skeleton-text" style={{ width: '70%' }}></div>
      </div>
    </div>
  );
}

export default function Products() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const search = params.get('search') || '';
  const category = params.get('category') || '';
  const brand = params.get('brand') || '';
  const sortBy = params.get('sort') || '-created_at';

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      let url = `/products/?page=${page}&ordering=${sortBy}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (category) url += `&category__slug=${category}`;
      if (brand) url += `&brand__slug=${brand}`;
      const data = await api.get(url);
      setProducts(data.results || data || []);
      setTotal(data.count || 0);
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [page, search, category, brand, sortBy]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  useEffect(() => {
    api.getCategories().then(d => setCategories(d || [])).catch(() => {});
    api.getBrands().then(d => setBrands(d?.results || d || [])).catch(() => {});
  }, []);

  const setFilter = (key, value) => {
    const p = new URLSearchParams(location.search);
    if (value) p.set(key, value); else p.delete(key);
    p.delete('page');
    navigate(`/products?${p.toString()}`);
    setPage(1);
  };

  const pageCount = Math.ceil(total / 20);

  return (
    <div className="container" style={{ paddingTop: '1.5rem', paddingBottom: '3rem' }}>
      {/* Breadcrumb */}
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <i className="bi bi-chevron-right"></i>
        <span>Products</span>
        {category && <><i className="bi bi-chevron-right"></i><span style={{ textTransform: 'capitalize' }}>{category}</span></>}
        {brand && <><i className="bi bi-chevron-right"></i><span style={{ textTransform: 'capitalize' }}>{brand}</span></>}
        {search && <><i className="bi bi-chevron-right"></i><span>"{search}"</span></>}
      </nav>

      <div style={{ display: 'flex', gap: '1.5rem' }}>
        {/* Sidebar Filter */}
        <aside style={{ width: 220, flexShrink: 0 }} className="d-none d-md-block">
          <div className="filter-sidebar">
            <h3 style={{ fontFamily: "'Syne',sans-serif", fontSize: '1rem', marginBottom: '1rem' }}>
              <i className="bi bi-funnel"></i> Filters
            </h3>

            {/* Categories */}
            <div className="filter-group">
              <h4>Categories</h4>
              {(categories || []).filter(c => !c.parent).map(cat => (
                <label key={cat.id} className="filter-check">
                  <input
                    type="radio"
                    name="category"
                    checked={category === cat.slug}
                    onChange={() => setFilter('category', cat.slug === category ? '' : cat.slug)}
                  />
                  {cat.name}
                </label>
              ))}
            </div>

            {/* Brands */}
            <div className="filter-group">
              <h4>Brands</h4>
              {brands.slice(0, 15).map(b => (
                <label key={b.id} className="filter-check">
                  <input
                    type="radio"
                    name="brand"
                    checked={brand === b.slug}
                    onChange={() => setFilter('brand', b.slug === brand ? '' : b.slug)}
                  />
                  {b.name} <span style={{ fontSize: '0.72rem', color: 'var(--text-light)' }}>({b.product_count})</span>
                </label>
              ))}
            </div>

            {/* Reset */}
            <button className="btn btn-outline btn-sm btn-full" onClick={() => navigate('/products')}>
              <i className="bi bi-arrow-clockwise"></i> Reset Filters
            </button>
          </div>
        </aside>

        {/* Main */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Toolbar */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-light)' }}>
              {loading ? 'Loading…' : `${total.toLocaleString()} products found`}
              {search && <> for <strong>"{search}"</strong></>}
            </p>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button
                className="btn btn-outline btn-sm"
                style={{ display: 'flex' }}
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                <i className="bi bi-funnel"></i> Filter
              </button>
              <select
                className="form-control"
                style={{ padding: '0.4rem 0.6rem', fontSize: '0.82rem', width: 'auto' }}
                value={sortBy}
                onChange={e => setFilter('sort', e.target.value)}
              >
                <option value="-created_at">Newest First</option>
                <option value="created_at">Oldest First</option>
                <option value="min_price">Price: Low → High</option>
                <option value="-min_price">Price: High → Low</option>
              </select>
            </div>
          </div>

          {/* Grid */}
          <div className="products-grid">
            {loading
              ? Array.from({ length: 12 }).map((_, i) => <SkeletonCard key={i} />)
              : products.length > 0
                ? products.map(p => <ProductCard key={p.id} product={p} />)
                : (
                  <div className="empty-state" style={{ gridColumn: '1 / -1' }}>
                    <i className="bi bi-search"></i>
                    <h3>No products found</h3>
                    <p>Try adjusting your search or filters</p>
                    <button className="btn btn-primary btn-sm" style={{ marginTop: '0.75rem' }} onClick={() => navigate('/products')}>
                      Clear Filters
                    </button>
                  </div>
                )
            }
          </div>

          {/* Pagination */}
          {pageCount > 1 && (
            <div className="pagination">
              <button className="page-btn" disabled={page === 1} onClick={() => setPage(p => p - 1)}>
                <i className="bi bi-chevron-left"></i>
              </button>
              {Array.from({ length: Math.min(pageCount, 7) }, (_, i) => {
                const p = i + 1;
                return (
                  <button key={p} className={`page-btn${page === p ? ' active' : ''}`} onClick={() => setPage(p)}>
                    {p}
                  </button>
                );
              })}
              <button className="page-btn" disabled={page === pageCount} onClick={() => setPage(p => p + 1)}>
                <i className="bi bi-chevron-right"></i>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}