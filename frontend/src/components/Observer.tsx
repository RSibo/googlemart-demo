import React, { useEffect, useRef } from 'react';

interface ObserverProps {
  sku: string;
  onVisible: (sku: string) => void;
  onHidden: (sku: string) => void;
  children: React.ReactNode;
}

const Observer: React.FC<ObserverProps> = ({ sku, onVisible, onHidden, children }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          onVisible(sku);
        } else {
          onHidden(sku);
        }
      },
      { threshold: 0.5 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [sku, onVisible, onHidden]);

  return <div ref={ref}>{children}</div>;
};

export default Observer;
