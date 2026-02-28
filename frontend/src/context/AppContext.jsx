// src/context/AppContext.jsx
import { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import api from '../utils/api';

const AppContext = createContext();

const initialState = {
  user: null,
  cart: null,
  wishlistIds: [],
  isLoggedIn: false,
  cartOpen: false,
  toasts: [],
  searchOpen: false,
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload, isLoggedIn: !!action.payload };
    case 'SET_CART':
      return { ...state, cart: action.payload };
    case 'SET_WISHLIST_IDS':
      return { ...state, wishlistIds: action.payload };
    case 'TOGGLE_CART':
      return { ...state, cartOpen: !state.cartOpen };
    case 'SET_CART_OPEN':
      return { ...state, cartOpen: action.payload };
    case 'TOGGLE_SEARCH':
      return { ...state, searchOpen: !state.searchOpen };
    case 'ADD_TOAST':
      return { ...state, toasts: [...state.toasts, { id: Date.now(), ...action.payload }] };
    case 'REMOVE_TOAST':
      return { ...state, toasts: state.toasts.filter(t => t.id !== action.payload) };
    case 'LOGOUT':
      return { ...initialState, toasts: state.toasts };
    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const showToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    dispatch({ type: 'ADD_TOAST', payload: { id, message, type } });
    setTimeout(() => dispatch({ type: 'REMOVE_TOAST', payload: id }), 3500);
  }, []);

  const fetchCart = useCallback(async () => {
    try {
      const cart = await api.getCart();
      dispatch({ type: 'SET_CART', payload: cart });
    } catch {}
  }, []);

  const fetchWishlist = useCallback(async () => {
    if (!localStorage.getItem('access_token')) return;
    try {
      const items = await api.getWishlist();
      dispatch({ type: 'SET_WISHLIST_IDS', payload: items.map(i => i.product.id) });
    } catch {}
  }, []);

  const checkAuth = useCallback(async () => {
    if (!localStorage.getItem('access_token')) return;
    try {
      const user = await api.getProfile();
      dispatch({ type: 'SET_USER', payload: user });
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }, []);

  useEffect(() => {
    checkAuth();
    fetchCart();
  }, [checkAuth, fetchCart]);

  useEffect(() => {
    if (state.isLoggedIn) fetchWishlist();
  }, [state.isLoggedIn, fetchWishlist]);

  const login = useCallback(async (credentials) => {
    const data = await api.login(credentials);
    localStorage.setItem('access_token', data.tokens.access);
    localStorage.setItem('refresh_token', data.tokens.refresh);
    dispatch({ type: 'SET_USER', payload: data.user });
    fetchCart();
    return data;
  }, [fetchCart]);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    dispatch({ type: 'LOGOUT' });
    fetchCart(); // get guest cart
  }, [fetchCart]);

  const addToCart = useCallback(async (productId, variantId = null, quantity = 1) => {
    try {
      await api.addToCart({ product_id: productId, variant_id: variantId, quantity });
      fetchCart();
      showToast('Added to cart!', 'success');
      dispatch({ type: 'SET_CART_OPEN', payload: true });
    } catch (err) {
      showToast('Failed to add to cart', 'error');
    }
  }, [fetchCart, showToast]);

  const removeFromCart = useCallback(async (itemId) => {
    try {
      await api.removeCartItem(itemId);
      fetchCart();
    } catch {}
  }, [fetchCart]);

  const updateCartQty = useCallback(async (itemId, quantity) => {
    try {
      await api.updateCartItem({ item_id: itemId, quantity });
      fetchCart();
    } catch {}
  }, [fetchCart]);

  const toggleWishlist = useCallback(async (productId, wishlistItemId) => {
    if (!state.isLoggedIn) {
      showToast('Please login to save items', 'info');
      return;
    }
    if (state.wishlistIds.includes(productId)) {
      await api.removeFromWishlist(wishlistItemId);
      dispatch({ type: 'SET_WISHLIST_IDS', payload: state.wishlistIds.filter(id => id !== productId) });
      showToast('Removed from wishlist');
    } else {
      await api.addToWishlist(productId);
      dispatch({ type: 'SET_WISHLIST_IDS', payload: [...state.wishlistIds, productId] });
      showToast('Saved to wishlist', 'success');
    }
  }, [state.isLoggedIn, state.wishlistIds, showToast]);

  const value = {
    ...state,
    dispatch,
    login,
    logout,
    fetchCart,
    addToCart,
    removeFromCart,
    updateCartQty,
    toggleWishlist,
    showToast,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export const useApp = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
};