"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  MessageSquare,
  LayoutGrid,
  Settings,
  Mail,
  Calendar,
  Twitter,
  Instagram,
  Globe,
  Mic,
  ChevronLeft,
  ChevronRight,
  Cpu,
} from "lucide-react";

interface SidebarProps {
  activeTab: "chat" | "widgets";
  onTabChange: (tab: "chat" | "widgets") => void;
}

const menuItems = [
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "widgets", label: "Dashboard", icon: LayoutGrid },
];

const quickActions = [
  { id: "email", label: "Emails", icon: Mail },
  { id: "calendar", label: "Calendrier", icon: Calendar },
  { id: "twitter", label: "Twitter", icon: Twitter },
  { id: "instagram", label: "Instagram", icon: Instagram },
  { id: "apis", label: "APIs", icon: Globe },
  { id: "voice", label: "Voix", icon: Mic },
];

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <motion.aside
      initial={false}
      animate={{ width: isCollapsed ? 64 : 240 }}
      className="relative h-full bg-card border-r border-border flex flex-col"
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-border">
        <motion.div
          animate={{ scale: isCollapsed ? 0.8 : 1 }}
          className="flex items-center gap-2"
        >
          <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/50 flex items-center justify-center">
            <Cpu className="w-6 h-6 text-primary" />
          </div>
          {!isCollapsed && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="font-bold text-xl text-gradient"
            >
              A.B.E.L
            </motion.span>
          )}
        </motion.div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-3 space-y-2">
        <div className="mb-4">
          {!isCollapsed && (
            <span className="text-xs uppercase text-muted-foreground px-3">
              Navigation
            </span>
          )}
        </div>

        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id as "chat" | "widgets")}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                transition-all duration-200
                ${
                  isActive
                    ? "bg-primary/20 text-primary border border-primary/30"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                }
              `}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="font-medium"
                >
                  {item.label}
                </motion.span>
              )}
            </button>
          );
        })}

        {/* Quick Actions */}
        <div className="pt-6">
          {!isCollapsed && (
            <span className="text-xs uppercase text-muted-foreground px-3">
              Actions Rapides
            </span>
          )}
          <div className="mt-3 space-y-1">
            {quickActions.map((action) => {
              const Icon = action.icon;

              return (
                <button
                  key={action.id}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg
                    text-muted-foreground hover:bg-secondary hover:text-foreground
                    transition-all duration-200"
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  {!isCollapsed && (
                    <span className="text-sm">{action.label}</span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Settings */}
      <div className="p-3 border-t border-border">
        <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-all duration-200">
          <Settings className="w-5 h-5" />
          {!isCollapsed && <span>Paramètres</span>}
        </button>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-border border border-border flex items-center justify-center hover:bg-primary hover:text-primary-foreground transition-colors"
      >
        {isCollapsed ? (
          <ChevronRight className="w-4 h-4" />
        ) : (
          <ChevronLeft className="w-4 h-4" />
        )}
      </button>
    </motion.aside>
  );
}
