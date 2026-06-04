"use client";

import { BotMessageSquare, Sparkles } from "lucide-react";

export function Hero() {
  return (
    <section className="relative flex min-h-[90vh] flex-col items-center justify-center overflow-hidden bg-gray-950 px-4 text-center pt-20">
      <div className="absolute inset-0 bg-gradient-to-b from-violet-900/20 via-gray-950 to-gray-950" />
      <div className="pointer-events-none absolute top-1/4 left-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-600/20 blur-3xl" />
      
      <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center">
        <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm font-medium text-violet-300 animate-fade-in-up">
          <Sparkles size={14} className="text-violet-400" />
          <span>Next-Generation AI Customer Support</span>
        </div>
        
        <h1 className="mb-6 text-5xl font-extrabold tracking-tight text-white md:text-7xl lg:text-8xl font-outfit animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          Support that never <br />
          <span className="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-indigo-400 bg-clip-text text-transparent">
            sleeps.
          </span>
        </h1>
        
        <p className="mx-auto mb-10 max-w-2xl text-lg md:text-xl text-gray-400 font-inter animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          Your customers hate waiting. Our AI agent instantly resolves queries, tracks orders, and processes refunds 24/7—freeing your human team for complex issues.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
          <button 
            onClick={() => window.dispatchEvent(new Event("open-chat"))}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-violet-600 text-white font-medium hover:bg-violet-500 transition-all shadow-lg shadow-violet-600/20 flex items-center justify-center gap-2"
          >
            <BotMessageSquare size={18} />
            Try the AI Agent
          </button>
          <button className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gray-900 border border-gray-700 text-gray-300 font-medium hover:bg-gray-800 hover:text-white transition-all">
            View Documentation
          </button>
        </div>
        
        <p className="mt-6 text-sm text-gray-500 font-medium animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
          Used by 2,000+ forward-thinking teams.
        </p>
      </div>
    </section>
  );
}
