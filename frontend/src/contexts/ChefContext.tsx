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
  setOnVideoData: (callback: ((data: string) => void) | null) => void;
  audioContext: AudioContext | null;
}

const ChefContext = createContext<ChefContextType | undefined>(undefined);

const DEFAULT_SETTINGS: ChefSettings = {
  accessToken: localStorage.getItem('accessToken') || '',
  projectId: localStorage.getItem('projectId') || 'cloud-llm-preview1',
  location: localStorage.getItem('location') || 'us-central1',
  modelId: 'gemini-3.1-flash-live-preview-04-2026',
  voice: localStorage.getItem('voice') || 'Kore',
  avatar: localStorage.getItem('avatar') || 'Kira'
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
  const [onVideoData, setOnVideoData] = useState<((data: string) => void) | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const nextPlaybackTimeRef = useRef<number>(0);
  const micStreamRef = useRef<MediaStream | null>(null);

  const playAudioChunk = useCallback((base64Data: string) => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
      nextPlaybackTimeRef.current = audioContextRef.current.currentTime;
    }
    const ctx = audioContextRef.current;
    
    const binaryString = window.atob(base64Data);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    const int16Array = new Int16Array(bytes.buffer);
    const float32Array = new Float32Array(int16Array.length);
    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 32768.0;
    }
    
    const audioBuffer = ctx.createBuffer(1, float32Array.length, 24000);
    audioBuffer.copyToChannel(float32Array, 0);
    
    const source = ctx.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(ctx.destination);
    
    const startTime = Math.max(nextPlaybackTimeRef.current, ctx.currentTime);
    source.start(startTime);
    nextPlaybackTimeRef.current = startTime + audioBuffer.duration;
  }, []);

  const startMic = useCallback((socket: WebSocket) => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      micStreamRef.current = stream;
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(2048, 1, 1);
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        
        // Simple VAD to filter out silence
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);
        if (rms < 0.005) return; // Skip sending if too quiet
        
        const int16Array = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          int16Array[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
        }
        
        const bytes = new Uint8Array(int16Array.buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
          binary += String.fromCharCode(bytes[i]);
        }
        const base64Data = window.btoa(binary);
        
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({
            type: 'audio',
            content: base64Data
          }));
        }
      };
    }).catch(err => console.error('Failed to get mic:', err));
  }, []);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(track => track.stop());
      micStreamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
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
      startMic(socket);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'text') {
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          const role = data.role || 'chef';
          if (lastMessage && lastMessage.role === role && !lastMessage.suggestion && !lastMessage.ui) {
            return [
              ...prev.slice(0, -1),
              { ...lastMessage, content: lastMessage.content + data.content }
            ];
          } else {
            return [...prev, { role: role, content: data.content, id: Date.now().toString() }];
          }
        });
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
        if (onVideoData) {
          onVideoData(data.content);
        }
      } else if (data.type === 'audio') {
        if (!isMuted) {
          playAudioChunk(data.content);
        }
      } else if (data.type === 'error') {
        console.error('Gemini Error:', data.content);
        setError(data.content);
        setIsConnecting(false);
      }
    };

    socket.onclose = (event) => {
      setIsConnected(false);
      setIsConnecting(false);
      console.log('WebSocket closed', event);
      if (!event.wasClean) {
        setError(`Connection lost: ${event.reason || 'Unknown reason'} (Code: ${event.code})`);
      }
    };

    socketRef.current = socket;
  }, [settings, disconnect]);

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: 'user', content, id: Date.now().toString() }]);
      socketRef.current.send(JSON.stringify({ content }));
    }
  }, []);

  const sendCartUpdate = useCallback((skus: string[]) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'cart_update',
        content: skus
      }));
    }
  }, []);

  const updateSettings = useCallback((newSettings: ChefSettings) => {
    setSettings(newSettings);
    Object.entries(newSettings).forEach(([key, value]) => localStorage.setItem(key, value));
  }, []);

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
      connect, disconnect, isMuted, setIsMuted, setOnVideoData,
      audioContext: audioContextRef.current
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
