// src/App.jsx
import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './global.css';

import { AppProvider } from './context/AppContext';
import Navbar from './components/Navbar';
import CategoryNav from './components/CategoryNav';
import Footer from './components/Footer';
import CartDrawer from './components/CartDrawer';
import Toasts from './components/Toast';

import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Checkout from './pages/Checkout';
import { Login, Register } from './pages/Auth';
import { Orders, OrderDetail } from './pages/Orders';
import Profile from './pages/Profile';
import { CategoryList, CategoryDetail, BrandList, BrandDetail } from './pages/CategoryPage';
import api from './utils/api';

function Layout({ children, categories }) {
  return (
    <>
      <Navbar categories={categories} />
      <CategoryNav categories={categories} />
      <main className="page-content" style={{ paddingTop: 'calc(var(--navbar-h) + 44px)', minHeight: '60vh' }}>
        {children}
      </main>
      <Footer />
      <CartDrawer />
      <Toasts />
    </>
  );
}

export default function App() {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    api.getCategories().then(d => setCategories(d || [])).catch(() => {});
  }, []);

  return (
    <BrowserRouter>
      <AppProvider>
        <Layout categories={categories}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<Products />} />
            <Route path="/products/:slug" element={<ProductDetail />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/orders/:id" element={<OrderDetail />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/categories" element={<CategoryList />} />
            <Route path="/categories/:slug" element={<CategoryDetail />} />
            <Route path="/brands" element={<BrandList />} />
            <Route path="/brands/:slug" element={<BrandDetail />} />
          </Routes>
        </Layout>
      </AppProvider>
    </BrowserRouter>
  );
}