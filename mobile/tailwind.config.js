/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        // Cyberpunk Dark Theme - A.B.E.L.
        abel: {
          // Primary backgrounds
          bg: {
            primary: "#0a0a0f",
            secondary: "#12121a",
            tertiary: "#1a1a25",
            card: "#15151f",
          },
          // Neon accent colors
          neon: {
            cyan: "#00f0ff",
            magenta: "#ff00ff",
            purple: "#8b5cf6",
            green: "#00ff88",
            orange: "#ff6600",
            red: "#ff3366",
          },
          // Text colors
          text: {
            primary: "#ffffff",
            secondary: "#a0a0b0",
            muted: "#606070",
            accent: "#00f0ff",
          },
          // Border colors
          border: {
            default: "#2a2a35",
            focus: "#00f0ff",
            error: "#ff3366",
          },
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        "neon-cyan": "0 0 20px rgba(0, 240, 255, 0.3)",
        "neon-magenta": "0 0 20px rgba(255, 0, 255, 0.3)",
        "neon-green": "0 0 20px rgba(0, 255, 136, 0.3)",
      },
      animation: {
        "pulse-neon": "pulse-neon 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        "pulse-neon": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.5 },
        },
        "glow": {
          "from": { boxShadow: "0 0 10px #00f0ff, 0 0 20px #00f0ff" },
          "to": { boxShadow: "0 0 20px #00f0ff, 0 0 40px #00f0ff" },
        },
      },
    },
  },
  plugins: [],
};
