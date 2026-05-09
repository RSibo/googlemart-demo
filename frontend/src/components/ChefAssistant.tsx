import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  const { messages, sendMessage, settings, updateSettings, isConnected, isConnecting, error, connect, disconnect, isMuted, setIsMuted, setOnVideoData } = useChef();
  const { addToCart } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [activeRecipe, setActiveRecipe] = useState<any>(null);
  const [products, setProducts] = useState<Record<string, Product>>({});
  const [position, setPosition] = useState({ x: window.innerWidth - 370, y: window.innerHeight - 520 });
  const [isDragging, setIsDragging] = useState(false);
  const [rel, setRel] = useState({ x: 0, y: 0 });
  
  const [hasVideo, setHasVideo] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const mseRef = useRef<MediaSource | null>(null);
  const sourceBufferRef = useRef<SourceBuffer | null>(null);
  const videoQueueRef = useRef<ArrayBuffer[]>([]);
  const cachedInitSegmentRef = useRef<ArrayBuffer | null>(null);
  const videoErrorListenerAddedRef = useRef<boolean>(false);
  const transcriptEndRef = useRef<HTMLDivElement | null>(null);

  const decodeBase64 = (base64: string): Uint8Array => {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
  };

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const initMediaSource = useCallback(() => {
    const videoElement = videoRef.current;
    if (!videoElement) return;
    if (!window.MediaSource) {
      console.error("MediaSource API not supported.");
      return;
    }
    if (mseRef.current) return;

    const mediaSource = new MediaSource();
    mseRef.current = mediaSource;
    videoElement.src = URL.createObjectURL(mediaSource);

    if (!videoErrorListenerAddedRef.current) {
      videoElement.addEventListener("error", (e: any) => {
        if (!mseRef.current) return;
        mseRef.current = null;
        sourceBufferRef.current = null;
        videoQueueRef.current = [];
        console.error("Video playback error:", videoElement.error);
      });
      videoErrorListenerAddedRef.current = true;
    }

    mediaSource.addEventListener("sourceopen", () => {
      try {
        let sourceBuffer = sourceBufferRef.current;
        if (!sourceBuffer) {
          const type = 'video/mp4; codecs="avc1.42E01E, mp4a.40.2"';
          if (MediaSource.isTypeSupported(type)) {
            sourceBuffer = mediaSource.addSourceBuffer(type);
          } else {
            sourceBuffer = mediaSource.addSourceBuffer("video/mp4");
          }
          sourceBuffer.mode = "sequence";
          sourceBufferRef.current = sourceBuffer;

          const cachedInitSegment = cachedInitSegmentRef.current;
          if (cachedInitSegment && videoQueueRef.current[0] !== cachedInitSegment) {
            videoQueueRef.current.unshift(cachedInitSegment);
          }
        }

        const currentSourceBuffer = sourceBufferRef.current;
        if (!currentSourceBuffer) {
          return;
        }

        if (videoQueueRef.current.length > 0 && !currentSourceBuffer.updating) {
          const chunk = videoQueueRef.current.shift();
          if (chunk) {
            try {
              currentSourceBuffer.appendBuffer(chunk);
            } catch (e) {
              console.error("Error appending initial chunk to sourceBuffer:", e);
            }
          }
        }

        currentSourceBuffer.addEventListener("updateend", () => {
          const sb = sourceBufferRef.current;
          const ms = mseRef.current;
          if (!sb || !ms) return;

          if (videoElement.paused) {
            videoElement.play().catch((_e: any) => {
              console.error("Error playing video");
            });
          }

          if (ms.readyState === 'open' && videoElement.buffered.length > 0) {
            try {
              const end = videoElement.buffered.end(videoElement.buffered.length - 1);
              ms.setLiveSeekableRange(0, end);
            } catch (e) {}
          }

          if (!sb.updating && videoElement.currentTime > 6) {
            try {
              if (videoElement.buffered.length > 0) {
                const start = videoElement.buffered.start(0);
                const endToRemove = videoElement.currentTime - 5;
                if (endToRemove > start) {
                  sb.remove(start, endToRemove);
                  return;
                }
              }
            } catch (e) {}
          }

          if (videoQueueRef.current.length > 0 && !sb.updating) {
            const chunk = videoQueueRef.current.shift();
            if (chunk) {
              try {
                sb.appendBuffer(chunk);
              } catch (e) {
                console.error("Error appending queued chunk to sourceBuffer:", e);
              }
            }
          }
        });
      } catch (e: any) {
        console.error('Failed to initialize video stream.');
      }
    });
  }, []);

  useEffect(() => {
    setOnVideoData(() => (base64Data: string) => {
      setHasVideo(true);
      initMediaSource();
      
      const uint8Array = decodeBase64(base64Data);
      const arrayBuffer = uint8Array.buffer.slice(uint8Array.byteOffset, uint8Array.byteOffset + uint8Array.byteLength) as ArrayBuffer;

      if (!cachedInitSegmentRef.current) {
        cachedInitSegmentRef.current = arrayBuffer;
      }

      const sourceBuffer = sourceBufferRef.current;
      if (sourceBuffer && !sourceBuffer.updating && videoQueueRef.current.length === 0) {
        try {
          sourceBuffer.appendBuffer(arrayBuffer);
        } catch (e: any) {
          if (e.name === "InvalidStateError") {
            mseRef.current = null;
            sourceBufferRef.current = null;
            videoQueueRef.current = [];
            console.error("MediaSource Invalid State Error:", e);
          } else {
            console.error("Error appending buffer, pushing to queue:", e);
            videoQueueRef.current.push(arrayBuffer);
          }
        }
      } else {
        videoQueueRef.current.push(arrayBuffer);
      }
    });

    return () => setOnVideoData(null);
  }, [initMediaSource, setOnVideoData]);

  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => setProducts(data));
  }, []);

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      setPosition({
        x: e.clientX - rel.x,
        y: e.clientY - rel.y
      });
    };

    const onMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [isDragging, rel]);

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
          <img src="/static/gemini_star.svg" alt="Gemini Star" style={{ width: '32px', height: '32px' }} />
        </div>
        <span style={{ fontWeight: 'bold', whiteSpace: 'nowrap', opacity: isOpen ? 1 : 0 }}>Chef Help</span>
      </div>

      {/* Chat Flyout */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          top: `${position.y}px`,
          left: `${position.x}px`,
          width: '350px',
          height: '500px',
          backgroundColor: 'white',
          border: '1px solid #e0e0e0',
          borderRadius: '12px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 1002
        }}>
          <div 
            onMouseDown={(e) => {
              if (e.button !== 0) return;
              setIsDragging(true);
              setRel({
                x: e.clientX - position.x,
                y: e.clientY - position.y
              });
            }}
            style={{ 
              background: '#00875a', 
              color: 'white', 
              padding: '15px', 
              borderRadius: '12px 12px 0 0', 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              cursor: 'move'
            }}
          >
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
              <button onClick={() => setIsSettingsOpen(!isSettingsOpen)} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', padding: '4px' }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3"></circle>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
              </button>
            </div>
            <button 
              onClick={() => {
                setIsOpen(false);
                setPosition({ x: window.innerWidth - 370, y: window.innerHeight - 520 });
              }} 
              style={{ background: 'none', border: 'none', color: 'white', fontSize: '20px', cursor: 'pointer', fontWeight: 'bold' }}
            >
              &times;
            </button>
          </div>

          {!isSettingsOpen ? (
            <>
              <div style={{ position: 'relative', width: '100%', height: '150px', background: '#eee', display: 'flex', justifyContent: 'center', borderBottom: '1px solid #e0e0e0' }}>
                <video
                  ref={videoRef}
                  style={{ maxHeight: '100%', opacity: hasVideo ? 1 : 0 }}
                  playsInline
                  autoPlay
                />
                {!hasVideo && (
                  <div style={{ position: 'absolute', top: 0, left: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', color: '#888' }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#888" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                )}
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
                {error && (
                  <div style={{
                    backgroundColor: '#ffebee',
                    color: '#d32f2f',
                    padding: '10px',
                    borderRadius: '8px',
                    fontSize: '12px',
                    border: '1px solid #ffcdd2',
                    marginBottom: '10px'
                  }}>
                    <strong>Connection Error:</strong> {error}
                  </div>
                )}
                {messages.map(msg => (
                  <div key={msg.id} style={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    backgroundColor: msg.role === 'user' ? '#0084ff' : '#00875a',
                    color: msg.role === 'user' ? 'white' : 'white',
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
                <div ref={transcriptEndRef} />
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
              {(Object.keys(settings) as Array<keyof typeof settings>)
                .filter(key => key !== 'modelId')
                .map(key => (
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
