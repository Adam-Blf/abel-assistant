/**
 * =============================================================================
 * (TABS)/SETTINGS.TSX - Settings Screen
 * =============================================================================
 * A.B.E.L. Project - Application Settings
 * =============================================================================
 */

import { View, Text, TouchableOpacity, ScrollView, Switch, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";

import { useAuth } from "@contexts/AuthContext";
import { useBiometric } from "@hooks/useBiometric";
import { colors } from "@theme/colors";

export default function SettingsScreen() {
  const { user, logout } = useAuth();
  const { isEnabled, isAvailable, biometricType, enableBiometric, disableBiometric } =
    useBiometric();

  /**
   * Handle biometric toggle
   */
  const handleBiometricToggle = async (value: boolean) => {
    if (value) {
      await enableBiometric();
    } else {
      await disableBiometric();
    }
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    Alert.alert(
      "Déconnexion",
      "Êtes-vous sûr de vouloir vous déconnecter ?",
      [
        { text: "Annuler", style: "cancel" },
        {
          text: "Déconnexion",
          style: "destructive",
          onPress: logout,
        },
      ]
    );
  };

  /**
   * Settings section component
   */
  const SettingsSection = ({
    title,
    children,
  }: {
    title: string;
    children: React.ReactNode;
  }) => (
    <View style={{ marginBottom: 24 }}>
      <Text
        style={{
          color: colors.text.secondary,
          fontSize: 12,
          fontWeight: "600",
          textTransform: "uppercase",
          letterSpacing: 1,
          marginBottom: 8,
          paddingHorizontal: 4,
        }}
      >
        {title}
      </Text>
      <View
        style={{
          backgroundColor: colors.background.card,
          borderRadius: 12,
          borderWidth: 1,
          borderColor: colors.border.default,
          overflow: "hidden",
        }}
      >
        {children}
      </View>
    </View>
  );

  /**
   * Settings row component
   */
  const SettingsRow = ({
    icon,
    iconColor = colors.text.secondary,
    label,
    value,
    onPress,
    rightElement,
    showChevron = true,
    destructive = false,
  }: {
    icon: string;
    iconColor?: string;
    label: string;
    value?: string;
    onPress?: () => void;
    rightElement?: React.ReactNode;
    showChevron?: boolean;
    destructive?: boolean;
  }) => (
    <TouchableOpacity
      onPress={onPress}
      disabled={!onPress}
      style={{
        flexDirection: "row",
        alignItems: "center",
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: colors.border.default,
      }}
    >
      <Ionicons name={icon as any} size={22} color={iconColor} />
      <Text
        style={{
          flex: 1,
          color: destructive ? colors.neon.red : colors.text.primary,
          fontSize: 16,
          marginLeft: 12,
        }}
      >
        {label}
      </Text>
      {value && (
        <Text style={{ color: colors.text.muted, fontSize: 14, marginRight: 8 }}>
          {value}
        </Text>
      )}
      {rightElement}
      {showChevron && onPress && (
        <Ionicons name="chevron-forward" size={20} color={colors.text.muted} />
      )}
    </TouchableOpacity>
  );

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
          Réglages
        </Text>
      </View>

      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Profile Section */}
        <SettingsSection title="Profil">
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              padding: 16,
              borderBottomWidth: 1,
              borderBottomColor: colors.border.default,
            }}
          >
            <View
              style={{
                width: 56,
                height: 56,
                borderRadius: 28,
                backgroundColor: colors.neon.cyan,
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <Text
                style={{
                  color: colors.background.primary,
                  fontSize: 24,
                  fontWeight: "bold",
                }}
              >
                {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || "?"}
              </Text>
            </View>
            <View style={{ flex: 1, marginLeft: 12 }}>
              <Text style={{ color: colors.text.primary, fontSize: 18, fontWeight: "600" }}>
                {user?.name || "Utilisateur"}
              </Text>
              <Text style={{ color: colors.text.muted, fontSize: 14, marginTop: 2 }}>
                {user?.email || "email@example.com"}
              </Text>
            </View>
          </View>
          <SettingsRow
            icon="person-outline"
            label="Modifier le profil"
            onPress={() => {}}
          />
        </SettingsSection>

        {/* Security Section */}
        <SettingsSection title="Sécurité">
          {isAvailable && (
            <SettingsRow
              icon={biometricType === "facial" ? "scan-outline" : "finger-print-outline"}
              iconColor={colors.neon.cyan}
              label={biometricType === "facial" ? "Face ID" : "Empreinte digitale"}
              showChevron={false}
              rightElement={
                <Switch
                  value={isEnabled}
                  onValueChange={handleBiometricToggle}
                  trackColor={{
                    false: colors.background.tertiary,
                    true: colors.neon.cyan,
                  }}
                  thumbColor={colors.text.primary}
                />
              }
            />
          )}
          <SettingsRow
            icon="lock-closed-outline"
            label="Changer le mot de passe"
            onPress={() => {}}
          />
          <SettingsRow
            icon="time-outline"
            label="Délai d'expiration"
            value="15 min"
            onPress={() => {}}
          />
        </SettingsSection>

        {/* App Settings */}
        <SettingsSection title="Application">
          <SettingsRow
            icon="notifications-outline"
            label="Notifications"
            onPress={() => {}}
          />
          <SettingsRow
            icon="moon-outline"
            label="Thème"
            value="Sombre"
            onPress={() => {}}
          />
          <SettingsRow
            icon="language-outline"
            label="Langue"
            value="Français"
            onPress={() => {}}
          />
        </SettingsSection>

        {/* About Section */}
        <SettingsSection title="À propos">
          <SettingsRow
            icon="information-circle-outline"
            label="Version"
            value="1.0.0"
            showChevron={false}
          />
          <SettingsRow
            icon="document-text-outline"
            label="Politique de confidentialité"
            onPress={() => {}}
          />
          <SettingsRow
            icon="shield-checkmark-outline"
            label="Conditions d'utilisation"
            onPress={() => {}}
          />
          <SettingsRow
            icon="logo-github"
            label="Code source (Open Source)"
            onPress={() => {}}
          />
        </SettingsSection>

        {/* Logout */}
        <SettingsSection title="Session">
          <SettingsRow
            icon="log-out-outline"
            iconColor={colors.neon.red}
            label="Déconnexion"
            onPress={handleLogout}
            showChevron={false}
            destructive
          />
        </SettingsSection>

        {/* Footer */}
        <View style={{ alignItems: "center", paddingVertical: 24 }}>
          <Text style={{ color: colors.neon.cyan, fontSize: 18, fontWeight: "bold" }}>
            A.B.E.L.
          </Text>
          <Text style={{ color: colors.text.muted, fontSize: 12, marginTop: 4 }}>
            Assistant Biométrique Enhanced Liaison
          </Text>
          <Text style={{ color: colors.text.muted, fontSize: 11, marginTop: 8 }}>
            Made with ❤️ by Adam
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
