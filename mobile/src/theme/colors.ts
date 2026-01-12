/**
 * =============================================================================
 * COLORS.TS - A.B.E.L. Cyberpunk Theme
 * =============================================================================
 * Dark cyberpunk color palette with neon accents
 * =============================================================================
 */

export const colors = {
  // Primary backgrounds
  background: {
    primary: "#0a0a0f",
    secondary: "#12121a",
    tertiary: "#1a1a25",
    card: "#15151f",
    overlay: "rgba(10, 10, 15, 0.95)",
  },

  // Neon accent colors
  neon: {
    cyan: "#00f0ff",
    cyanLight: "#66f7ff",
    cyanDark: "#00b8c4",
    magenta: "#ff00ff",
    magentaLight: "#ff66ff",
    purple: "#8b5cf6",
    green: "#00ff88",
    greenLight: "#66ffb3",
    orange: "#ff6600",
    red: "#ff3366",
    redLight: "#ff6688",
  },

  // Text colors
  text: {
    primary: "#ffffff",
    secondary: "#a0a0b0",
    muted: "#606070",
    accent: "#00f0ff",
    error: "#ff3366",
    success: "#00ff88",
    warning: "#ff6600",
  },

  // Border colors
  border: {
    default: "#2a2a35",
    light: "#3a3a45",
    focus: "#00f0ff",
    error: "#ff3366",
    success: "#00ff88",
  },

  // Status colors
  status: {
    online: "#00ff88",
    offline: "#606070",
    busy: "#ff6600",
    error: "#ff3366",
  },

  // Gradient presets
  gradients: {
    primary: ["#00f0ff", "#8b5cf6"],
    secondary: ["#ff00ff", "#ff6600"],
    dark: ["#0a0a0f", "#1a1a25"],
    card: ["#15151f", "#12121a"],
  },
} as const;

// Type for accessing colors
export type ColorKey = keyof typeof colors;
export type NeonColor = keyof typeof colors.neon;

// Helper function to get neon color with opacity
export const withOpacity = (color: string, opacity: number): string => {
  // Convert hex to rgba
  const hex = color.replace("#", "");
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

// Shadow presets for neon glow effects
export const shadows = {
  neonCyan: {
    shadowColor: colors.neon.cyan,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 10,
  },
  neonMagenta: {
    shadowColor: colors.neon.magenta,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 10,
  },
  neonGreen: {
    shadowColor: colors.neon.green,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 10,
  },
  card: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
};

export default colors;
