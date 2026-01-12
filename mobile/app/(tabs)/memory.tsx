/**
 * =============================================================================
 * (TABS)/MEMORY.TSX - Memory/RAG Screen
 * =============================================================================
 * A.B.E.L. Project - Personal Memory Management (Phase 7)
 * This is where A.B.E.L. learns from you!
 * =============================================================================
 */

import { View, Text, TouchableOpacity, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";

import { colors } from "@theme/colors";

export default function MemoryScreen() {
  // Placeholder memory items
  const memoryItems = [
    {
      id: "1",
      type: "preference",
      title: "Préférences",
      description: "Vos goûts et préférences personnelles",
      icon: "heart-outline",
      color: colors.neon.magenta,
    },
    {
      id: "2",
      type: "habit",
      title: "Habitudes",
      description: "Vos routines et comportements",
      icon: "repeat-outline",
      color: colors.neon.cyan,
    },
    {
      id: "3",
      type: "knowledge",
      title: "Connaissances",
      description: "Ce que vous m'avez appris",
      icon: "bulb-outline",
      color: colors.neon.green,
    },
    {
      id: "4",
      type: "context",
      title: "Contexte",
      description: "Informations sur votre vie",
      icon: "person-outline",
      color: colors.neon.purple,
    },
  ];

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
          Memory
        </Text>
        <Text style={{ color: colors.text.secondary, fontSize: 14, marginTop: 4 }}>
          A.B.E.L. apprend de vous
        </Text>
      </View>

      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Info Card */}
        <View
          style={{
            backgroundColor: colors.background.card,
            borderRadius: 16,
            borderWidth: 1,
            borderColor: colors.neon.cyan,
            padding: 16,
            marginBottom: 24,
          }}
        >
          <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 12 }}>
            <Ionicons name="information-circle" size={24} color={colors.neon.cyan} />
            <Text
              style={{
                color: colors.neon.cyan,
                fontSize: 16,
                fontWeight: "bold",
                marginLeft: 8,
              }}
            >
              Mémoire personnalisée
            </Text>
          </View>
          <Text style={{ color: colors.text.secondary, lineHeight: 22 }}>
            A.B.E.L. se souvient de vos conversations et apprend de vos préférences
            pour vous offrir une expérience personnalisée. Vos données sont
            sécurisées et vous en gardez le contrôle total.
          </Text>
        </View>

        {/* Memory Categories */}
        <Text
          style={{
            color: colors.text.primary,
            fontSize: 18,
            fontWeight: "bold",
            marginBottom: 16,
          }}
        >
          Catégories de mémoire
        </Text>

        {memoryItems.map((item) => (
          <TouchableOpacity
            key={item.id}
            style={{
              backgroundColor: colors.background.card,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: colors.border.default,
              padding: 16,
              marginBottom: 12,
              flexDirection: "row",
              alignItems: "center",
            }}
          >
            <View
              style={{
                width: 48,
                height: 48,
                borderRadius: 24,
                backgroundColor: colors.background.tertiary,
                justifyContent: "center",
                alignItems: "center",
                borderWidth: 1,
                borderColor: item.color,
              }}
            >
              <Ionicons name={item.icon as any} size={24} color={item.color} />
            </View>
            <View style={{ flex: 1, marginLeft: 12 }}>
              <Text style={{ color: colors.text.primary, fontSize: 16, fontWeight: "600" }}>
                {item.title}
              </Text>
              <Text style={{ color: colors.text.muted, fontSize: 13, marginTop: 2 }}>
                {item.description}
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.text.muted} />
          </TouchableOpacity>
        ))}

        {/* Actions */}
        <View style={{ marginTop: 24 }}>
          <TouchableOpacity
            style={{
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: colors.background.card,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: colors.neon.green,
              padding: 16,
              marginBottom: 12,
            }}
          >
            <Ionicons name="add-circle-outline" size={20} color={colors.neon.green} />
            <Text style={{ color: colors.neon.green, marginLeft: 8, fontWeight: "600" }}>
              Ajouter une information
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={{
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: colors.background.card,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: colors.neon.red,
              padding: 16,
            }}
          >
            <Ionicons name="trash-outline" size={20} color={colors.neon.red} />
            <Text style={{ color: colors.neon.red, marginLeft: 8, fontWeight: "600" }}>
              Effacer ma mémoire
            </Text>
          </TouchableOpacity>
        </View>

        {/* Coming Soon Badge */}
        <View
          style={{
            marginTop: 32,
            alignItems: "center",
          }}
        >
          <View
            style={{
              paddingHorizontal: 16,
              paddingVertical: 8,
              backgroundColor: colors.background.card,
              borderRadius: 20,
              borderWidth: 1,
              borderColor: colors.neon.orange,
            }}
          >
            <Text style={{ color: colors.neon.orange, fontSize: 12 }}>
              Phase 7 - En développement
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
