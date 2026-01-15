"use client";

import { Mail, ExternalLink } from "lucide-react";

export function EmailWidget() {
  // Mock email data
  const emails = [
    {
      id: 1,
      from: "john@example.com",
      subject: "Réunion demain",
      snippet: "N'oublie pas la réunion de demain à 10h...",
      time: "10:30",
      unread: true,
    },
    {
      id: 2,
      from: "newsletter@tech.com",
      subject: "Les news tech de la semaine",
      snippet: "Cette semaine dans le monde de la tech...",
      time: "09:15",
      unread: true,
    },
    {
      id: 3,
      from: "support@service.com",
      subject: "Votre ticket a été traité",
      snippet: "Nous avons résolu votre problème...",
      time: "Hier",
      unread: false,
    },
  ];

  return (
    <div className="card-cyber p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Mail className="w-5 h-5 text-primary" />
          <h3 className="font-semibold">Emails</h3>
          <span className="px-2 py-0.5 text-xs rounded-full bg-accent/20 text-accent">
            2 non lus
          </span>
        </div>
        <button className="text-muted-foreground hover:text-foreground">
          <ExternalLink className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-2">
        {emails.map((email) => (
          <div
            key={email.id}
            className={`p-2 rounded-lg cursor-pointer transition-colors ${
              email.unread
                ? "bg-primary/5 border border-primary/20 hover:bg-primary/10"
                : "bg-secondary/50 hover:bg-secondary"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium truncate max-w-[150px]">
                {email.from}
              </span>
              <span className="text-xs text-muted-foreground">{email.time}</span>
            </div>
            <div className="text-sm truncate">{email.subject}</div>
            <div className="text-xs text-muted-foreground truncate">
              {email.snippet}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
