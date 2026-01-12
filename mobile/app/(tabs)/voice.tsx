/**
 * =============================================================================
 * (TABS)/VOICE.TSX - Voice Interaction Screen
 * =============================================================================
 * A.B.E.L. Project - Voice STT/TTS Interface (Phase 5)
 * =============================================================================
 */

import { View, Text, TouchableOpacity } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";

import { colors } from "@theme/colors";

export default function VoiceScreen() {
  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: colors.background.primary }}
      edges={["top"]}
    >
      {/* Header */}
      <View
        style={{
          paddingHorizontal: 16,
          paddingVertical: 12,
          borderBottomWidth: 1,
          borderBottomColor: colors.border.default,
        }}
      >
        <Text
          style={{
            color: colors.text.primary,
            fontSize: 24,
            fontWeight: "bold",
          }}
        >
          Voice
        </Text>
        <Text style={{ color: colors.text.secondary, fontSize: 14, marginTop: 4 }}>
          Parlez avec A.B.E.L.
        </Text>
      </View>

      {/* Content */}
      <View
        style={{
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          padding: 24,
        }}
      >
        {/* Mic Button */}
        <TouchableOpacity
          style={{
            width: 120,
            height: 120,
            borderRadius: 60,
            overflow: "hidden",
            marginBottom: 24,
          }}
        >
          <LinearGradient
            colors={[colors.neon.cyan, colors.neon.purple]}
            style={{
              width: "100%",
              height: "100%",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Ionicons name="mic" size={48} color={colors.background.primary} />
          </LinearGradient>
        </TouchableOpacity>

        <Text
          style={{
            color: colors.text.secondary,
            fontSize: 16,
            textAlign: "center",
          }}
        >
          Appuyez pour parler
        </Text>

        {/* Coming Soon Badge */}
        <View
          style={{
            marginTop: 40,
            paddingHorizontal: 16,
            paddingVertical: 8,
            backgroundColor: colors.background.card,
            borderRadius: 20,
            borderWidth: 1,
            borderColor: colors.neon.orange,
          }}
        >
          <Text style={{ color: colors.neon.orange, fontSize: 12 }}>
            Phase 5 - En développement
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
