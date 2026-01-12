/**
 * =============================================================================
 * LOGIN.TSX - Login Screen
 * =============================================================================
 * A.B.E.L. Project - Cyberpunk themed login with biometric support
 * =============================================================================
 */

import { useState, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from "react-native";
import { Link, router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";

import { useAuth } from "@contexts/AuthContext";
import { useBiometric } from "@hooks/useBiometric";
import { colors } from "@theme/colors";

export default function LoginScreen() {
  const { login, isLoading } = useAuth();
  const { isAvailable: biometricAvailable, authenticate, biometricType } = useBiometric();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  /**
   * Validate inputs
   */
  const validate = useCallback((): boolean => {
    const newErrors: typeof errors = {};

    if (!email.trim()) {
      newErrors.email = "Email requis";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Email invalide";
    }

    if (!password) {
      newErrors.password = "Mot de passe requis";
    } else if (password.length < 6) {
      newErrors.password = "Minimum 6 caractères";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [email, password]);

  /**
   * Handle login
   */
  const handleLogin = useCallback(async () => {
    if (!validate()) return;

    const success = await login(email, password);

    if (success) {
      router.replace("/(tabs)");
    } else {
      Alert.alert(
        "Erreur de connexion",
        "Email ou mot de passe incorrect",
        [{ text: "OK" }]
      );
    }
  }, [email, password, login, validate]);

  /**
   * Handle biometric login
   */
  const handleBiometricLogin = useCallback(async () => {
    const success = await authenticate("Connexion à A.B.E.L.");
    if (success) {
      // Biometric success - attempt auto-login if tokens exist
      router.replace("/(tabs)");
    }
  }, [authenticate]);

  /**
   * Get biometric icon
   */
  const getBiometricIcon = () => {
    switch (biometricType) {
      case "facial":
        return "scan-outline";
      case "fingerprint":
        return "finger-print-outline";
      default:
        return "lock-closed-outline";
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={{ flex: 1, backgroundColor: colors.background.primary }}
    >
      <View style={{ flex: 1, padding: 24, justifyContent: "center" }}>
        {/* Header */}
        <View style={{ alignItems: "center", marginBottom: 48 }}>
          <Text
            style={{
              fontSize: 48,
              fontWeight: "bold",
              color: colors.neon.cyan,
              letterSpacing: 4,
            }}
          >
            A.B.E.L.
          </Text>
          <Text
            style={{
              fontSize: 14,
              color: colors.text.secondary,
              marginTop: 8,
            }}
          >
            Assistant Biométrique Enhanced Liaison
          </Text>
        </View>

        {/* Email Input */}
        <View style={{ marginBottom: 16 }}>
          <Text style={{ color: colors.text.secondary, marginBottom: 8 }}>
            Email
          </Text>
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              backgroundColor: colors.background.card,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: errors.email ? colors.border.error : colors.border.default,
              paddingHorizontal: 16,
            }}
          >
            <Ionicons name="mail-outline" size={20} color={colors.text.muted} />
            <TextInput
              style={{
                flex: 1,
                height: 50,
                color: colors.text.primary,
                marginLeft: 12,
              }}
              placeholder="votre@email.com"
              placeholderTextColor={colors.text.muted}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
            />
          </View>
          {errors.email && (
            <Text style={{ color: colors.neon.red, fontSize: 12, marginTop: 4 }}>
              {errors.email}
            </Text>
          )}
        </View>

        {/* Password Input */}
        <View style={{ marginBottom: 24 }}>
          <Text style={{ color: colors.text.secondary, marginBottom: 8 }}>
            Mot de passe
          </Text>
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              backgroundColor: colors.background.card,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: errors.password ? colors.border.error : colors.border.default,
              paddingHorizontal: 16,
            }}
          >
            <Ionicons name="lock-closed-outline" size={20} color={colors.text.muted} />
            <TextInput
              style={{
                flex: 1,
                height: 50,
                color: colors.text.primary,
                marginLeft: 12,
              }}
              placeholder="••••••••"
              placeholderTextColor={colors.text.muted}
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              autoComplete="password"
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
              <Ionicons
                name={showPassword ? "eye-off-outline" : "eye-outline"}
                size={20}
                color={colors.text.muted}
              />
            </TouchableOpacity>
          </View>
          {errors.password && (
            <Text style={{ color: colors.neon.red, fontSize: 12, marginTop: 4 }}>
              {errors.password}
            </Text>
          )}
        </View>

        {/* Login Button */}
        <TouchableOpacity
          onPress={handleLogin}
          disabled={isLoading}
          style={{ marginBottom: 16 }}
        >
          <LinearGradient
            colors={[colors.neon.cyan, colors.neon.purple]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={{
              height: 50,
              borderRadius: 12,
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            {isLoading ? (
              <ActivityIndicator color={colors.background.primary} />
            ) : (
              <Text
                style={{
                  color: colors.background.primary,
                  fontSize: 16,
                  fontWeight: "bold",
                }}
              >
                Se connecter
              </Text>
            )}
          </LinearGradient>
        </TouchableOpacity>

        {/* Biometric Button */}
        {biometricAvailable && (
          <TouchableOpacity
            onPress={handleBiometricLogin}
            style={{
              height: 50,
              borderRadius: 12,
              borderWidth: 1,
              borderColor: colors.neon.cyan,
              justifyContent: "center",
              alignItems: "center",
              flexDirection: "row",
              marginBottom: 24,
            }}
          >
            <Ionicons name={getBiometricIcon()} size={24} color={colors.neon.cyan} />
            <Text
              style={{
                color: colors.neon.cyan,
                fontSize: 16,
                marginLeft: 8,
              }}
            >
              {biometricType === "facial" ? "Face ID" : "Empreinte"}
            </Text>
          </TouchableOpacity>
        )}

        {/* Register Link */}
        <View style={{ flexDirection: "row", justifyContent: "center" }}>
          <Text style={{ color: colors.text.secondary }}>
            Pas encore de compte ?{" "}
          </Text>
          <Link href="/(auth)/register" asChild>
            <TouchableOpacity>
              <Text style={{ color: colors.neon.cyan, fontWeight: "bold" }}>
                S'inscrire
              </Text>
            </TouchableOpacity>
          </Link>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}
