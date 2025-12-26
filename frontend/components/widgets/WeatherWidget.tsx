"use client";

import { Cloud, Sun, CloudRain, Thermometer } from "lucide-react";

export function WeatherWidget() {
  // Mock weather data
  const weather = {
    temp: 12,
    condition: "Nuageux",
    humidity: 75,
    wind: 15,
    location: "Paris",
  };

  return (
    <div className="card-cyber p-4">
      <div className="flex items-center gap-2 mb-4">
        <Cloud className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Météo</h3>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <div className="text-4xl font-bold text-gradient">
            {weather.temp}°C
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {weather.condition}
          </div>
          <div className="text-xs text-muted-foreground">{weather.location}</div>
        </div>

        <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/30 flex items-center justify-center">
          <Cloud className="w-8 h-8 text-primary" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 mt-4">
        <div className="p-2 rounded-lg bg-secondary/50 text-center">
          <div className="text-xs text-muted-foreground">Humidité</div>
          <div className="font-semibold">{weather.humidity}%</div>
        </div>
        <div className="p-2 rounded-lg bg-secondary/50 text-center">
          <div className="text-xs text-muted-foreground">Vent</div>
          <div className="font-semibold">{weather.wind} km/h</div>
        </div>
      </div>
    </div>
  );
}
