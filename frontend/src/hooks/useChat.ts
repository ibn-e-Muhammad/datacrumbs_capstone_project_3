import { useState, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import { ChatMessage, Message } from "@/types/chat";
import { sendChatMessage } from "@/lib/api";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addMessage = useCallback((role: Message["role"], content: string) => {
    const newMessage: ChatMessage = {
      id: uuidv4(),
      role,
      content,
      createdAt: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      // Add user message
      addMessage("user", content);
      setIsLoading(true);
      setError(null);

      try {
        const response = await sendChatMessage({
          message: content,
          conversation_id: conversationId,
        });

        if (response.conversation_id) {
          setConversationId(response.conversation_id);
        }

        // Add assistant message
        addMessage("assistant", response.reply);
      } catch (err) {
        console.error("Chat error:", err);
        setError("I'm sorry, I encountered an error connecting to our support system. Please try again later.");
        // Add error message as assistant response
        addMessage(
          "assistant",
          "I'm sorry, I encountered an error connecting to our support system. Please try again later."
        );
      } finally {
        setIsLoading(false);
      }
    },
    [messages, addMessage]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    addMessage,
    clearChat,
  };
}
