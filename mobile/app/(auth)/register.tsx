/**
 * =============================================================================
 * REGISTER.TSX - Registration Screen
 * =============================================================================
 * A.B.E.L. Project - Cyberpunk themed registration
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
  ScrollView,
} from "react-native";
import { Link, router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";

import { useAuth } from "@contexts/AuthContext";
import { colors } from "@theme/colors";

export default function RegisterScreen() {
  const { register, isLoading } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{
    name?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  /**
   * Validate inputs
   */
  const validate = useCallback((): boolean => {
    const newErrors: typeof errors = {};

    if (!name.trim()) {
      newErrors.name = "Nom requis";
    } else if (name.trim().length < 2) {
      newErrors.name = "Minimum 2 caractères";
    }

    if (!email.trim()) {
      newErrors.email = "Email requis";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Email invalide";
    }

    if (!password) {
      newErrors.password = "Mot de passe requis";
    } else if (password.length < 8) {
      newErrors.password = "Minimum 8 caractères";
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      newErrors.password = "Doit contenir majuscule, minuscule et chiffre";
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = "Les mots de passe ne correspondent pas";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [name, email, password, confirmPassword]);

  /**
   * Handle registration
   */
  const handleRegister = useCallback(async () => {
    if (!validate()) return;

    const success = await register(email, password, name);

    if (success) {
      Alert.alert(
        "Bienvenue sur A.B.E.L.",
        "Votre compte a été créé avec succès !",
        [
          {
            text: "Commencer",
            onPress: () => router.replace("/(tabs)"),
          },
        ]
      );
    } else {
      Alert.alert(
        "Erreur d'inscription",
        "Impossible de créer le compte. Vérifiez vos informations.",
        [{ text: "OK" }]
      );
    }
  }, [email, password, name, register, validate]);

  /**
   * Input component
   */
  const InputField = ({
    icon,
    placeholder,
    value,
    onChangeText,
    error,
    secure = false,
    keyboardType = "default" as any,
    autoCapitalize = "none" as any,
  }: {
    icon: string;
    placeholder: string;
    value: string;
    onChangeText: (text: string) => void;
    error?: string;
    secure?: boolean;
    keyboardType?: any;
    autoCapitalize?: any;
  }) => (
    <View style={{ marginBottom: 16 }}>
      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          backgroundColor: colors.background.card,
          borderRadius: 12,
          borderWidth: 1,
          borderColor: error ? colors.border.error : colors.border.default,
          paddingHorizontal: 16,
        }}
      >
        <Ionicons name={icon as any} size={20} color={colors.text.muted} />
        <TextInput
          style={{
            flex: 1,
            height: 50,
            color: colors.text.primary,
            marginLeft: 12,
          }}
          placeholder={placeholder}
          placeholderTextColor={colors.text.muted}
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={secure && !showPassword}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
        />
        {secure && (
          <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
            <Ionicons
              name={showPassword ? "eye-off-outline" : "eye-outline"}
              size={20}
              color={colors.text.muted}
            />
          </TouchableOpacity>
        )}
      </View>
      {error && (
        <Text style={{ color: colors.neon.red, fontSize: 12, marginTop: 4 }}>
          {error}
        </Text>
      )}
    </View>
  );

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      style={{ flex: 1, backgroundColor: colors.background.primary }}
    >
      <ScrollView
        contentContainerStyle={{
          flexGrow: 1,
          padding: 24,
          justifyContent: "center",
        }}
        keyboardShouldPersistTaps="handled"
      >
        {/* Back Button */}
        <TouchableOpacity
          onPress={() => router.back()}
          style={{
            position: "absolute",
            top: 60,
            left: 24,
            flexDirection: "row",
            alignItems: "center",
          }}
        >
          <Ionicons name="chevron-back" size={24} color={colors.neon.cyan} />
          <Text style={{ color: colors.neon.cyan, marginLeft: 4 }}>Retour</Text>
        </TouchableOpacity>

        {/* Header */}
        <View style={{ alignItems: "center", marginBottom: 40 }}>
          <Text
            style={{
              fontSize: 36,
              fontWeight: "bold",
              color: colors.neon.cyan,
              letterSpacing: 2,
            }}
          >
            Créer un compte
          </Text>
          <Text
            style={{
              fontSize: 14,
              color: colors.text.secondary,
              marginTop: 8,
              textAlign: "center",
            }}
          >
            Rejoignez A.B.E.L. et découvrez{"\n"}votre assistant IA personnel
          </Text>
        </View>

        {/* Form */}
        <InputField
          icon="person-outline"
          placeholder="Votre nom"
          value={name}
          onChangeText={setName}
          error={errors.name}
          autoCapitalize="words"
        />

        <InputField
          icon="mail-outline"
          placeholder="votre@email.com"
          value={email}
          onChangeText={setEmail}
          error={errors.email}
          keyboardType="email-address"
        />

        <InputField
          icon="lock-closed-outline"
          placeholder="Mot de passe"
          value={password}
          onChangeText={setPassword}
          error={errors.password}
          secure
        />

        <InputField
          icon="shield-checkmark-outline"
          placeholder="Confirmer le mot de passe"
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          error={errors.confirmPassword}
          secure
        />

        {/* Password Requirements */}
        <View style={{ marginBottom: 24 }}>
          <Text style={{ color: colors.text.muted, fontSize: 12 }}>
            Le mot de passe doit contenir :
          </Text>
          <Text style={{ color: colors.text.muted, fontSize: 12 }}>
            • Au moins 8 caractères
          </Text>
          <Text style={{ color: colors.text.muted, fontSize: 12 }}>
            • Une majuscule et une minuscule
          </Text>
          <Text style={{ color: colors.text.muted, fontSize: 12 }}>
            • Un chiffre
          </Text>
        </View>

        {/* Register Button */}
        <TouchableOpacity
          onPress={handleRegister}
          disabled={isLoading}
          style={{ marginBottom: 24 }}
        >
          <LinearGradient
            colors={[colors.neon.magenta, colors.neon.purple]}
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
              <ActivityIndicator color={colors.text.primary} />
            ) : (
              <Text
                style={{
                  color: colors.text.primary,
                  fontSize: 16,
                  fontWeight: "bold",
                }}
              >
                Créer mon compte
              </Text>
            )}
          </LinearGradient>
        </TouchableOpacity>

        {/* Login Link */}
        <View style={{ flexDirection: "row", justifyContent: "center" }}>
          <Text style={{ color: colors.text.secondary }}>
            Déjà un compte ?{" "}
          </Text>
          <Link href="/(auth)/login" asChild>
            <TouchableOpacity>
              <Text style={{ color: colors.neon.cyan, fontWeight: "bold" }}>
                Se connecter
              </Text>
            </TouchableOpacity>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
