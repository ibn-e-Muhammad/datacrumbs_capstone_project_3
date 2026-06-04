export function HowItWorks() {
  const steps = [
    {
      num: "01",
      title: "Listen & Analyze",
      description: "The AI agent parses the customer's query, identifying intent and extracting key entities like Order IDs.",
    },
    {
      num: "02",
      title: "Knowledge Retrieval",
      description: "For general queries, it searches the FAISS vector database to retrieve relevant company policies or product info.",
    },
    {
      num: "03",
      title: "Tool Execution",
      description: "For specific requests, it autonomously calls backend tools to fetch live data from Google Sheets.",
    },
    {
      num: "04",
      title: "Action & Respond",
      description: "It formulates a natural, helpful response or takes action like generating a refund ticket in your system.",
    }
  ];

  return (
    <section id="how-it-works" className="py-24 bg-gray-950 relative">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold font-outfit text-white mb-6">
            How the ReAct Loop Works
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Our agent doesn't just chat. It reasons, acts, and observes using advanced tool-calling architecture.
          </p>
        </div>

        <div className="space-y-12 relative">
          {/* Vertical connecting line */}
          <div className="absolute left-6 md:left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-violet-500/0 via-violet-500/50 to-violet-500/0 md:-translate-x-1/2 hidden sm:block" />

          {steps.map((step, idx) => (
            <div key={idx} className={`flex flex-col sm:flex-row gap-6 md:gap-12 items-start md:items-center ${idx % 2 !== 0 ? 'md:flex-row-reverse' : ''}`}>
              <div className="md:w-1/2 flex flex-col items-start md:items-end md:text-right">
                <div className={`glass-card p-6 rounded-2xl relative z-10 w-full ${idx % 2 !== 0 ? 'md:text-left' : 'md:text-right'}`}>
                  <h3 className="text-xl font-bold text-white mb-2 font-outfit">{step.title}</h3>
                  <p className="text-gray-400">{step.description}</p>
                </div>
              </div>
              <div className="hidden sm:flex absolute left-6 md:left-1/2 w-12 h-12 rounded-full bg-gray-950 border-2 border-violet-500 md:-translate-x-1/2 items-center justify-center z-20 font-bold text-violet-400 font-outfit shadow-[0_0_15px_rgba(139,92,246,0.3)]">
                {step.num}
              </div>
              <div className="md:w-1/2 hidden md:block" />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
