/**
 * =============================================================================
 * (TABS)/VISION.TSX - Vision AI Screen
 * =============================================================================
 * A.B.E.L. Project - Image Analysis Interface (Phase 6)
 * =============================================================================
 */

import { View, Text, TouchableOpacity } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";

import { colors } from "@theme/colors";

export default function VisionScreen() {
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
          Vision
        </Text>
        <Text style={{ color: colors.text.secondary, fontSize: 14, marginTop: 4 }}>
          Analyse d'images avec Gemini
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
        {/* Camera Button */}
        <TouchableOpacity
          style={{
            width: 120,
            height: 120,
            borderRadius: 20,
            overflow: "hidden",
            marginBottom: 24,
          }}
        >
          <LinearGradient
            colors={[colors.neon.magenta, colors.neon.orange]}
            style={{
              width: "100%",
              height: "100%",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Ionicons name="camera" size={48} color={colors.text.primary} />
          </LinearGradient>
        </TouchableOpacity>

        <Text
          style={{
            color: colors.text.secondary,
            fontSize: 16,
            textAlign: "center",
          }}
        >
          Prenez une photo ou{"\n"}sélectionnez une image
        </Text>

        {/* Options */}
        <View
          style={{
            flexDirection: "row",
            marginTop: 32,
            gap: 16,
          }}
        >
          <TouchableOpacity
            style={{
              flex: 1,
              backgroundColor: colors.background.card,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: colors.border.default,
              padding: 16,
              alignItems: "center",
            }}
          >
            <Ionicons name="camera-outline" size={24} color={colors.neon.cyan} />
            <Text style={{ color: colors.text.primary, marginTop: 8 }}>
              Caméra
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={{
              flex: 1,
              backgroundColor: colors.background.card,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: colors.border.default,
              padding: 16,
              alignItems: "center",
            }}
          >
            <Ionicons name="images-outline" size={24} color={colors.neon.purple} />
            <Text style={{ color: colors.text.primary, marginTop: 8 }}>
              Galerie
            </Text>
          </TouchableOpacity>
        </View>

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
            Phase 6 - En développement
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
