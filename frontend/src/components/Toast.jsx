// src/components/Toast.jsx
import { useApp } from '../context/AppContext';

const icons = { success: 'bi-check-circle-fill', error: 'bi-x-circle-fill', info: 'bi-info-circle-fill', warning: 'bi-exclamation-triangle-fill' };

export default function Toasts() {
  const { toasts, dispatch } = useApp();
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type || 'success'}`}>
          <i className={`bi ${icons[t.type] || icons.success}`}></i>
          <span style={{ flex: 1 }}>{t.message}</span>
          <button onClick={() => dispatch({ type: 'REMOVE_TOAST', payload: t.id })}
            style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: '0.9rem', marginLeft: '0.5rem' }}>
            <i className="bi bi-x"></i>
          </button>
        </div>
      ))}
    </div>
  );
}