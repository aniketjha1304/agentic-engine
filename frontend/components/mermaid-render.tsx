// mermaid-render.tsx
import { useEffect, useRef } from 'react';

interface MermaidProps {
  code: string;
}

export default function Mermaid({ code }: MermaidProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const renderMermaid = async () => {
      const mermaidModule = await import('mermaid');
      const mermaid = mermaidModule.default;

      mermaid.initialize({ startOnLoad: false });

      if (ref.current) {
        ref.current.innerHTML = '';
        try {
          console.log('Rendering mermaid diagram with code:', code);
          const { svg } = await mermaid.render('mermaid-diagram', code);
          if (ref.current) {
            ref.current.innerHTML = svg;
          }
        } catch (error) {
          console.error('Error rendering mermaid diagram:', error);
          if (ref.current) {
            ref.current.innerHTML = '<p>Error rendering diagram</p>';
          }
        }
      }
    };

    if (typeof window !== 'undefined') {
      renderMermaid();
    }
  }, [code]);

  return <div ref={ref} />;
}