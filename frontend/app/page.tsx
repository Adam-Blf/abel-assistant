"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Sidebar } from "@/components/layout/Sidebar";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { WidgetGrid } from "@/components/widgets/WidgetGrid";
import { StatusBar } from "@/components/layout/StatusBar";

export default function Dashboard() {
  const [isOnline, setIsOnline] = useState(false);
  const [activeTab, setActiveTab] = useState<"chat" | "widgets">("chat");

  useEffect(() => {
    // Check API health
    const checkHealth = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
        setIsOnline(res.ok);
      } catch {
        setIsOnline(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Status Bar */}
        <StatusBar isOnline={isOnline} />

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="h-full"
          >
            {activeTab === "chat" ? <ChatPanel /> : <WidgetGrid />}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
