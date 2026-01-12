/**
 * =============================================================================
 * (TABS)/_LAYOUT.TSX - Main Tab Navigation
 * =============================================================================
 * A.B.E.L. Project - Bottom tab navigation for main app
 * =============================================================================
 */

import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { View } from "react-native";

import { colors } from "@theme/colors";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.background.secondary,
          borderTopColor: colors.border.default,
          borderTopWidth: 1,
          height: 85,
          paddingBottom: 25,
          paddingTop: 10,
        },
        tabBarActiveTintColor: colors.neon.cyan,
        tabBarInactiveTintColor: colors.text.muted,
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: "500",
        },
      }}
    >
      {/* Chat Tab */}
      <Tabs.Screen
        name="index"
        options={{
          title: "Chat",
          tabBarIcon: ({ focused, color }) => (
            <View
              style={{
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Ionicons
                name={focused ? "chatbubbles" : "chatbubbles-outline"}
                size={24}
                color={color}
              />
              {focused && (
                <View
                  style={{
                    position: "absolute",
                    bottom: -8,
                    width: 4,
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: colors.neon.cyan,
                  }}
                />
              )}
            </View>
          ),
        }}
      />

      {/* Voice Tab */}
      <Tabs.Screen
        name="voice"
        options={{
          title: "Voice",
          tabBarIcon: ({ focused, color }) => (
            <View style={{ alignItems: "center", justifyContent: "center" }}>
              <Ionicons
                name={focused ? "mic" : "mic-outline"}
                size={24}
                color={color}
              />
              {focused && (
                <View
                  style={{
                    position: "absolute",
                    bottom: -8,
                    width: 4,
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: colors.neon.cyan,
                  }}
                />
              )}
            </View>
          ),
        }}
      />

      {/* Vision Tab */}
      <Tabs.Screen
        name="vision"
        options={{
          title: "Vision",
          tabBarIcon: ({ focused, color }) => (
            <View style={{ alignItems: "center", justifyContent: "center" }}>
              <Ionicons
                name={focused ? "eye" : "eye-outline"}
                size={24}
                color={color}
              />
              {focused && (
                <View
                  style={{
                    position: "absolute",
                    bottom: -8,
                    width: 4,
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: colors.neon.cyan,
                  }}
                />
              )}
            </View>
          ),
        }}
      />

      {/* Memory Tab */}
      <Tabs.Screen
        name="memory"
        options={{
          title: "Memory",
          tabBarIcon: ({ focused, color }) => (
            <View style={{ alignItems: "center", justifyContent: "center" }}>
              <Ionicons
                name={focused ? "hardware-chip" : "hardware-chip-outline"}
                size={24}
                color={color}
              />
              {focused && (
                <View
                  style={{
                    position: "absolute",
                    bottom: -8,
                    width: 4,
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: colors.neon.cyan,
                  }}
                />
              )}
            </View>
          ),
        }}
      />

      {/* Settings Tab */}
      <Tabs.Screen
        name="settings"
        options={{
          title: "Settings",
          tabBarIcon: ({ focused, color }) => (
            <View style={{ alignItems: "center", justifyContent: "center" }}>
              <Ionicons
                name={focused ? "settings" : "settings-outline"}
                size={24}
                color={color}
              />
              {focused && (
                <View
                  style={{
                    position: "absolute",
                    bottom: -8,
                    width: 4,
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: colors.neon.cyan,
                  }}
                />
              )}
            </View>
          ),
        }}
      />
    </Tabs>
  );
}
