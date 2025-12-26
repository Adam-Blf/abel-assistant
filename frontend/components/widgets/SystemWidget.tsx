"use client";

import { useState, useEffect } from "react";
import { Cpu, HardDrive, Wifi, Database, Server } from "lucide-react";

interface ServiceStatus {
  name: string;
  status: "healthy" | "unhealthy" | "unknown";
  latency?: number;
}

export function SystemWidget() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: "API", status: "unknown" },
    { name: "Database", status: "unknown" },
    { name: "Redis", status: "unknown" },
    { name: "Qdrant", status: "unknown" },
  ]);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/health/detailed`
        );
        if (res.ok) {
          const data = await res.json();
          const serviceList: ServiceStatus[] = Object.entries(
            data.services || {}
          ).map(([name, info]: [string, any]) => ({
            name: name.charAt(0).toUpperCase() + name.slice(1),
            status: info.status === "healthy" ? "healthy" : "unhealthy",
            latency: info.latency_ms,
          }));
          setServices(serviceList);
        }
      } catch {
        setServices((prev) =>
          prev.map((s) => ({ ...s, status: "unhealthy" as const }))
        );
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-success";
      case "unhealthy":
        return "text-destructive";
      default:
        return "text-warning";
    }
  };

  const getStatusIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case "api":
        return Server;
      case "database":
        return Database;
      case "redis":
        return HardDrive;
      case "qdrant":
        return Cpu;
      default:
        return Wifi;
    }
  };

  return (
    <div className="card-cyber p-4">
      <div className="flex items-center gap-2 mb-4">
        <Cpu className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Système</h3>
      </div>

      <div className="space-y-3">
        {services.map((service) => {
          const Icon = getStatusIcon(service.name);
          return (
            <div
              key={service.name}
              className="flex items-center justify-between p-2 rounded-lg bg-secondary/50"
            >
              <div className="flex items-center gap-2">
                <Icon className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm">{service.name}</span>
              </div>
              <div className="flex items-center gap-2">
                {service.latency !== undefined && (
                  <span className="text-xs text-muted-foreground">
                    {service.latency.toFixed(0)}ms
                  </span>
                )}
                <div
                  className={`w-2 h-2 rounded-full ${
                    service.status === "healthy"
                      ? "bg-success"
                      : service.status === "unhealthy"
                      ? "bg-destructive"
                      : "bg-warning"
                  }`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
