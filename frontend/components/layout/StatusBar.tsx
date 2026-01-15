"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Cpu,
  HardDrive,
  Wifi,
  WifiOff,
  Clock,
  Thermometer,
} from "lucide-react";

interface StatusBarProps {
  isOnline: boolean;
}

export function StatusBar({ isOnline }: StatusBarProps) {
  const [time, setTime] = useState(new Date());
  const [cpuUsage, setCpuUsage] = useState(0);
  const [memUsage, setMemUsage] = useState(0);

  useEffect(() => {
    // Update clock
    const timer = setInterval(() => setTime(new Date()), 1000);

    // Simulate system metrics
    const metrics = setInterval(() => {
      setCpuUsage(Math.random() * 30 + 10);
      setMemUsage(Math.random() * 20 + 40);
    }, 5000);

    return () => {
      clearInterval(timer);
      clearInterval(metrics);
    };
  }, []);

  return (
    <header className="h-12 bg-card/80 backdrop-blur-sm border-b border-border flex items-center justify-between px-4">
      {/* Left: Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          {isOnline ? (
            <>
              <Wifi className="w-4 h-4 text-success" />
              <span className="text-sm text-success">ONLINE</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-destructive" />
              <span className="text-sm text-destructive">OFFLINE</span>
            </>
          )}
        </div>

        <div className="h-4 w-px bg-border" />

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-4 text-sm text-muted-foreground"
        >
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5" />
            <span>{cpuUsage.toFixed(1)}%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <HardDrive className="w-3.5 h-3.5" />
            <span>{memUsage.toFixed(1)}%</span>
          </div>
        </motion.div>
      </div>

      {/* Center: Title */}
      <div className="absolute left-1/2 -translate-x-1/2">
        <h1 className="text-sm font-medium text-muted-foreground tracking-wider uppercase">
          Command Center
        </h1>
      </div>

      {/* Right: Time */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <Thermometer className="w-3.5 h-3.5" />
          <span>23°C</span>
        </div>

        <div className="h-4 w-px bg-border" />

        <div className="flex items-center gap-1.5 text-sm font-mono">
          <Clock className="w-3.5 h-3.5 text-primary" />
          <span className="text-foreground">
            {time.toLocaleTimeString("fr-FR", {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
            })}
          </span>
        </div>
      </div>
    </header>
  );
}
