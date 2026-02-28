// src/pages/Checkout.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import api from '../utils/api';
import { BASE_URL } from '../utils/api';

const STEPS = ['Cart Review', 'Delivery', 'Payment'];

export default function Checkout() {
  const { cart, isLoggedIn, showToast, fetchCart } = useApp();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [createdOrder, setCreatedOrder] = useState(null);
  const [mpesaLoading, setMpesaLoading] = useState(false);
  const [mpesaSent, setMpesaSent] = useState(false);

  const [form, setForm] = useState({
    full_name: '', email: '', phone: '', shipping_address: '',
    city: '', county: 'Nairobi', payment_method: 'mpesa', mpesa_phone: '', notes: ''
  });

  const items = cart?.items || [];
  const subtotal = cart?.total || 0;
  const shipping = 200;
  const total = subtotal + shipping;

  const update = (field, val) => setForm(f => ({ ...f, [field]: val }));

  const handleDeliverySubmit = async (e) => {
    e.preventDefault();
    if (!form.full_name || !form.email || !form.phone || !form.shipping_address || !form.city) {
      showToast('Please fill all required fields', 'error');
      return;
    }
    setLoading(true);
    try {
      const order = await api.createOrder({
        ...form,
        mpesa_phone: form.mpesa_phone || form.phone,
      });
      setCreatedOrder(order);
      setStep(2);
    } catch (err) {
      showToast(err?.detail || 'Failed to create order', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleStkPush = async () => {
    setMpesaLoading(true);
    try {
      await api.stkPush({ phone: form.mpesa_phone || form.phone, order_id: createdOrder.id });
      setMpesaSent(true);
      showToast('STK push sent! Check your phone to complete payment.', 'success');
    } catch (err) {
      showToast(err?.error || 'Failed to initiate M-Pesa payment', 'error');
    } finally {
      setMpesaLoading(false);
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="container" style={{ paddingTop: '3rem', paddingBottom: '3rem', textAlign: 'center' }}>
        <i className="bi bi-lock" style={{ fontSize: '3rem', color: 'var(--border)' }}></i>
        <h2 style={{ marginTop: '1rem' }}>Please Login to Checkout</h2>
        <button className="btn btn-primary btn-lg" style={{ marginTop: '1rem' }} onClick={() => navigate('/login?next=/checkout')}>
          Login / Register
        </button>
      </div>
    );
  }

  if (items.length === 0 && !createdOrder) {
    return (
      <div className="container empty-state" style={{ paddingTop: '3rem' }}>
        <i className="bi bi-bag-x"></i>
        <h3>Your cart is empty</h3>
        <button className="btn btn-primary btn-sm" style={{ marginTop: '0.75rem' }} onClick={() => navigate('/products')}>
          Shop Now
        </button>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem', maxWidth: 900 }}>
      <h1 style={{ marginBottom: '1.5rem' }}>Checkout</h1>

      {/* Steps */}
      <div className="checkout-steps" style={{ marginBottom: '2rem' }}>
        {STEPS.map((s, i) => (
          <div key={s} className="checkout-step">
            <div className="step-indicator">
              <div className={`step-circle${i === step ? ' active' : i < step ? ' done' : ''}`}>
                {i < step ? <i className="bi bi-check"></i> : i + 1}
              </div>
              <span className="step-label">{s}</span>
            </div>
            {i < STEPS.length - 1 && <div className={`step-line${i < step ? ' done' : ''}`}></div>}
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.5rem', alignItems: 'start' }}>
        {/* Left panel */}
        <div>
          {/* Step 0 – Cart Review */}
          {step === 0 && (
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Order Summary</h3>
              {items.map(item => {
                const imgSrc = item.product?.main_image?.image
                  ? (item.product.main_image.image.startsWith('http') ? item.product.main_image.image : `${BASE_URL.replace('/api/v1', '')}${item.product.main_image.image}`)
                  : '/placeholder.png';
                return (
                  <div key={item.id} style={{ display: 'flex', gap: '0.75rem', padding: '0.75rem 0', borderBottom: '1px solid var(--border)' }}>
                    <img src={imgSrc} alt={item.product?.name} style={{ width: 56, height: 56, objectFit: 'contain', background: '#f5f5f5', borderRadius: 'var(--radius-sm)', padding: 4 }} />
                    <div style={{ flex: 1 }}>
                      <p style={{ fontWeight: 600, fontSize: '0.88rem' }}>{item.product?.name}</p>
                      {item.variant && <p style={{ fontSize: '0.78rem', color: 'var(--text-light)' }}>{item.variant.name}</p>}
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-mid)' }}>x{item.quantity}</p>
                    </div>
                    <p style={{ fontWeight: 700, color: 'var(--red)', whiteSpace: 'nowrap' }}>KSh {item.subtotal?.toLocaleString()}</p>
                  </div>
                );
              })}
              <button className="btn btn-primary btn-full btn-lg" style={{ marginTop: '1.5rem' }} onClick={() => setStep(1)}>
                Proceed to Delivery <i className="bi bi-arrow-right"></i>
              </button>
            </div>
          )}

          {/* Step 1 – Delivery */}
          {step === 1 && (
            <form className="card" style={{ padding: '1.5rem' }} onSubmit={handleDeliverySubmit}>
              <h3 style={{ marginBottom: '1rem' }}>Delivery Information</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 1rem' }}>
                <div className="form-group">
                  <label className="form-label">Full Name *</label>
                  <input className="form-control" required value={form.full_name} onChange={e => update('full_name', e.target.value)} placeholder="John Doe" />
                </div>
                <div className="form-group">
                  <label className="form-label">Email *</label>
                  <input className="form-control" type="email" required value={form.email} onChange={e => update('email', e.target.value)} placeholder="john@email.com" />
                </div>
                <div className="form-group">
                  <label className="form-label">Phone *</label>
                  <input className="form-control" required value={form.phone} onChange={e => update('phone', e.target.value)} placeholder="0712345678" />
                </div>
                <div className="form-group">
                  <label className="form-label">City *</label>
                  <input className="form-control" required value={form.city} onChange={e => update('city', e.target.value)} placeholder="Nairobi" />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Delivery Address *</label>
                <textarea className="form-control" rows={3} required value={form.shipping_address} onChange={e => update('shipping_address', e.target.value)} placeholder="Street, Building, Estate…" />
              </div>
              <div className="form-group">
                <label className="form-label">County</label>
                <select className="form-control" value={form.county} onChange={e => update('county', e.target.value)}>
                  {['Nairobi','Mombasa','Kisumu','Nakuru','Eldoret','Thika','Murang\'a','Kiambu','Machakos','Nyeri'].map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Order Notes (optional)</label>
                <textarea className="form-control" rows={2} value={form.notes} onChange={e => update('notes', e.target.value)} placeholder="Any special instructions?" />
              </div>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setStep(0)}>
                  <i className="bi bi-arrow-left"></i> Back
                </button>
                <button type="submit" className="btn btn-primary btn-lg" style={{ flex: 1 }} disabled={loading}>
                  {loading ? <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span> Processing…</> : <>Continue to Payment <i className="bi bi-arrow-right"></i></>}
                </button>
              </div>
            </form>
          )}

          {/* Step 2 – Payment */}
          {step === 2 && createdOrder && (
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem' }}>Payment</h3>
              <div className="alert alert-success" style={{ marginBottom: '1.5rem' }}>
                <i className="bi bi-check-circle-fill"></i>
                Order <strong>{createdOrder.order_number}</strong> created successfully!
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                  {['mpesa', 'cash'].map(method => (
                    <label key={method} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', padding: '0.75rem 1rem', border: `2px solid ${form.payment_method === method ? 'var(--primary)' : 'var(--border)'}`, borderRadius: 'var(--radius-sm)', flex: 1, background: form.payment_method === method ? 'var(--primary-light)' : '#fff' }}>
                      <input type="radio" name="payment" value={method} checked={form.payment_method === method} onChange={() => update('payment_method', method)} />
                      {method === 'mpesa' ? <><i className="bi bi-phone-fill" style={{ color: '#00a650' }}></i> M-Pesa</> : <><i className="bi bi-cash-stack"></i> Cash on Delivery</>}
                    </label>
                  ))}
                </div>

                {form.payment_method === 'mpesa' && (
                  <div>
                    <div className="form-group">
                      <label className="form-label">M-Pesa Phone Number</label>
                      <input
                        className="form-control"
                        value={form.mpesa_phone || form.phone}
                        onChange={e => update('mpesa_phone', e.target.value)}
                        placeholder="07XXXXXXXX"
                      />
                      <p style={{ fontSize: '0.78rem', color: 'var(--text-light)', marginTop: '0.3rem' }}>
                        You will receive an STK push prompt on this number.
                      </p>
                    </div>

                    {mpesaSent ? (
                      <div className="alert alert-info">
                        <i className="bi bi-phone-vibrate"></i>
                        Check your phone for the M-Pesa prompt. Enter your PIN to complete payment.
                        <br /><button className="btn btn-sm btn-primary" style={{ marginTop: '0.75rem' }} onClick={() => navigate(`/orders/${createdOrder.id}`)}>
                          View Order
                        </button>
                      </div>
                    ) : (
                      <button className="btn btn-primary btn-full btn-lg" onClick={handleStkPush} disabled={mpesaLoading}>
                        {mpesaLoading
                          ? <><span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span> Sending…</>
                          : <><i className="bi bi-phone-fill"></i> Pay KSh {total.toLocaleString()} via M-Pesa</>
                        }
                      </button>
                    )}
                  </div>
                )}

                {form.payment_method === 'cash' && (
                  <div>
                    <div className="alert alert-warning">
                      <i className="bi bi-info-circle"></i>
                      Pay with cash upon delivery. Note: Cash on delivery is only available within Nairobi.
                    </div>
                    <button className="btn btn-accent btn-full btn-lg" onClick={() => navigate(`/orders/${createdOrder.id}`)}>
                      <i className="bi bi-check-lg"></i> Confirm Order
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Order summary sidebar */}
        <div className="card" style={{ padding: '1.25rem', position: 'sticky', top: 'calc(var(--navbar-h) + 60px)' }}>
          <h4 style={{ marginBottom: '1rem', fontFamily: "'Syne',sans-serif" }}>Order Total</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
              <span style={{ color: 'var(--text-mid)' }}>Subtotal</span>
              <span>KSh {subtotal.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
              <span style={{ color: 'var(--text-mid)' }}>Shipping</span>
              <span>KSh {shipping.toLocaleString()}</span>
            </div>
            <div style={{ borderTop: '1px solid var(--border)', paddingTop: '0.6rem', display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: '1rem' }}>
              <span>Total</span>
              <span style={{ color: 'var(--primary)' }}>KSh {(createdOrder?.total || total).toLocaleString()}</span>
            </div>
          </div>
          <div style={{ background: 'var(--bg)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', fontSize: '0.8rem', color: 'var(--text-light)' }}>
            <i className="bi bi-shield-lock-fill" style={{ color: 'var(--primary)', marginRight: '0.4rem' }}></i>
            Secured & encrypted checkout
          </div>
        </div>
      </div>
    </div>
  );
}