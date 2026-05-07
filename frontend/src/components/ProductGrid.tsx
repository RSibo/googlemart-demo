import React, { useState, useEffect } from 'react';
import type { Product } from '../types';
import { useCart } from '../contexts/CartContext';
import { useChef } from '../contexts/ChefContext';
import Observer from './Observer';

const filterButtonStyle = {
  backgroundColor: '#f5f5f5',
  border: '1px solid #e0e0e0',
  borderRadius: '16px',
  padding: '6px 15px',
  cursor: 'pointer',
  color: '#333',
  fontSize: '14px'
};

const ProductGrid: React.FC = () => {
  const [products, setProducts] = useState<Record<string, Product>>({});
  const [addedSku, setAddedSku] = useState<string | null>(null);
  const { addToCart } = useCart();
  const { setVisibleProducts } = useChef();

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => setProducts(data));
  }, []);

  const handleVisible = (sku: string) => {
    setVisibleProducts((prev: string[]) => Array.from(new Set([...prev, sku])));
  };

  const handleHidden = (sku: string) => {
    setVisibleProducts((prev: string[]) => prev.filter((s: string) => s !== sku));
  };

  const handleAddToCart = (product: Product, sku: string) => {
    addToCart({ ...product, sku });
    setAddedSku(sku);
    setTimeout(() => setAddedSku(null), 1000);
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#fff' }}>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '10px', color: '#333' }}>
        Fresh Specials in NSW
      </h2>
      
      {/* Filter Bar */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap', fontSize: '14px', alignItems: 'center' }}>
        <span style={{ color: '#666' }}>Sort by</span>
        <select style={{ border: '1px solid #e0e0e0', borderRadius: '4px', padding: '5px' }}>
          <option>Relevance</option>
        </select>
        <button style={filterButtonStyle}>In stock</button>
        <button style={filterButtonStyle}>Specials</button>
        <button style={filterButtonStyle}>Sold By</button>
        <button style={filterButtonStyle}>Brand</button>
        <button style={filterButtonStyle}>Allergens</button>
        <button style={filterButtonStyle}>Dietary and Lifestyle</button>
        <button style={filterButtonStyle}>Health Star Rating</button>

      </div>

      <div style={{ color: '#666', marginBottom: '15px', fontSize: '14px' }}>
        1 - {Object.keys(products).length} of {Object.keys(products).length} Products
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '20px'
      }}>
        {Object.entries(products).map(([sku, product]) => (
          <Observer 
            key={sku} 
            sku={sku} 
            onVisible={handleVisible} 
            onHidden={handleHidden}
          >
            <div className="product-card" style={{
              background: 'white',
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              height: '100%',
              position: 'relative'
            }}>
              {/* Mock Special Badge */}
              <div style={{
                position: 'absolute',
                top: '10px',
                left: '10px',
                backgroundColor: '#e6f4ea',
                color: '#137333',
                fontSize: '12px',
                fontWeight: 'bold',
                padding: '4px 8px',
                borderRadius: '4px'
              }}>
                Fresh Special
              </div>

              <div>
                <div style={{
                  width: '100%',
                  height: '180px',
                  backgroundColor: '#fff',
                  borderRadius: '4px',
                  marginBottom: '15px',
                  overflow: 'hidden',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <img 
                    src={product.image_url || `https://loremflickr.com/400/400/${product.image_keyword.replace(/,/g, ',')}/all?lock=${sku}`} 
                    alt={product.name} 
                    style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                    onError={(e) => {
                      e.currentTarget.src = `https://loremflickr.com/400/400/${product.image_keyword.replace(/,/g, ',')}/all?lock=${sku}`;
                    }}
                  />
                </div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#333', marginBottom: '5px' }}>
                  ${product.price.toFixed(2)}
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
                  ${(product.price / 1).toFixed(2)} / 1EA
                </div>
                <div style={{ fontSize: '14px', color: '#333', height: '40px', overflow: 'hidden', lineHeight: '1.4' }}>
                  {product.name}
                </div>
              </div>
              <button 
                onClick={() => handleAddToCart(product, sku)}
                style={{
                  backgroundColor: addedSku === sku ? '#28a745' : '#00875a',
                  color: 'white',
                  border: 'none',
                  padding: '12px',
                  borderRadius: '24px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  marginTop: '15px',
                  transition: 'background-color 0.2s ease',
                  width: '100%'
                }}
              >
                {addedSku === sku ? 'Added!' : 'Add to cart'}
              </button>
            </div>
          </Observer>
        ))}
      </div>
    </div>
  );
};

export default ProductGrid;
