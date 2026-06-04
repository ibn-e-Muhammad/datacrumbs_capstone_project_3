import Link from "next/link";
import { Mountain } from "lucide-react";

export function Navbar() {
  return (
    <nav className="fixed top-0 w-full z-40 glass border-b border-gray-800/50 backdrop-blur-xl bg-gray-950/70">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40 transition-shadow">
            <Mountain size={18} />
          </div>
          <span className="font-outfit font-bold text-lg tracking-wide text-white">ACME</span>
        </Link>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-300">
          <Link href="#features" className="hover:text-white transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-white transition-colors">How it Works</Link>
          <Link href="#testimonials" className="hover:text-white transition-colors">Testimonials</Link>
        </div>
        
        <div className="flex items-center gap-4">
          <button className="text-sm font-medium text-gray-300 hover:text-white transition-colors hidden sm:block">
            Sign In
          </button>
          <button className="text-sm font-medium px-4 py-2 bg-white text-gray-950 hover:bg-gray-200 rounded-lg transition-colors">
            Get Started
          </button>
        </div>
      </div>
    </nav>
  );
}
