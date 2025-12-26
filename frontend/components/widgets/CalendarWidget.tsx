"use client";

import { Calendar, Clock, MapPin } from "lucide-react";

export function CalendarWidget() {
  // Mock calendar data
  const events = [
    {
      id: 1,
      title: "Standup quotidien",
      time: "09:00",
      duration: "15 min",
      location: "Google Meet",
      color: "primary",
    },
    {
      id: 2,
      title: "Review de code",
      time: "14:00",
      duration: "1h",
      location: "Salle B",
      color: "accent",
    },
    {
      id: 3,
      title: "1:1 avec Manager",
      time: "16:30",
      duration: "30 min",
      location: "Bureau 3",
      color: "success",
    },
  ];

  const today = new Date().toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  return (
    <div className="card-cyber p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-primary" />
          <h3 className="font-semibold">Aujourd'hui</h3>
        </div>
        <span className="text-xs text-muted-foreground capitalize">{today}</span>
      </div>

      <div className="space-y-2">
        {events.map((event) => (
          <div
            key={event.id}
            className="p-2 rounded-lg bg-secondary/50 border-l-2"
            style={{
              borderColor:
                event.color === "primary"
                  ? "var(--primary)"
                  : event.color === "accent"
                  ? "var(--accent)"
                  : "var(--success)",
            }}
          >
            <div className="font-medium text-sm">{event.title}</div>
            <div className="flex items-center gap-3 mt-1">
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                {event.time} · {event.duration}
              </div>
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <MapPin className="w-3 h-3" />
                {event.location}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
