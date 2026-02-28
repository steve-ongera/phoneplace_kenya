// src/components/CartDrawer.jsx
import { useApp } from '../context/AppContext';
import { useNavigate } from 'react-router-dom';
import { BASE_URL } from '../utils/api';

export default function CartDrawer() {
  const { cart, cartOpen, dispatch, removeFromCart, updateCartQty } = useApp();
  const navigate = useNavigate();

  const items = cart?.items || [];
  const total = cart?.total || 0;

  const close = () => dispatch({ type: 'SET_CART_OPEN', payload: false });

  const goCheckout = () => {
    close();
    navigate('/checkout');
  };

  return (
    <>
      {/* Overlay */}
      {cartOpen && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.4)', zIndex: 1099 }}
          onClick={close}
        />
      )}

      <div className={`cart-drawer${cartOpen ? ' open' : ''}`}>
        <div className="cart-drawer-header">
          <h3><i className="bi bi-bag"></i> Cart ({cart?.item_count || 0})</h3>
          <button onClick={close} style={{ background: 'none', border: 'none', fontSize: '1.3rem', color: 'var(--text-mid)', cursor: 'pointer' }}>
            <i className="bi bi-x-lg"></i>
          </button>
        </div>

        <div className="cart-drawer-body">
          {items.length === 0 ? (
            <div className="empty-state" style={{ padding: '3rem 1rem' }}>
              <i className="bi bi-bag-x" style={{ fontSize: '3rem', color: 'var(--border)' }}></i>
              <p style={{ marginTop: '1rem', color: 'var(--text-light)' }}>Your cart is empty</p>
              <button className="btn btn-primary btn-sm" style={{ marginTop: '0.75rem' }} onClick={() => { close(); navigate('/products'); }}>
                Shop Now
              </button>
            </div>
          ) : (
            items.map(item => {
              const imgSrc = item.product?.main_image?.image
                ? (item.product.main_image.image.startsWith('http') ? item.product.main_image.image : `${BASE_URL.replace('/api/v1', '')}${item.product.main_image.image}`)
                : '/placeholder.png';
              return (
                <div key={item.id} className="cart-item-row">
                  <img src={imgSrc} alt={item.product?.name} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontWeight: 600, fontSize: '0.85rem', lineHeight: 1.3, marginBottom: '0.25rem' }}>
                      {item.product?.name}
                    </p>
                    {item.variant && (
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-light)' }}>{item.variant.name}</p>
                    )}
                    <p style={{ color: 'var(--red)', fontWeight: 700, fontSize: '0.9rem' }}>
                      KSh {item.subtotal?.toLocaleString()}
                    </p>
                    <div className="cart-qty-ctrl">
                      <button onClick={() => updateCartQty(item.id, item.quantity - 1)}>−</button>
                      <span>{item.quantity}</span>
                      <button onClick={() => updateCartQty(item.id, item.quantity + 1)}>+</button>
                      <button
                        onClick={() => removeFromCart(item.id)}
                        style={{ marginLeft: '0.3rem', color: 'var(--red)', border: 'none', background: 'none', cursor: 'pointer', fontSize: '0.9rem' }}
                      >
                        <i className="bi bi-trash3"></i>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {items.length > 0 && (
          <div className="cart-drawer-footer">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', fontWeight: 700 }}>
              <span>Subtotal</span>
              <span style={{ color: 'var(--primary)' }}>KSh {total.toLocaleString()}</span>
            </div>
            <button className="btn btn-primary btn-full btn-lg" onClick={goCheckout}>
              <i className="bi bi-credit-card"></i> Checkout
            </button>
            <button className="btn btn-outline btn-full btn-sm" style={{ marginTop: '0.5rem' }} onClick={close}>
              Continue Shopping
            </button>
          </div>
        )}
      </div>
    </>
  );
}