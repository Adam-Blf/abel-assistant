import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // A.B.E.L Cyberpunk Theme
        background: "#050505",
        foreground: "#FAFAFA",
        primary: {
          DEFAULT: "#00F0FF",
          foreground: "#050505",
        },
        secondary: {
          DEFAULT: "#1A1A2E",
          foreground: "#FAFAFA",
        },
        accent: {
          DEFAULT: "#FF006E",
          foreground: "#FAFAFA",
        },
        muted: {
          DEFAULT: "#16161A",
          foreground: "#A0A0A0",
        },
        card: {
          DEFAULT: "#0A0A0F",
          foreground: "#FAFAFA",
        },
        border: "#2A2A3E",
        input: "#1A1A2E",
        ring: "#00F0FF",
        destructive: {
          DEFAULT: "#FF4444",
          foreground: "#FAFAFA",
        },
        success: {
          DEFAULT: "#00FF88",
          foreground: "#050505",
        },
        warning: {
          DEFAULT: "#FFB800",
          foreground: "#050505",
        },
        cyan: {
          50: "#E0FFFF",
          100: "#B3FFFF",
          200: "#80FFFF",
          300: "#4DFFFF",
          400: "#1AFFFF",
          500: "#00F0FF",
          600: "#00C4CC",
          700: "#009999",
          800: "#006D66",
          900: "#004D4D",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": {
            boxShadow: "0 0 5px #00F0FF, 0 0 10px #00F0FF, 0 0 15px #00F0FF",
          },
          "50%": {
            boxShadow: "0 0 10px #00F0FF, 0 0 20px #00F0FF, 0 0 30px #00F0FF",
          },
        },
        "scan-line": {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(0)" },
        },
      },
      animation: {
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "scan-line": "scan-line 8s linear infinite",
        "fade-in": "fade-in 0.3s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
      },
      backgroundImage: {
        "grid-pattern": `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300F0FF' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
