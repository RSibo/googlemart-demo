import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { ChefSettings, ChatMessage } from '../types';

interface ChefContextType {
  messages: ChatMessage[];
  sendMessage: (text: string) => void;
  sendCartUpdate: (skus: string[]) => void;
  settings: ChefSettings;
  updateSettings: (settings: ChefSettings) => void;
  avatarFrame: string | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  visibleProducts: string[];
  setVisibleProducts: React.Dispatch<React.SetStateAction<string[]>>;
  connect: () => void;
  disconnect: () => void;
  isMuted: boolean;
  setIsMuted: (muted: boolean) => void;
}

const ChefContext = createContext<ChefContextType | undefined>(undefined);

const DEFAULT_SETTINGS: ChefSettings = {
  accessToken: localStorage.getItem('accessToken') || '',
  projectId: localStorage.getItem('projectId') || 'cloud-llm-preview1',
  location: localStorage.getItem('location') || 'us-central1',
  modelId: localStorage.getItem('modelId') || 'gemini-3.1-flash-live-preview-04-2026',
  voice: localStorage.getItem('voice') || 'Puck',
  avatar: localStorage.getItem('avatar') || 'Ben'
};

export const ChefProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [settings, setSettings] = useState<ChefSettings>(DEFAULT_SETTINGS);
  const [avatarFrame, setAvatarFrame] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [visibleProducts, setVisibleProducts] = useState<string[]>([]);
  const [isMuted, setIsMuted] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
    setAvatarFrame(null);
  }, []);

  const connect = useCallback(() => {
    disconnect();
    setIsConnecting(true);
    setError(null);

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
      setIsConnecting(false);
      socket.send(JSON.stringify({
        type: 'setup',
        content: settings
      }));
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'text') {
        setMessages(prev => [...prev, { role: 'chef', content: data.content, id: Date.now().toString() }]);
      } else if (data.type === 'product_suggestion') {
        setMessages(prev => [...prev, { 
          role: 'chef', 
          content: 'I recommend adding this to your cart:', 
          suggestion: data.content, 
          id: Date.now().toString() 
        }]);
      } else if (data.type === 'show_ui') {
        setMessages(prev => [...prev, { 
          role: 'chef', 
          content: `Opening ${data.component}...`, 
          ui: { component: data.component, props: data.props },
          id: Date.now().toString() 
        }]);
      } else if (data.type === 'video') {
        setAvatarFrame(`data:image/jpeg;base64,${data.content}`);
      } else if (data.type === 'error') {
        console.error('Gemini Error:', data.content);
        setError(data.content);
        setIsConnecting(false);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      setIsConnecting(false);
      console.log('WebSocket closed');
    };

    socketRef.current = socket;
  }, [settings, disconnect]);

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  const sendMessage = (content: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: 'user', content, id: Date.now().toString() }]);
      socketRef.current.send(JSON.stringify({ content }));
    }
  };

  const sendCartUpdate = (skus: string[]) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'cart_update',
        content: skus
      }));
    }
  };

  const updateSettings = (newSettings: ChefSettings) => {
    setSettings(newSettings);
    Object.entries(newSettings).forEach(([key, value]) => localStorage.setItem(key, value));
  };

  // Sync visible products context
  useEffect(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN && visibleProducts.length > 0) {
      socketRef.current.send(JSON.stringify({
        type: 'context_update',
        content: `User is currently viewing: ${visibleProducts.join(', ')}`
      }));
    }
  }, [visibleProducts]);

  return (
    <ChefContext.Provider value={{ 
      messages, sendMessage, sendCartUpdate, settings, updateSettings, 
      avatarFrame, isConnected, isConnecting, error, visibleProducts, setVisibleProducts,
      connect, disconnect, isMuted, setIsMuted
    }}>
      {children}
    </ChefContext.Provider>
  );
};

export const useChef = () => {
  const context = useContext(ChefContext);
  if (!context) throw new Error('useChef must be used within a ChefProvider');
  return context;
};
