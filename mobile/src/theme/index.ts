/**
 * =============================================================================
 * THEME INDEX - A.B.E.L. Theme Exports
 * =============================================================================
 */

export { colors, shadows, withOpacity } from "./colors";
export type { ColorKey, NeonColor } from "./colors";

// Spacing scale
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  "2xl": 48,
  "3xl": 64,
} as const;

// Border radius scale
export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  "2xl": 24,
  full: 9999,
} as const;

// Font sizes
export const fontSize = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  "2xl": 24,
  "3xl": 30,
  "4xl": 36,
} as const;

// Animation durations
export const duration = {
  fast: 150,
  normal: 300,
  slow: 500,
} as const;
