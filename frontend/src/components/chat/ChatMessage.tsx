import { ChatMessage as ChatMessageType } from "@/types/chat";
import { Bot, User } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`flex max-w-[85%] ${
          isUser ? "flex-row-reverse" : "flex-row"
        } items-end gap-2`}
      >
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser
              ? "bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/20"
              : "bg-gray-800 border border-gray-700"
          }`}
        >
          {isUser ? (
            <User size={16} className="text-white" />
          ) : (
            <Bot size={16} className="text-violet-400" />
          )}
        </div>
        
        <div
          className={`px-4 py-3 text-sm ${
            isUser
              ? "bg-gradient-to-br from-violet-600 to-indigo-600 text-white rounded-2xl rounded-br-sm shadow-md"
              : "glass text-gray-100 rounded-2xl rounded-bl-sm"
          }`}
        >
          <div className="whitespace-pre-wrap">{message.content}</div>
          <div
            className={`text-[10px] mt-1.5 ${
              isUser ? "text-violet-200 text-right" : "text-gray-500 text-left"
            }`}
          >
            {message.createdAt.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
