import { motion } from "framer-motion";

interface QuickActionsProps {
  onSelect: (action: string) => void;
}

export function QuickActions({ onSelect }: QuickActionsProps) {
  const actions = [
    "Track My Order",
    "Refund Policy",
    "Shipping Info",
    "Contact Support",
  ];

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {actions.map((action, index) => (
        <motion.button
          key={action}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          onClick={() => onSelect(action)}
          className="text-xs font-medium px-3 py-1.5 rounded-full border border-violet-500/30 text-violet-300 bg-violet-500/10 hover:bg-violet-500/20 hover:border-violet-500/50 transition-colors"
        >
          {action}
        </motion.button>
      ))}
    </div>
  );
}
