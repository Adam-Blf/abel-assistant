"use client";

import {
  Zap,
  Mail,
  Calendar,
  Search,
  Mic,
  Twitter,
  RefreshCw,
} from "lucide-react";

export function QuickActionsWidget() {
  const actions = [
    {
      id: "check-emails",
      label: "Vérifier emails",
      icon: Mail,
      color: "primary",
    },
    {
      id: "check-calendar",
      label: "Événements",
      icon: Calendar,
      color: "accent",
    },
    {
      id: "search-apis",
      label: "Chercher API",
      icon: Search,
      color: "success",
    },
    {
      id: "voice-command",
      label: "Commande vocale",
      icon: Mic,
      color: "warning",
    },
    {
      id: "post-tweet",
      label: "Tweeter",
      icon: Twitter,
      color: "primary",
    },
    {
      id: "refresh-all",
      label: "Tout actualiser",
      icon: RefreshCw,
      color: "muted",
    },
  ];

  const getColorClass = (color: string) => {
    switch (color) {
      case "primary":
        return "bg-primary/10 text-primary border-primary/30 hover:bg-primary/20";
      case "accent":
        return "bg-accent/10 text-accent border-accent/30 hover:bg-accent/20";
      case "success":
        return "bg-success/10 text-success border-success/30 hover:bg-success/20";
      case "warning":
        return "bg-warning/10 text-warning border-warning/30 hover:bg-warning/20";
      default:
        return "bg-secondary text-muted-foreground border-border hover:bg-secondary/80";
    }
  };

  return (
    <div className="card-cyber p-4">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Actions Rapides</h3>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              className={`flex items-center gap-2 p-2.5 rounded-lg border transition-all ${getColorClass(
                action.color
              )}`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-xs font-medium">{action.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
