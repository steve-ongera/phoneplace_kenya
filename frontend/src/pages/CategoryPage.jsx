// src/pages/CategoryPage.jsx
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import ProductCard from '../components/ProductCard';

export function CategoryList() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCategories().then(d => setCategories(d || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container loading-center"><div className="spinner"></div></div>;

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>All Categories</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
        {categories.filter(c => !c.parent).map(cat => (
          <Link key={cat.id} to={`/categories/${cat.slug}`} className="card" style={{ padding: '1.5rem', textAlign: 'center', textDecoration: 'none' }}>
            <i className={`bi ${cat.icon || 'bi-grid'}`} style={{ fontSize: '2.5rem', color: 'var(--primary)', marginBottom: '0.75rem' }}></i>
            <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>{cat.name}</h3>
            {cat.subcategories?.length > 0 && (
              <p style={{ fontSize: '0.78rem', color: 'var(--text-light)' }}>
                {cat.subcategories.map(s => s.name).join(' • ')}
              </p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}

export function CategoryDetail() {
  const { slug } = useParams();
  const [products, setProducts] = useState([]);
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [cats, prods] = await Promise.all([
          api.getCategories(),
          api.getByCategory(slug),
        ]);
        const cat = (cats || []).find(c => c.slug === slug);
        setCategory(cat);
        setProducts(prods?.results || prods || []);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <i className="bi bi-chevron-right"></i>
        <Link to="/categories">Categories</Link>
        <i className="bi bi-chevron-right"></i>
        <span>{category?.name || slug}</span>
      </nav>

      <div className="section-header" style={{ marginBottom: '1.5rem' }}>
        <h1>{category?.name || slug}</h1>
        <span style={{ color: 'var(--text-light)', fontSize: '0.88rem' }}>{products.length} products</span>
      </div>

      {loading ? (
        <div className="loading-center"><div className="spinner"></div></div>
      ) : products.length > 0 ? (
        <div className="products-grid">
          {products.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      ) : (
        <div className="empty-state">
          <i className="bi bi-search"></i>
          <h3>No products in this category</h3>
        </div>
      )}
    </div>
  );
}

export function BrandList() {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getBrands().then(d => setBrands(d?.results || d || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>Shop By Brand</h1>
      {loading ? (
        <div className="loading-center"><div className="spinner"></div></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '1rem' }}>
          {brands.map(brand => (
            <Link key={brand.id} to={`/brands/${brand.slug}`} className="card" style={{ padding: '1.5rem', textAlign: 'center' }}>
              {brand.logo ? (
                <img src={brand.logo} alt={brand.name} style={{ height: 50, objectFit: 'contain', margin: '0 auto 0.75rem' }} />
              ) : (
                <div style={{ fontSize: '2rem', marginBottom: '0.75rem', fontFamily: "'Syne',sans-serif", fontWeight: 800, color: 'var(--primary)' }}>
                  {brand.name[0]}
                </div>
              )}
              <h3 style={{ fontSize: '0.95rem' }}>{brand.name}</h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-light)' }}>{brand.product_count} products</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function BrandDetail() {
  const { slug } = useParams();
  const [brand, setBrand] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [brands, prods] = await Promise.all([
          api.getBrands(),
          api.getByBrand(slug),
        ]);
        const b = (brands?.results || brands || []).find(b => b.slug === slug);
        setBrand(b);
        setProducts(prods?.results || prods || []);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <i className="bi bi-chevron-right"></i>
        <Link to="/brands">Brands</Link>
        <i className="bi bi-chevron-right"></i>
        <span>{brand?.name || slug}</span>
      </nav>

      {brand && (
        <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
          {brand.logo && <img src={brand.logo} alt={brand.name} style={{ height: 60, objectFit: 'contain' }} />}
          <div>
            <h1 style={{ marginBottom: '0.25rem' }}>{brand.name}</h1>
            {brand.description && <p style={{ color: 'var(--text-mid)', fontSize: '0.9rem' }}>{brand.description}</p>}
            <p style={{ color: 'var(--text-light)', fontSize: '0.85rem' }}>{products.length} products available</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading-center"><div className="spinner"></div></div>
      ) : products.length > 0 ? (
        <div className="products-grid">
          {products.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      ) : (
        <div className="empty-state">
          <i className="bi bi-search"></i>
          <h3>No products for this brand</h3>
        </div>
      )}
    </div>
  );
}