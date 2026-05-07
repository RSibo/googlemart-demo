import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import { CartProvider } from './contexts/CartContext.tsx';
import { ChefProvider } from './contexts/ChefContext.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChefProvider>
      <CartProvider>
        <App />
      </CartProvider>
    </ChefProvider>
  </React.StrictMode>,
);
