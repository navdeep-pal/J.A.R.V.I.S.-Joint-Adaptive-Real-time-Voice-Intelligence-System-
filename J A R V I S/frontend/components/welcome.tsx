import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface WelcomeProps {
  disabled: boolean;
  startButtonText: string;
  assistantName?: string;
  onStartCall: () => void;
}

export const Welcome = ({
  disabled,
  startButtonText,
  assistantName = 'Jarvis',
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeProps) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <section
      ref={ref}
      inert={disabled} // Note: React 19/Next 15 supports boolean 'inert'
      className={cn(
        'fixed inset-0 mx-auto flex h-svh flex-col items-center justify-center overflow-hidden bg-black text-center',
        disabled ? 'z-10' : 'z-20'
      )}
    >
      {/* Background Effects (Iron Man Theme) */}
      <div className="pointer-events-none absolute inset-0 z-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 via-black to-black opacity-80" />
      <div className="pointer-events-none absolute top-0 left-0 z-0 h-full w-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03]" />

      {/* Rotating HUD Rings */}
      <div className="pointer-events-none absolute top-1/2 left-1/2 z-0 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 animate-[spin_60s_linear_infinite] rounded-full border border-cyan-900/30" />
      <div className="pointer-events-none absolute top-1/2 left-1/2 z-0 h-[800px] w-[800px] -translate-x-1/2 -translate-y-1/2 animate-[spin_40s_linear_infinite_reverse] rounded-full border border-cyan-900/20" />

      {/* Content Container */}
      <div className="relative z-10 inline-block">
        {/* GIF Container */}
        <div className="relative">
          <Image
            src="/Jarvis.gif"
            alt={assistantName}
            width={800}
            height={450}
            unoptimized
            className="h-auto w-[800px] opacity-90 transition-opacity duration-500 hover:opacity-100"
          />
        </div>

        {/* Start Button */}
        <div className="absolute bottom-10 left-1/2 w-full max-w-xs -translate-x-1/2 transform">
          <Button
            variant="outline"
            size="lg"
            onClick={() => {
              const clickSound = new Audio('/button-click.m4a');
              clickSound.volume = 0.3;
              clickSound.play().catch(() => {});
              onStartCall();
            }}
            className="w-full border-cyan-500 bg-cyan-950/30 py-6 font-mono tracking-widest text-cyan-400 uppercase shadow-[0_0_20px_rgba(6,182,212,0.2)] backdrop-blur-md transition-all duration-300 hover:bg-cyan-500 hover:text-black hover:shadow-[0_0_30px_rgba(6,182,212,0.6)]"
          >
            {startButtonText}
          </Button>
        </div>
      </div>

      <footer className="pointer-events-none fixed bottom-5 left-0 z-20 flex w-full items-center justify-center">
        <div className="rounded-full border border-cyan-900/50 bg-black/50 px-4 py-2 backdrop-blur-md">
          <p className="text-[10px] tracking-[0.2em] text-cyan-700 uppercase">
            System Status: Online • <span className="text-cyan-400">Ready</span>
          </p>
        </div>
      </footer>

      {/* Corner Decorative Elements */}
      <div className="pointer-events-none fixed top-0 left-0 h-32 w-32 rounded-tl-3xl border-t-2 border-l-2 border-cyan-500/20" />
      <div className="pointer-events-none fixed top-0 right-0 h-32 w-32 rounded-tr-3xl border-t-2 border-r-2 border-cyan-500/20" />
      <div className="pointer-events-none fixed bottom-0 left-0 h-32 w-32 rounded-bl-3xl border-b-2 border-l-2 border-cyan-500/20" />
      <div className="pointer-events-none fixed right-0 bottom-0 h-32 w-32 rounded-br-3xl border-r-2 border-b-2 border-cyan-500/20" />
    </section>
  );
};
