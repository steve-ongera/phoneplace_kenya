// src/pages/Orders.jsx
import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../utils/api';

const STATUS_CLASS = {
  pending: 'status-pending', confirmed: 'status-confirmed', processing: 'status-processing',
  shipped: 'status-shipped', delivered: 'status-delivered', cancelled: 'status-cancelled'
};

export function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getOrders()
      .then(d => setOrders(d?.results || d || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container loading-center"><div className="spinner"></div></div>;

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem' }}>
      <h1 style={{ marginBottom: '1.5rem' }}>My Orders</h1>

      {orders.length === 0 ? (
        <div className="empty-state">
          <i className="bi bi-bag-x"></i>
          <h3>No orders yet</h3>
          <p>When you place an order, it will appear here.</p>
          <Link to="/products" className="btn btn-primary btn-sm" style={{ marginTop: '0.75rem' }}>Start Shopping</Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {orders.map(order => (
            <div key={order.id} className="card" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div>
                  <p style={{ fontFamily: "'Syne',sans-serif", fontWeight: 700, fontSize: '1rem' }}>
                    Order #{order.order_number}
                  </p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-light)' }}>
                    {new Date(order.created_at).toLocaleDateString('en-KE', { dateStyle: 'medium' })}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                  <span className={`order-status-badge ${STATUS_CLASS[order.status] || ''}`}>
                    {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                  </span>
                  <span className={`order-status-badge ${order.payment_status === 'paid' ? 'status-delivered' : 'status-pending'}`}>
                    {order.payment_status === 'paid' ? <><i className="bi bi-check-circle-fill"></i> Paid</> : 'Awaiting Payment'}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                {order.items?.slice(0, 3).map((item, i) => (
                  <span key={i} style={{ fontSize: '0.82rem', color: 'var(--text-mid)', background: 'var(--bg)', padding: '0.25rem 0.6rem', borderRadius: '4px' }}>
                    {item.product_name} {item.variant_name && `(${item.variant_name})`} x{item.quantity}
                  </span>
                ))}
                {order.items?.length > 3 && <span style={{ fontSize: '0.82rem', color: 'var(--text-light)' }}>+{order.items.length - 3} more</span>}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                <p style={{ fontWeight: 700, color: 'var(--primary)' }}>
                  Total: KSh {Number(order.total).toLocaleString()}
                </p>
                <Link to={`/orders/${order.id}`} className="btn btn-outline btn-sm">
                  View Details <i className="bi bi-arrow-right"></i>
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getOrder(id)
      .then(setOrder)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="container loading-center"><div className="spinner"></div></div>;
  if (!order) return <div className="container empty-state" style={{ paddingTop: '3rem' }}><i className="bi bi-exclamation-circle"></i><h3>Order not found</h3></div>;

  const timeline = [
    { status: 'pending', label: 'Order Placed', icon: 'bi-bag-check' },
    { status: 'confirmed', label: 'Confirmed', icon: 'bi-check-circle' },
    { status: 'processing', label: 'Processing', icon: 'bi-gear' },
    { status: 'shipped', label: 'Shipped', icon: 'bi-truck' },
    { status: 'delivered', label: 'Delivered', icon: 'bi-house-check' },
  ];
  const statusOrder = ['pending', 'confirmed', 'processing', 'shipped', 'delivered'];
  const currentIdx = statusOrder.indexOf(order.status);

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '3rem', maxWidth: 860 }}>
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <i className="bi bi-chevron-right"></i>
        <Link to="/orders">My Orders</Link>
        <i className="bi bi-chevron-right"></i>
        <span>{order.order_number}</span>
      </nav>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h1>Order {order.order_number}</h1>
          <p style={{ color: 'var(--text-light)', fontSize: '0.88rem' }}>
            Placed on {new Date(order.created_at).toLocaleDateString('en-KE', { dateStyle: 'long' })}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span className={`order-status-badge ${STATUS_CLASS[order.status] || ''}`} style={{ fontSize: '0.88rem', padding: '0.4rem 0.9rem' }}>
            {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Order timeline */}
      {order.status !== 'cancelled' && (
        <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
          <h4 style={{ marginBottom: '1.25rem' }}>Order Progress</h4>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {timeline.map((step, i) => (
              <div key={step.status} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
                {i > 0 && (
                  <div style={{
                    position: 'absolute', top: 16, right: '50%', left: '-50%', height: 3,
                    background: i <= currentIdx ? 'var(--primary)' : 'var(--border)'
                  }} />
                )}
                <div style={{
                  width: 34, height: 34, borderRadius: '50%', zIndex: 1,
                  background: i <= currentIdx ? 'var(--primary)' : '#fff',
                  border: `2px solid ${i <= currentIdx ? 'var(--primary)' : 'var(--border)'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: i <= currentIdx ? '#fff' : 'var(--text-light)'
                }}>
                  <i className={`bi ${step.icon}`} style={{ fontSize: '0.85rem' }}></i>
                </div>
                <p style={{ fontSize: '0.72rem', marginTop: '0.4rem', textAlign: 'center', color: i <= currentIdx ? 'var(--primary)' : 'var(--text-light)', fontWeight: i === currentIdx ? 700 : 400 }}>
                  {step.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        {/* Items */}
        <div className="card" style={{ padding: '1.25rem', gridColumn: '1 / -1' }}>
          <h4 style={{ marginBottom: '1rem' }}>Items Ordered</h4>
          {order.items?.map((item, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: i < order.items.length - 1 ? '1px solid var(--border)' : 'none', gap: '0.75rem' }}>
              <div>
                <p style={{ fontWeight: 600, fontSize: '0.9rem' }}>{item.product_name}</p>
                {item.variant_name && <p style={{ fontSize: '0.78rem', color: 'var(--text-light)' }}>{item.variant_name}</p>}
                <p style={{ fontSize: '0.82rem', color: 'var(--text-mid)' }}>Qty: {item.quantity} × KSh {Number(item.price).toLocaleString()}</p>
              </div>
              <p style={{ fontWeight: 700, whiteSpace: 'nowrap', color: 'var(--text-dark)' }}>KSh {Number(item.subtotal).toLocaleString()}</p>
            </div>
          ))}
          <div style={{ borderTop: '2px solid var(--border)', marginTop: '0.75rem', paddingTop: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.9rem' }}>
              <span>Subtotal</span><span>KSh {Number(order.subtotal).toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.9rem' }}>
              <span>Shipping</span><span>KSh {Number(order.shipping_fee).toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: '1.05rem' }}>
              <span>Total</span><span style={{ color: 'var(--primary)' }}>KSh {Number(order.total).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Delivery */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <h4 style={{ marginBottom: '0.75rem' }}>Delivery Address</h4>
          <p style={{ fontWeight: 600 }}>{order.full_name}</p>
          <p style={{ color: 'var(--text-mid)', fontSize: '0.88rem', lineHeight: 1.8 }}>
            {order.shipping_address}<br />{order.city}, {order.county}
          </p>
          <p style={{ color: 'var(--text-mid)', fontSize: '0.88rem', marginTop: '0.5rem' }}>
            <i className="bi bi-telephone"></i> {order.phone}
          </p>
        </div>

        {/* Payment */}
        <div className="card" style={{ padding: '1.25rem' }}>
          <h4 style={{ marginBottom: '0.75rem' }}>Payment</h4>
          <p style={{ fontSize: '0.9rem', marginBottom: '0.4rem' }}>
            <span style={{ color: 'var(--text-light)' }}>Method: </span>
            {order.payment_method === 'mpesa' ? <><i className="bi bi-phone-fill" style={{ color: '#00a650' }}></i> M-Pesa</> : 'Cash on Delivery'}
          </p>
          <p style={{ fontSize: '0.9rem', marginBottom: '0.4rem' }}>
            <span style={{ color: 'var(--text-light)' }}>Status: </span>
            <span className={`order-status-badge ${order.payment_status === 'paid' ? 'status-delivered' : 'status-pending'}`}>
              {order.payment_status === 'paid' ? 'Paid' : 'Pending'}
            </span>
          </p>
          {order.mpesa_transaction_id && (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-mid)' }}>
              Receipt: <strong>{order.mpesa_transaction_id}</strong>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}