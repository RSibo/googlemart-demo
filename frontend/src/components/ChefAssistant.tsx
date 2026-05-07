import React, { useState, useEffect } from 'react';
import { useChef } from '../contexts/ChefContext';
import { useCart } from '../contexts/CartContext';
import RecipePanel from './RecipePanel';
import type { Product } from '../types';

const VOICES = [
  "Zephyr", "Kore", "Orus", "Autonoe", "Umbriel", "Erinome", "Laomedeia", "Schedar", "Achird", "Sadachbia", 
  "Puck", "Fenrir", "Aoede", "Enceladus", "Algieba", "Algenib", "Achernar", "Gacrux", "Zubenelgenubi", 
  "Sadaltager", "Charon", "Leda", "Callirrhoe", "Iapetus", "Despina", "Rasalgethi", "Alnilam", 
  "Pulcherrima", "Vindemiatrix", "Sulafat"
];

const AVATARS = ["Kira", "Ingrid", "Vera", "Sam", "Jay", "Paul", "Ben", "Kai", "Carmen", "Leo", "Piper"];

const ChefAssistant: React.FC = () => {
  const { messages, sendMessage, avatarFrame, settings, updateSettings, isConnected, isConnecting, connect, disconnect, isMuted, setIsMuted } = useChef();
  const { addToCart } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [activeRecipe, setActiveRecipe] = useState<any>(null);
  const [products, setProducts] = useState<Record<string, Product>>({});

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => setProducts(data));
  }, []);

  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };

  const handleSuggestAction = (sku: string) => {
    const product = products[sku];
    if (product) {
      addToCart({ ...product, sku });
    }
  };

  return (
    <>
      {activeRecipe && (
        <RecipePanel 
          recipe={activeRecipe} 
          onClose={() => setActiveRecipe(null)} 
        />
      )}

      {/* Floating Icon */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: isOpen ? '180px' : '60px',
          height: '60px',
          background: 'linear-gradient(135deg, #007aff 0%, #00c781 100%)',
          borderRadius: '30px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          transition: 'width 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          overflow: 'hidden',
          zIndex: 1000,
          color: 'white'
        }}
      >
        <div style={{ width: '60px', height: '60px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <img src="/gemini_star.svg" alt="Gemini Star" style={{ width: '32px', height: '32px' }} />
        </div>
        <span style={{ fontWeight: 'bold', whiteSpace: 'nowrap', opacity: isOpen ? 1 : 0 }}>Chef Help</span>
      </div>

      {/* Chat Flyout */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '350px',
          height: '500px',
          backgroundColor: 'white',
          border: '1px solid #e0e0e0',
          borderRadius: '12px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1000
        }}>
          <div style={{ background: '#00875a', color: 'white', padding: '15px', borderRadius: '12px 12px 0 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>Virtual Chef</span>
              <button 
                onClick={() => isConnected || isConnecting ? disconnect() : connect()} 
                disabled={isConnecting}
                style={{ 
                  background: isConnecting ? '#888' : (isConnected ? '#d93025' : '#0084ff'), 
                  color: 'white', 
                  border: 'none', 
                  padding: '4px 8px', 
                  borderRadius: '4px', 
                  cursor: isConnecting ? 'wait' : 'pointer', 
                  fontSize: '12px', 
                  fontWeight: 'bold',
                  opacity: isConnecting ? 0.7 : 1
                }}
              >
                {isConnecting ? 'Connecting...' : (isConnected ? 'Disconnect' : 'Connect')}
              </button>
              <button onClick={() => setIsSettingsOpen(!isSettingsOpen)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px' }}>⚙️</button>
            </div>
            <button 
              onClick={() => setIsOpen(false)} 
              style={{ background: 'none', border: 'none', color: 'white', fontSize: '20px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              &times;
            </button>
          </div>

          {!isSettingsOpen ? (
            <>
              <div style={{ position: 'relative', width: '100%', height: '150px', background: '#eee', display: 'flex', justifyContent: 'center', borderBottom: '1px solid #e0e0e0' }}>
                <img src={avatarFrame || "/avatar.png"} alt="Avatar" style={{ maxHeight: '100%' }} />
                {isConnected && (
                  <button 
                    onClick={() => setIsMuted(!isMuted)} 
                    style={{
                      position: 'absolute',
                      bottom: '10px',
                      right: '10px',
                      background: 'rgba(0,0,0,0.5)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '50%',
                      width: '32px',
                      height: '32px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      fontSize: '16px'
                    }}
                    title={isMuted ? "Unmute Avatar" : "Mute Avatar"}
                  >
                    {isMuted ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <line x1="23" y1="9" x2="17" y2="15"></line>
                        <line x1="17" y1="9" x2="23" y2="15"></line>
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                      </svg>
                    )}
                  </button>
                )}
              </div>
              <div style={{ flex: 1, overflowY: 'auto', padding: '15px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {messages.map(msg => (
                  <div key={msg.id} style={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    backgroundColor: msg.role === 'user' ? '#0084ff' : '#e4e6eb',
                    color: msg.role === 'user' ? 'white' : 'black',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    maxWidth: '80%'
                  }}>
                    {msg.content}

                    {msg.suggestion && products[msg.suggestion] && (
                      <div style={{ marginTop: '10px', background: 'white', padding: '10px', borderRadius: '4px', border: '1px solid #ddd', color: 'black' }}>
                        <div style={{ fontSize: '12px', fontWeight: 'bold' }}>{products[msg.suggestion].name}</div>
                        <button 
                          onClick={() => handleSuggestAction(msg.suggestion!)}
                          style={{ width: '100%', marginTop: '5px', background: '#00875a', color: 'white', border: 'none', padding: '5px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}
                        >
                          Add to Cart
                        </button>
                      </div>
                    )}

                    {msg.ui?.component === 'recipe_card' && (
                      <button 
                        onClick={() => setActiveRecipe(msg.ui!.props)}
                        style={{ width: '100%', marginTop: '10px', background: 'white', color: '#00875a', border: '1px solid #00875a', padding: '5px', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}
                      >
                        View Full Recipe
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <div style={{ padding: '15px', borderTop: '1px solid #e0e0e0', display: 'flex', gap: '10px' }}>
                <input 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask the Chef..."
                  style={{ flex: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
                />
                <button onClick={handleSend} style={{ background: '#00875a', color: 'white', border: 'none', padding: '10px', borderRadius: '4px' }}>Send</button>
              </div>
            </>
          ) : (
            <div style={{ padding: '15px', overflowY: 'auto' }}>
              <h3>Settings</h3>
              {(Object.keys(settings) as Array<keyof typeof settings>).map(key => (
                <div key={key} style={{ marginBottom: '10px' }}>
                  <label style={{ display: 'block', fontSize: '12px', textTransform: 'capitalize' }}>
                    {key.replace(/([A-Z])/g, ' $1')}
                  </label>
                  {key === 'voice' ? (
                    <select 
                      value={settings.voice}
                      onChange={(e) => updateSettings({ ...settings, voice: e.target.value })}
                      style={{ width: '100%', padding: '5px' }}
                    >
                      {VOICES.map(v => <option key={v} value={v}>{v}</option>)}
                    </select>
                  ) : key === 'avatar' ? (
                    <select 
                      value={settings.avatar}
                      onChange={(e) => updateSettings({ ...settings, avatar: e.target.value })}
                      style={{ width: '100%', padding: '5px' }}
                    >
                      {AVATARS.map(a => <option key={a} value={a}>{a}</option>)}
                    </select>
                  ) : (
                    <input 
                      type={key === 'accessToken' ? 'password' : 'text'}
                      value={settings[key]}
                      onChange={(e) => updateSettings({ ...settings, [key]: e.target.value })}
                      style={{ width: '100%', padding: '5px' }}
                    />
                  )}
                </div>
              ))}
              <button onClick={() => setIsSettingsOpen(false)} style={{ width: '100%', padding: '10px', background: '#00875a', color: 'white', border: 'none', borderRadius: '4px' }}>Done</button>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default ChefAssistant;
