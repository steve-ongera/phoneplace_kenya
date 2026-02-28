// src/utils/api.js
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

function getHeaders() {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request(endpoint, options = {}) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: { ...getHeaders(), ...options.headers },
  });

  if (res.status === 401) {
    // Try refresh
    const refreshed = await refreshToken();
    if (refreshed) {
      const retry = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        headers: { ...getHeaders(), ...options.headers },
      });
      if (!retry.ok) throw new Error(await retry.text());
      return retry.json();
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
  }

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ error: res.statusText }));
    throw errorData;
  }

  if (res.status === 204) return null;
  return res.json();
}

async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE_URL}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('access_token', data.access);
    return true;
  } catch {
    return false;
  }
}

const api = {
  get: (url) => request(url),
  post: (url, body) => request(url, { method: 'POST', body: JSON.stringify(body) }),
  patch: (url, body) => request(url, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (url) => request(url, { method: 'DELETE' }),

  // Auth
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),

  // Products
  getProducts: (params = '') => api.get(`/products/${params}`),
  getProduct: (slug) => api.get(`/products/${slug}/`),
  getRelated: (slug) => api.get(`/products/${slug}/related/`),
  getFeatured: () => api.get('/products/featured/'),
  getBestSellers: () => api.get('/products/best_sellers/'),
  getNewArrivals: () => api.get('/products/new_arrivals/'),
  getByCategory: (slug) => api.get(`/products/by_category/?slug=${slug}`),
  getByBrand: (slug) => api.get(`/products/by_brand/?slug=${slug}`),
  searchProducts: (q) => api.get(`/products/?search=${encodeURIComponent(q)}`),

  // Categories & Brands
  getCategories: () => api.get('/categories/'),
  getBrands: () => api.get('/brands/'),
  getFeaturedBrands: () => api.get('/brands/featured/'),

  // Banners
  getBanners: () => api.get('/banners/'),
  getHeroBanners: () => api.get('/banners/hero/'),

  // Cart
  getCart: () => api.get('/cart/'),
  addToCart: (data) => request('/cart/', { method: 'POST', body: JSON.stringify(data) }),
  updateCartItem: (data) => request('/cart/update_item/', { method: 'PATCH', body: JSON.stringify(data) }),
  removeCartItem: (id) => api.delete(`/cart/${id}/`),
  clearCart: () => request('/cart/clear/', { method: 'DELETE' }),

  // Orders
  createOrder: (data) => api.post('/orders/', data),
  getOrders: () => api.get('/orders/'),
  getOrder: (id) => api.get(`/orders/${id}/`),

  // M-Pesa
  stkPush: (data) => api.post('/mpesa/stk-push/', data),

  // Wishlist
  getWishlist: () => api.get('/wishlist/'),
  addToWishlist: (productId) => api.post('/wishlist/', { product_id: productId }),
  removeFromWishlist: (id) => api.delete(`/wishlist/${id}/`),

  // Recently Viewed
  getRecentlyViewed: () => api.get('/recently-viewed/'),
};

export default api;
export { BASE_URL };