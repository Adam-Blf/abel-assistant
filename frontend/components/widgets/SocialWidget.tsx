"use client";

import { useState } from "react";
import { MessageCircle, Send, AlertCircle } from "lucide-react";

interface PendingMessage {
  id: number;
  platform: "instagram" | "twitter";
  from: string;
  message: string;
  tone: string;
  suggestedResponse: string;
}

export function SocialWidget() {
  const [directive, setDirective] = useState("");

  // Mock pending messages
  const pendingMessages: PendingMessage[] = [
    {
      id: 1,
      platform: "instagram",
      from: "@user123",
      message: "Salut! Tu fais quoi ce weekend?",
      tone: "Amical",
      suggestedResponse: "Hey! Pas grand chose, pourquoi?",
    },
  ];

  return (
    <div className="card-cyber p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-primary" />
          <h3 className="font-semibold">Social</h3>
        </div>
        {pendingMessages.length > 0 && (
          <span className="px-2 py-0.5 text-xs rounded-full bg-warning/20 text-warning flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            En attente
          </span>
        )}
      </div>

      {pendingMessages.length > 0 ? (
        <div className="space-y-3">
          {pendingMessages.map((msg) => (
            <div key={msg.id} className="p-3 rounded-lg bg-secondary/50 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{msg.from}</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">
                  {msg.tone}
                </span>
              </div>

              <div className="text-sm text-muted-foreground italic">
                "{msg.message}"
              </div>

              <div className="text-xs text-muted-foreground">
                Suggestion: {msg.suggestedResponse}
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={directive}
                  onChange={(e) => setDirective(e.target.value)}
                  placeholder="Ta directive..."
                  className="flex-1 text-sm bg-background border border-border rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-primary"
                />
                <button className="p-1.5 rounded bg-primary text-primary-foreground hover:glow-cyan transition-all">
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6 text-muted-foreground">
          <MessageCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">Aucun message en attente</p>
        </div>
      )}
    </div>
  );
}
