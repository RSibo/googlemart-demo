import React from 'react';
import { useCart } from '../contexts/CartContext';

interface CartPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

const CartPanel: React.FC<CartPanelProps> = ({ isOpen, onClose }) => {
  const { cart, removeFromCart, total } = useCart();

  return (
    <div style={{
      position: 'fixed',
      right: isOpen ? '0' : '-350px',
      top: 0,
      width: '300px',
      height: '100%',
      background: 'white',
      boxShadow: '-2px 0 10px rgba(0,0,0,0.1)',
      transition: 'right 0.3s ease',
      zIndex: 1001,
      padding: '20px',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0 }}>My Basket</h3>
        <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer' }}>&times;</button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {cart.map((item) => (
          <div key={item.sku} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '10px',
            border: '1px solid #eee',
            borderRadius: '4px'
          }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{item.name}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                ${item.price.toFixed(2)} {item.quantity > 1 ? `x ${item.quantity}` : ''}
              </div>
            </div>
            <button 
              onClick={() => removeFromCart(item.sku)}
              style={{ background: 'none', border: 'none', color: '#ff4d4f', cursor: 'pointer', fontSize: '18px' }}
            >
              &times;
            </button>
          </div>
        ))}
      </div>

      <div style={{ borderTop: '1px solid #eee', paddingTop: '20px', marginTop: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', marginBottom: '20px' }}>
          <span>Total:</span>
          <span>${total.toFixed(2)}</span>
        </div>
        <button style={{
          width: '100%',
          backgroundColor: '#00875a',
          color: 'white',
          border: 'none',
          padding: '15px',
          borderRadius: '4px',
          fontWeight: 'bold',
          cursor: 'pointer'
        }}>
          Checkout
        </button>
      </div>
    </div>
  );
};

export default CartPanel;
