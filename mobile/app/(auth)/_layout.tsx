/**
 * =============================================================================
 * (AUTH)/_LAYOUT.TSX - Auth Stack Layout
 * =============================================================================
 * A.B.E.L. Project - Layout for authentication screens
 * =============================================================================
 */

import { Stack } from "expo-router";
import { colors } from "@theme/colors";

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: {
          backgroundColor: colors.background.primary,
        },
        animation: "fade",
      }}
    >
      <Stack.Screen name="login" />
      <Stack.Screen name="register" />
    </Stack>
  );
}
