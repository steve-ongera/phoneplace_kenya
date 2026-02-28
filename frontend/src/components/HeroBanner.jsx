// src/components/HeroBanner.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BASE_URL } from '../utils/api';

export default function HeroBanner({ banners }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    if (!banners?.length) return;
    const timer = setInterval(() => setCurrent(c => (c + 1) % banners.length), 4500);
    return () => clearInterval(timer);
  }, [banners]);

  if (!banners?.length) {
    // Fallback static banner matching site design
    return (
      <div style={{
        background: 'linear-gradient(135deg, #0f1923 0%, #1a7a3e 100%)',
        borderRadius: 'var(--radius)', overflow: 'hidden', marginBottom: '1.5rem',
        minHeight: 220, display: 'flex', alignItems: 'center', padding: '2rem',
        position: 'relative'
      }}>
        <div style={{ maxWidth: 520 }}>
          <span className="badge badge-green" style={{ marginBottom: '0.75rem' }}>30-90 DAYS</span>
          <h1 style={{ color: '#fff', fontSize: 'clamp(1.6rem, 4vw, 2.6rem)', lineHeight: 1.1, marginBottom: '0.5rem' }}>
            Corporate Financing<br /><span style={{ color: 'var(--accent)' }}>Made Easier</span>
          </h1>
          <p style={{ color: '#d1fae5', marginBottom: '1.25rem', maxWidth: 400 }}>
            Payment plan for corporate financing on smartphones.
          </p>
          <Link to="/contact" className="btn btn-accent btn-lg">Contact Us Today</Link>
        </div>
      </div>
    );
  }

  const banner = banners[current];
  const imgSrc = banner.image?.startsWith('http') ? banner.image : `${BASE_URL.replace('/api/v1', '')}${banner.image}`;

  return (
    <div style={{ position: 'relative', borderRadius: 'var(--radius)', overflow: 'hidden', marginBottom: '1.5rem', background: '#0f1923' }}>
      <img
        src={imgSrc}
        alt={banner.title}
        style={{ width: '100%', maxHeight: 420, objectFit: 'cover', display: 'block' }}
      />
      {/* Dots */}
      <div style={{ position: 'absolute', bottom: '1rem', left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: '0.4rem' }}>
        {banners.map((_, i) => (
          <button key={i} onClick={() => setCurrent(i)} style={{
            width: i === current ? 22 : 8, height: 8, borderRadius: 4, border: 'none',
            background: i === current ? '#fff' : 'rgba(255,255,255,.4)', transition: 'all 0.3s', padding: 0, cursor: 'pointer'
          }} />
        ))}
      </div>
    </div>
  );
}