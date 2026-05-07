import React, { useState, useEffect } from 'react';
import ProductGrid from './components/ProductGrid';
import CartPanel from './components/CartPanel';
import ChefAssistant from './components/ChefAssistant';
import { useCart } from './contexts/CartContext';
import { useChef } from './contexts/ChefContext';
import './App.css';

const App: React.FC = () => {
  const [isCartOpen, setIsCartOpen] = useState(false);
  const { cart, total } = useCart();
  const { sendCartUpdate } = useChef();

  useEffect(() => {
    const skus = cart.map(item => item.sku);
    sendCartUpdate(skus);
  }, [cart, sendCartUpdate]);

  return (
    <div className="app">
      <header style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        backgroundColor: '#e6f4ea',
        padding: '15px 20px',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#00875a', display: 'flex', alignItems: 'center' }}>
          GoogleMart
        </div>
        
        <div style={{ flex: 1, maxWidth: '600px', margin: '0 40px', position: 'relative' }}>
          <input 
            type="text" 
            placeholder="Search products..." 
            style={{ 
              width: '100%', 
              padding: '12px 40px 12px 15px', 
              border: '1px solid #e0e0e0', 
              borderRadius: '24px',
              backgroundColor: '#f5f5f5',
              fontSize: '16px'
            }}
          />
          <span style={{ position: 'absolute', right: '15px', top: '50%', transform: 'translateY(-50%)', color: '#666' }}>🔍</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '30px', fontSize: '14px', color: '#333' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer' }}>
            <span>📋</span>
            <span>Lists & Buy again</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer' }}>
            <span>👤</span>
            <span>Log in or Sign up</span>
          </div>
          <div 
            onClick={() => setIsCartOpen(true)} 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '10px', 
              cursor: 'pointer',
              backgroundColor: '#f5f5f5',
              padding: '10px 15px',
              borderRadius: '20px'
            }}
          >
            <span>🛒</span>
            <span style={{ fontWeight: 'bold' }}>${total.toFixed(2)}</span>
            <span style={{ 
              backgroundColor: '#d93025', 
              color: 'white', 
              borderRadius: '50%', 
              padding: '2px 6px',
              fontSize: '12px'
            }}>
              {cart.length}
            </span>
          </div>
        </div>
      </header>

      <nav style={{
        marginTop: '70px', /* Height of fixed header */
        backgroundColor: 'white',
        padding: '10px 20px',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '14px'
      }}>
        <div style={{ display: 'flex', gap: '25px' }}>
          <a href="#" style={{ textDecoration: 'none', color: '#333', fontWeight: 'bold' }}>☰ Browse products</a>
          <a href="#" style={{ textDecoration: 'none', color: '#333' }}>Specials & catalogue</a>
          <a href="#" style={{ textDecoration: 'none', color: '#333' }}>Recipes & ideas</a>
          <a href="#" style={{ textDecoration: 'none', color: '#333' }}>Get more value</a>
          <a href="#" style={{ textDecoration: 'none', color: '#333' }}>Ways to shop</a>
          <a href="#" style={{ textDecoration: 'none', color: '#333' }}>Help</a>
        </div>
        <div style={{ display: 'flex', gap: '20px', color: '#666' }}>
          <a href="#" style={{ textDecoration: 'none', color: '#666' }}>Shop for business ↗</a>
          <span>📍 Stores</span>
        </div>
      </nav>

      {/* Delivery Bar */}
      <div style={{
        backgroundColor: '#f9f9f9',
        padding: '8px 20px',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '12px',
        color: '#333'
      }}>
        <div>
          🚚 Delivery to: <a href="#" style={{ color: '#00875a', textDecoration: 'underline' }}>Set your Delivery address</a>
        </div>
        <div>
          🕒 Select a time: <a href="#" style={{ color: '#00875a', textDecoration: 'underline' }}>View available times</a>
        </div>
      </div>

      <main>
        <ProductGrid />
      </main>

      <CartPanel isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
      <ChefAssistant />
    </div>
  );
};

export default App;
