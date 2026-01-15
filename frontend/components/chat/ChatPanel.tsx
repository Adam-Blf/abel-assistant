"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Mic,
  MicOff,
  Loader2,
  Bot,
  User,
  Sparkles,
} from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Salut! Je suis A.B.E.L, ton assistant personnel. Comment puis-je t'aider aujourd'hui?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/quick?message=${encodeURIComponent(userMessage.content)}`, {
        method: "POST",
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error("API error");
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Désolé, je ne peux pas répondre pour le moment. Vérifie que le backend est en ligne.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-border flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center">
          <Bot className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="font-semibold">A.B.E.L</h2>
          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <span className="status-online" />
            Prêt à t'aider
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex gap-3 ${
                message.role === "user" ? "flex-row-reverse" : ""
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === "user"
                    ? "bg-accent/20 border border-accent/50"
                    : "bg-primary/20 border border-primary/50"
                }`}
              >
                {message.role === "user" ? (
                  <User className="w-4 h-4 text-accent" />
                ) : (
                  <Sparkles className="w-4 h-4 text-primary" />
                )}
              </div>
              <div
                className={`max-w-[70%] rounded-2xl px-4 py-2.5 ${
                  message.role === "user"
                    ? "bg-accent/20 border border-accent/30"
                    : "bg-secondary border border-border"
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>
                <span className="text-xs text-muted-foreground mt-1 block">
                  {message.timestamp.toLocaleTimeString("fr-FR", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center">
              <Loader2 className="w-4 h-4 text-primary animate-spin" />
            </div>
            <div className="bg-secondary border border-border rounded-2xl px-4 py-2.5">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-75" />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-150" />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsListening(!isListening)}
            className={`p-3 rounded-xl transition-all ${
              isListening
                ? "bg-accent text-accent-foreground animate-pulse-glow"
                : "bg-secondary text-muted-foreground hover:text-foreground"
            }`}
          >
            {isListening ? (
              <MicOff className="w-5 h-5" />
            ) : (
              <Mic className="w-5 h-5" />
            )}
          </button>

          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Écris ton message..."
              rows={1}
              className="w-full bg-secondary border border-border rounded-xl px-4 py-3 pr-12
                resize-none focus:outline-none focus:ring-2 focus:ring-primary/50
                placeholder:text-muted-foreground"
            />
          </div>

          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="p-3 rounded-xl bg-primary text-primary-foreground
              disabled:opacity-50 disabled:cursor-not-allowed
              hover:glow-cyan transition-all"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
