import { useState, useRef, useEffect } from "react";
import { SendHorizontal } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (!input.trim() || disabled) return;
    onSend(input);
    setInput("");
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // Auto-resize
    const textarea = e.target;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  };

  // Focus on mount
  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  return (
    <div className="p-4 border-t border-gray-800 bg-gray-950/80 rounded-b-2xl">
      <div className="flex items-end gap-2 bg-gray-900 border border-gray-700 focus-within:border-violet-500 focus-within:ring-1 focus-within:ring-violet-500/50 rounded-xl p-1 pl-3 transition-all duration-200 shadow-inner">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={disabled ? "Connecting..." : "Type your message..."}
          className="flex-1 max-h-[120px] bg-transparent text-sm text-gray-100 placeholder:text-gray-500 py-2.5 resize-none focus:outline-none chat-scroll"
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || disabled}
          className={`p-2 rounded-lg flex-shrink-0 transition-colors mb-0.5 mr-0.5 ${
            input.trim() && !disabled
              ? "bg-violet-600 text-white hover:bg-violet-500 shadow-md shadow-violet-900/50"
              : "bg-gray-800 text-gray-500"
          }`}
          aria-label="Send message"
        >
          <SendHorizontal size={18} className={input.trim() && !disabled ? "translate-x-[-1px]" : ""} />
        </button>
      </div>
      <div className="text-center mt-2">
        <span className="text-[10px] text-gray-500">
          Press <kbd className="font-sans px-1 py-0.5 rounded bg-gray-800 border border-gray-700">Enter</kbd> to send
        </span>
      </div>
    </div>
  );
}
