// src/components/Footer.jsx
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        {/* Trust badges */}
        <div className="footer-trust">
          {[
            { icon: 'bi-truck', title: 'Country Wide Delivery', sub: 'Fast Delivery' },
            { icon: 'bi-patch-check', title: 'Great Prices', sub: 'Best Price Guarantee' },
            { icon: 'bi-headset', title: 'Support 24/7', sub: 'Get In Touch With Us' },
            { icon: 'bi-shield-check', title: 'Quality Guarantee', sub: 'Original Product' },
          ].map(item => (
            <div className="trust-item" key={item.title}>
              <i className={`bi ${item.icon}`}></i>
              <div>
                <h5>{item.title}</h5>
                <p>{item.sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Main footer links */}
        <div className="footer-top">
          {/* Brand */}
          <div>
            <h4 style={{ fontSize: '1.2rem', marginBottom: '0.75rem' }}>
              <i className="bi bi-phone" style={{ color: 'var(--primary)' }}></i> PhonePlace Kenya
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#9ca3af', marginBottom: '0.75rem', lineHeight: 1.7 }}>
              Bazaar Plaza, Mezzanine 1 unit 5,<br />Moi Avenue, Nairobi.
            </p>
            <p style={{ fontSize: '0.85rem', color: '#9ca3af' }}>
              <i className="bi bi-envelope" style={{ color: 'var(--primary)' }}></i> info@phoneplacekenya.com
            </p>
            <div className="footer-social" style={{ marginTop: '1rem' }}>
              {[
                { icon: 'bi-facebook', href: '#' },
                { icon: 'bi-instagram', href: '#' },
                { icon: 'bi-tiktok', href: '#' },
                { icon: 'bi-youtube', href: '#' },
                { icon: 'bi-twitter-x', href: '#' },
              ].map(s => (
                <a key={s.icon} href={s.href}>
                  <i className={`bi ${s.icon}`}></i>
                </a>
              ))}
            </div>
          </div>

          {/* Our Company */}
          <div>
            <h4>Our Company</h4>
            <ul className="footer-links">
              {['About Us', 'Contact Us', 'Service Center', 'Privacy Policy', 'Extended Warranty', 'Terms and Conditions', 'Shipping and Return Policy'].map(item => (
                <li key={item}><Link to="#">{item}</Link></li>
              ))}
            </ul>
          </div>

          {/* Shop By Brands */}
          <div>
            <h4>Shop By Brands</h4>
            <ul className="footer-links">
              {['Samsung', 'Apple', 'Infinix', 'JBL', 'Oneplus', 'Xiaomi', 'Google', 'Nothing', 'Oppo', 'Tecno'].map(b => (
                <li key={b}><Link to={`/brands/${b.toLowerCase()}`}>{b}</Link></li>
              ))}
            </ul>
          </div>

          {/* Call Us */}
          <div className="footer-contact">
            <h4>Call Us Here</h4>
            {[
              { label: 'Sales', num: '0726 526375' },
              { label: 'Sales', num: '0707 548758' },
              { label: 'Sales', num: '0721 510444' },
              { label: 'Sales', num: '0716 442992' },
              { label: 'Repairs', num: '0745 063030' },
              { label: 'Lipo Polepole', num: '0110464132' },
              { label: 'Corporate Sales', num: '0708465290' },
            ].map((c, i) => (
              <p key={i}>
                <i className="bi bi-telephone-fill"></i>
                <strong>{c.label}:</strong> {c.num}
              </p>
            ))}
          </div>
        </div>

        {/* Bottom */}
        <div className="footer-bottom">
          <p>©2026 <a href="/" style={{ color: 'var(--primary)' }}>PhonePlace Kenya</a>. All Rights Reserved.</p>
          <p style={{ fontSize: '0.78rem', color: '#4b5563' }}>
            Powered by PhonePlace Kenya &bull; Nairobi, Kenya
          </p>
        </div>
      </div>
    </footer>
  );
}