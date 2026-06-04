"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { useChat } from "@/hooks/useChat";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";
import { QuickActions } from "./QuickActions";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [hasOpened, setHasOpened] = useState(false);
  const { messages, isLoading, error, sendMessage, addMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Welcome message on first open
  useEffect(() => {
    if (isOpen && !hasOpened) {
      setHasOpened(true);
      // Small delay to simulate connection
      setTimeout(() => {
        addMessage(
          "assistant",
          "👋 Hi there! I'm ACME's AI customer support assistant.\n\nI can help you track orders, request refunds, or answer questions about our products and policies. How can I assist you today?"
        );
      }, 600);
    }
  }, [isOpen, hasOpened, addMessage]);

  const handleQuickAction = (action: string) => {
    let message = "";
    switch (action) {
      case "Track My Order":
        message = "I'd like to track my order.";
        break;
      case "Refund Policy":
        message = "What is your refund policy?";
        break;
      case "Shipping Info":
        message = "How long does shipping take?";
        break;
      case "Contact Support":
        message = "How can I contact human support?";
        break;
      default:
        message = action;
    }
    sendMessage(message);
  };

  return (
    <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute bottom-20 right-0 w-[90vw] sm:w-[400px] h-[75vh] sm:h-[600px] max-h-[800px] glass rounded-2xl shadow-2xl flex flex-col overflow-hidden ring-1 ring-white/10"
          >
            {/* Header */}
            <div className="bg-gray-950 p-4 border-b border-gray-800 flex justify-between items-center z-10 shadow-sm relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-violet-900/20 to-indigo-900/20 pointer-events-none" />
              <div className="flex items-center gap-3 relative z-10">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-inner shadow-white/20">
                    <span className="font-outfit font-bold text-white text-lg">A</span>
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-gray-950 shadow-sm" />
                </div>
                <div>
                  <h3 className="font-outfit font-semibold text-white tracking-wide text-sm">ACME Support</h3>
                  <p className="text-xs text-violet-300 font-medium flex items-center gap-1">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500"></span>
                    </span>
                    AI Assistant Online
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-8 h-8 rounded-full bg-gray-900 border border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800 hover:border-gray-600 transition-colors flex items-center justify-center relative z-10"
                aria-label="Close chat"
              >
                <X size={18} />
              </button>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 chat-scroll flex flex-col relative bg-gray-950/50">
              <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.02] pointer-events-none mix-blend-overlay"></div>
              
              {messages.length === 1 && (
                <div className="mt-auto mb-4">
                  <QuickActions onSelect={handleQuickAction} />
                </div>
              )}
              
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              
              {isLoading && (
                <div className="mb-4">
                  <TypingIndicator />
                </div>
              )}
              
              {error && (
                <div className="mx-auto my-2 px-3 py-1.5 bg-red-950/50 border border-red-900/50 rounded-full text-xs text-red-400 font-medium">
                  Connection Error
                </div>
              )}
              
              <div ref={messagesEndRef} className="h-1" />
            </div>

            {/* Input Area */}
            <ChatInput onSend={sendMessage} disabled={isLoading} />
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="w-14 h-14 bg-violet-600 hover:bg-violet-500 text-white rounded-full shadow-xl shadow-violet-900/50 flex items-center justify-center transition-colors relative z-50 overflow-hidden group border border-violet-400/30"
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        {isOpen ? <X size={24} className="relative z-10" /> : <MessageCircle size={24} className="relative z-10" />}
      </motion.button>
    </div>
  );
}
