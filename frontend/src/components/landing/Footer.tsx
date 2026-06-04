import { Mountain } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-gray-950 border-t border-gray-900 pt-16 pb-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
          <div className="col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 rounded-lg bg-gray-800 flex items-center justify-center text-gray-400">
                <Mountain size={18} />
              </div>
              <span className="font-outfit font-bold text-lg tracking-wide text-white">ACME</span>
            </div>
            <p className="text-gray-500 max-w-sm">
              Empowering modern e-commerce teams with intelligent automation and 24/7 autonomous customer support.
            </p>
          </div>
          
          <div>
            <h4 className="font-bold text-white mb-4">Product</h4>
            <ul className="space-y-3 text-gray-500 text-sm">
              <li><a href="#" className="hover:text-violet-400 transition-colors">Features</a></li>
              <li><a href="#" className="hover:text-violet-400 transition-colors">Integrations</a></li>
              <li><a href="#" className="hover:text-violet-400 transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-violet-400 transition-colors">Changelog</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-bold text-white mb-4">Support</h4>
            <ul className="space-y-3 text-gray-500 text-sm">
              <li><a href="#" className="hover:text-violet-400 transition-colors">Documentation</a></li>
              <li><a href="#" className="hover:text-violet-400 transition-colors">API Reference</a></li>
              <li><a href="#" className="hover:text-violet-400 transition-colors">Community</a></li>
              <li><a href="#" className="hover:text-violet-400 transition-colors">Contact Sales</a></li>
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-gray-900 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-600">
          <p>© {new Date().getFullYear()} ACME Corporation. All rights reserved.</p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-gray-300">Privacy Policy</a>
            <a href="#" className="hover:text-gray-300">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
