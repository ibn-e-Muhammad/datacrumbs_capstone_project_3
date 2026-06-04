import { Brain, Package, RefreshCw } from "lucide-react";

export function Features() {
  const features = [
    {
      title: "AI-Powered Answers",
      description: "Our RAG pipeline seamlessly ingests your company knowledge base to provide accurate, instant answers to complex customer questions.",
      icon: <Brain size={24} className="text-violet-400" />,
    },
    {
      title: "Live Order Tracking",
      description: "Securely connects to your backend systems to look up order status in real-time, giving customers peace of mind without human intervention.",
      icon: <Package size={24} className="text-indigo-400" />,
    },
    {
      title: "Automated Refunds",
      description: "Verifies eligibility, collects required information, and automatically generates support tickets in your existing systems.",
      icon: <RefreshCw size={24} className="text-fuchsia-400" />,
    },
  ];

  return (
    <section id="features" className="py-24 bg-gray-950 relative border-t border-gray-900">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
        <div className="text-center mb-16 max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-5xl font-bold font-outfit text-white mb-6">
            Intelligent automation <br/>for modern commerce
          </h2>
          <p className="text-gray-400 text-lg">
            Built on advanced LLMs and precise tool calling, the ACME agent goes beyond simple chatbots to actually solve customer problems.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div 
              key={idx} 
              className="glass-card rounded-3xl p-8 hover:bg-gray-800/50 transition-colors border border-gray-800 hover:border-gray-700 group relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="w-12 h-12 rounded-xl bg-gray-950 border border-gray-800 flex items-center justify-center mb-6 relative z-10">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold font-outfit text-white mb-3 relative z-10">{feature.title}</h3>
              <p className="text-gray-400 relative z-10 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
