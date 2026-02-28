// src/pages/Profile.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import api from '../utils/api';

export default function Profile() {
  const { user, logout, showToast, dispatch } = useApp();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.profile?.phone || '',
    address: user?.profile?.address || '',
    city: user?.profile?.city || '',
    county: user?.profile?.county || '',
  });
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await api.updateProfile(form);
      dispatch({ type: 'SET_USER', payload: updated });
      showToast('Profile updated!', 'success');
    } catch {
      showToast('Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    showToast('Logged out successfully');
  };

  if (!user) {
    return (
      <div className="container empty-state" style={{ paddingTop: '3rem' }}>
        <i className="bi bi-person-x"></i>
        <h3>Not logged in</h3>
        <Link to="/login" className="btn btn-primary btn-sm" style={{ marginTop: '0.75rem' }}>Login</Link>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem', maxWidth: 800 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'var(--primary)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', fontWeight: 700, flexShrink: 0 }}>
          {user.first_name?.[0]?.toUpperCase() || user.username?.[0]?.toUpperCase()}
        </div>
        <div>
          <h2>{user.first_name} {user.last_name}</h2>
          <p style={{ color: 'var(--text-light)', fontSize: '0.88rem' }}>{user.email}</p>
          <p style={{ color: 'var(--text-light)', fontSize: '0.78rem' }}>
            Member since {new Date(user.date_joined).toLocaleDateString('en-KE', { dateStyle: 'medium' })}
          </p>
        </div>
        <button className="btn btn-outline btn-sm" style={{ marginLeft: 'auto' }} onClick={handleLogout}>
          <i className="bi bi-box-arrow-right"></i> Logout
        </button>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {[['profile', 'bi-person', 'Profile'], ['orders', 'bi-bag', 'My Orders'], ['wishlist', 'bi-heart', 'Wishlist']].map(([tab, icon, label]) => (
          <button key={tab} className={`tab-btn${activeTab === tab ? ' active' : ''}`} onClick={() => { setActiveTab(tab); if (tab === 'orders') navigate('/orders'); }}>
            <i className={`bi ${icon}`}></i> {label}
          </button>
        ))}
      </div>

      {activeTab === 'profile' && (
        <form className="card" style={{ padding: '1.5rem' }} onSubmit={save}>
          <h3 style={{ marginBottom: '1.25rem' }}>Personal Information</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input className="form-control" value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))} />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input className="form-control" value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-control" type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Phone</label>
            <input className="form-control" value={form.phone} onChange={e => setForm(f => ({ ...f, phone: e.target.value }))} />
          </div>
          <div className="form-group">
            <label className="form-label">Default Delivery Address</label>
            <textarea className="form-control" rows={2} value={form.address} onChange={e => setForm(f => ({ ...f, address: e.target.value }))} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
            <div className="form-group">
              <label className="form-label">City</label>
              <input className="form-control" value={form.city} onChange={e => setForm(f => ({ ...f, city: e.target.value }))} />
            </div>
            <div className="form-group">
              <label className="form-label">County</label>
              <input className="form-control" value={form.county} onChange={e => setForm(f => ({ ...f, county: e.target.value }))} />
            </div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving…' : <><i className="bi bi-check-lg"></i> Save Changes</>}
          </button>
        </form>
      )}
    </div>
  );
}