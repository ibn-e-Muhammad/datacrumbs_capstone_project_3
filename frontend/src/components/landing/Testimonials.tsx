export function Testimonials() {
  const testimonials = [
    {
      quote: "The ACME AI Agent reduced our support ticket volume by 45% in the first month. It handles all the repetitive 'where is my order' queries flawlessly.",
      author: "Sarah Jenkins",
      role: "VP of Customer Success, TechRetail",
    },
    {
      quote: "We were worried about an AI hallucinating policies, but the RAG implementation ensures it only uses our official documentation. Incredible accuracy.",
      author: "David Chen",
      role: "Operations Director, StyleStore",
    },
    {
      quote: "The ability for the agent to actually take action—like creating refund tickets—is what sets this apart from basic chatbots. It's a real digital worker.",
      author: "Elena Rodriguez",
      role: "Founder, Bloom & Grow",
    }
  ];

  return (
    <section id="testimonials" className="py-24 bg-gray-900 border-t border-gray-800">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold font-outfit text-white mb-6">
            Loved by support teams
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((t, idx) => (
            <div key={idx} className="glass-card p-8 rounded-3xl flex flex-col justify-between">
              <div>
                <div className="flex gap-1 mb-6 text-yellow-500">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 fill-current" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-300 text-lg mb-8 italic">"{t.quote}"</p>
              </div>
              
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${
                  idx === 0 ? 'from-pink-500 to-orange-400' : 
                  idx === 1 ? 'from-blue-500 to-cyan-400' : 
                  'from-emerald-500 to-teal-400'
                }`} />
                <div>
                  <div className="font-bold text-white">{t.author}</div>
                  <div className="text-sm text-gray-500">{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
