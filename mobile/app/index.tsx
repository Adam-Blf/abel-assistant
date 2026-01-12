/**
 * =============================================================================
 * INDEX.TSX - Entry Point / Auth Router
 * =============================================================================
 * A.B.E.L. Project - Redirects based on auth state
 * =============================================================================
 */

import { useEffect } from "react";
import { View, Text, ActivityIndicator } from "react-native";
import { Redirect } from "expo-router";

import { useAuth } from "@contexts/AuthContext";
import { colors } from "@theme/colors";

export default function Index() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading screen while checking auth
  if (isLoading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: colors.background.primary,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Text
          style={{
            color: colors.neon.cyan,
            fontSize: 32,
            fontWeight: "bold",
            marginBottom: 20,
          }}
        >
          A.B.E.L.
        </Text>
        <ActivityIndicator size="large" color={colors.neon.cyan} />
        <Text
          style={{
            color: colors.text.secondary,
            fontSize: 14,
            marginTop: 16,
          }}
        >
          Initialisation...
        </Text>
      </View>
    );
  }

  // Redirect based on auth state
  if (isAuthenticated) {
    return <Redirect href="/(tabs)" />;
  }

  return <Redirect href="/(auth)/login" />;
}
