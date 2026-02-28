// src/pages/Auth.jsx
import { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import api from '../utils/api';

export function Login() {
  const { login, showToast } = useApp();
  const navigate = useNavigate();
  const location = useLocation();
  const next = new URLSearchParams(location.search).get('next') || '/';
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(form);
      showToast('Welcome back!', 'success');
      navigate(next);
    } catch (err) {
      setError(err?.error || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        <div className="card" style={{ padding: '2.5rem' }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <i className="bi bi-phone" style={{ fontSize: '2.5rem', color: 'var(--primary)' }}></i>
            <h2 style={{ marginTop: '0.5rem' }}>Welcome Back</h2>
            <p style={{ color: 'var(--text-light)', fontSize: '0.88rem' }}>Login to your PhonePlace Kenya account</p>
          </div>

          {error && (
            <div className="alert alert-danger" style={{ marginBottom: '1.25rem' }}>
              <i className="bi bi-exclamation-circle"></i> {error}
            </div>
          )}

          <form onSubmit={submit}>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input className="form-control" type="email" required value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} placeholder="your@email.com" />
            </div>
            <div className="form-group">
              <label className="form-label">Password</label>
              <input className="form-control" type="password" required value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} placeholder="••••••••" />
            </div>
            <button className="btn btn-primary btn-full btn-lg" type="submit" disabled={loading} style={{ marginTop: '0.5rem' }}>
              {loading ? <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span> Logging in…</> : 'Login'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.88rem', color: 'var(--text-light)' }}>
            Don't have an account? <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export function Register() {
  const { login, showToast } = useApp();
  const navigate = useNavigate();
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', password: '', password2: '' });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    setErrors({});
    if (form.password !== form.password2) {
      setErrors({ password2: 'Passwords do not match' });
      return;
    }
    setLoading(true);
    try {
      const data = await api.register({ ...form, username: form.email });
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      showToast('Account created! Welcome to PhonePlace Kenya 🎉', 'success');
      navigate('/');
    } catch (err) {
      setErrors(err || {});
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
      <div style={{ width: '100%', maxWidth: 480 }}>
        <div className="card" style={{ padding: '2.5rem' }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <i className="bi bi-person-plus" style={{ fontSize: '2.5rem', color: 'var(--primary)' }}></i>
            <h2 style={{ marginTop: '0.5rem' }}>Create Account</h2>
            <p style={{ color: 'var(--text-light)', fontSize: '0.88rem' }}>Join PhonePlace Kenya today</p>
          </div>

          <form onSubmit={submit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
              <div className="form-group">
                <label className="form-label">First Name</label>
                <input className="form-control" required value={form.first_name} onChange={e => update('first_name', e.target.value)} placeholder="John" />
              </div>
              <div className="form-group">
                <label className="form-label">Last Name</label>
                <input className="form-control" value={form.last_name} onChange={e => update('last_name', e.target.value)} placeholder="Doe" />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Email Address *</label>
              <input className={`form-control${errors.email ? ' error' : ''}`} type="email" required value={form.email} onChange={e => update('email', e.target.value)} placeholder="john@email.com" />
              {errors.email && <p className="form-error">{errors.email}</p>}
            </div>
            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <input className="form-control" value={form.phone} onChange={e => update('phone', e.target.value)} placeholder="07XXXXXXXX" />
            </div>
            <div className="form-group">
              <label className="form-label">Password *</label>
              <input className="form-control" type="password" required minLength={8} value={form.password} onChange={e => update('password', e.target.value)} placeholder="Min 8 characters" />
            </div>
            <div className="form-group">
              <label className="form-label">Confirm Password *</label>
              <input className={`form-control${errors.password2 ? ' error' : ''}`} type="password" required value={form.password2} onChange={e => update('password2', e.target.value)} placeholder="Repeat password" />
              {errors.password2 && <p className="form-error">{errors.password2}</p>}
            </div>
            <button className="btn btn-primary btn-full btn-lg" type="submit" disabled={loading}>
              {loading ? <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span> Creating account…</> : 'Create Account'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.88rem', color: 'var(--text-light)' }}>
            Already have an account? <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}