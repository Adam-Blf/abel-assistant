/**
 * =============================================================================
 * (TABS)/VOICE.TSX - Voice Interaction Screen
 * =============================================================================
 * A.B.E.L. Project - Voice STT/TTS Interface
 * =============================================================================
 */

import { useCallback, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import * as Speech from "expo-speech";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  cancelAnimation,
} from "react-native-reanimated";

import { useVoice } from "@hooks/useVoice";
import { colors } from "@theme/colors";

export default function VoiceScreen() {
  const {
    isRecording,
    isProcessing,
    duration,
    transcription,
    response,
    error,
    startRecording,
    stopRecording,
    cancelRecording,
    reset,
  } = useVoice();

  // Pulse animation for recording
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  useEffect(() => {
    if (isRecording) {
      scale.value = withRepeat(
        withTiming(1.2, { duration: 1000 }),
        -1,
        true
      );
      opacity.value = withRepeat(
        withTiming(0.6, { duration: 1000 }),
        -1,
        true
      );
    } else {
      cancelAnimation(scale);
      cancelAnimation(opacity);
      scale.value = withTiming(1, { duration: 200 });
      opacity.value = withTiming(1, { duration: 200 });
    }
  }, [isRecording]);

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  /**
   * Handle mic press
   */
  const handleMicPress = useCallback(async () => {
    if (isRecording) {
      const result = await stopRecording();
      // Speak response
      if (result?.response) {
        Speech.speak(result.response, {
          language: "fr-FR",
          rate: 1.0,
        });
      }
    } else {
      await startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  /**
   * Format duration
   */
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  /**
   * Handle new conversation
   */
  const handleNewConversation = useCallback(() => {
    Speech.stop();
    reset();
  }, [reset]);

  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: colors.background.primary }}
      edges={["top"]}
    >
      {/* Header */}
      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          paddingHorizontal: 16,
          paddingVertical: 12,
          borderBottomWidth: 1,
          borderBottomColor: colors.border.default,
        }}
      >
        <View>
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

        {(transcription || response) && (
          <TouchableOpacity
            onPress={handleNewConversation}
            style={{
              paddingHorizontal: 12,
              paddingVertical: 6,
              backgroundColor: colors.background.card,
              borderRadius: 16,
            }}
          >
            <Text style={{ color: colors.neon.cyan, fontSize: 12 }}>
              Nouveau
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Content */}
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{
          flexGrow: 1,
          justifyContent: "center",
          alignItems: "center",
          padding: 24,
        }}
      >
        {/* Response Display */}
        {response && !isRecording && !isProcessing && (
          <View
            style={{
              width: "100%",
              backgroundColor: colors.background.card,
              borderRadius: 16,
              padding: 16,
              marginBottom: 32,
              borderWidth: 1,
              borderColor: colors.border.default,
            }}
          >
            {transcription && (
              <View style={{ marginBottom: 12 }}>
                <Text style={{ color: colors.text.muted, fontSize: 12, marginBottom: 4 }}>
                  Vous avez dit:
                </Text>
                <Text style={{ color: colors.text.secondary, fontSize: 14 }}>
                  "{transcription}"
                </Text>
              </View>
            )}
            <View>
              <Text style={{ color: colors.neon.cyan, fontSize: 12, marginBottom: 4 }}>
                A.B.E.L.:
              </Text>
              <Text style={{ color: colors.text.primary, fontSize: 16, lineHeight: 24 }}>
                {response}
              </Text>
            </View>
          </View>
        )}

        {/* Mic Button with Pulse Effect */}
        <Animated.View style={[pulseStyle]}>
          <TouchableOpacity
            onPress={handleMicPress}
            disabled={isProcessing}
            onLongPress={cancelRecording}
            style={{
              width: 120,
              height: 120,
              borderRadius: 60,
              overflow: "hidden",
              marginBottom: 24,
            }}
          >
            <LinearGradient
              colors={
                isRecording
                  ? [colors.neon.red, colors.neon.orange]
                  : isProcessing
                  ? [colors.background.card, colors.background.card]
                  : [colors.neon.cyan, colors.neon.purple]
              }
              style={{
                width: "100%",
                height: "100%",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              {isProcessing ? (
                <ActivityIndicator size="large" color={colors.neon.cyan} />
              ) : (
                <Ionicons
                  name={isRecording ? "stop" : "mic"}
                  size={48}
                  color={colors.background.primary}
                />
              )}
            </LinearGradient>
          </TouchableOpacity>
        </Animated.View>

        {/* Status Text */}
        <Text
          style={{
            color: isRecording ? colors.neon.red : colors.text.secondary,
            fontSize: 16,
            textAlign: "center",
            marginBottom: 8,
          }}
        >
          {isRecording
            ? `Enregistrement... ${formatDuration(duration)}`
            : isProcessing
            ? "Traitement en cours..."
            : "Appuyez pour parler"}
        </Text>

        {isRecording && (
          <Text style={{ color: colors.text.muted, fontSize: 12 }}>
            Maintenez pour annuler
          </Text>
        )}

        {/* Error Display */}
        {error && (
          <View
            style={{
              marginTop: 16,
              paddingHorizontal: 16,
              paddingVertical: 8,
              backgroundColor: "rgba(255, 69, 58, 0.1)",
              borderRadius: 8,
              borderWidth: 1,
              borderColor: colors.neon.red,
            }}
          >
            <Text style={{ color: colors.neon.red, fontSize: 14 }}>{error}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
