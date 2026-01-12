/**
 * =============================================================================
 * (TABS)/VISION.TSX - Vision AI Screen
 * =============================================================================
 * A.B.E.L. Project - Image Analysis Interface with Gemini Vision
 * =============================================================================
 */

import { useState, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  ScrollView,
  ActivityIndicator,
  TextInput,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";

import { useCamera } from "@hooks/useCamera";
import { colors } from "@theme/colors";

type AnalysisMode = "analyze" | "ocr" | "objects";

export default function VisionScreen() {
  const {
    hasPermission,
    isAnalyzing,
    currentImage,
    analysisResult,
    objects,
    extractedText,
    error,
    takePhoto,
    pickImage,
    analyzeImage,
    identifyObjects,
    extractText,
    reset,
  } = useCamera();

  const [question, setQuestion] = useState("");
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>("analyze");

  /**
   * Handle camera capture
   */
  const handleCamera = useCallback(async () => {
    await takePhoto();
  }, [takePhoto]);

  /**
   * Handle gallery selection
   */
  const handleGallery = useCallback(async () => {
    await pickImage();
  }, [pickImage]);

  /**
   * Handle analysis based on mode
   */
  const handleAnalyze = useCallback(async () => {
    if (!currentImage) return;

    switch (analysisMode) {
      case "analyze":
        await analyzeImage(currentImage, question || undefined);
        break;
      case "ocr":
        await extractText(currentImage);
        break;
      case "objects":
        await identifyObjects(currentImage);
        break;
    }
  }, [currentImage, analysisMode, question, analyzeImage, extractText, identifyObjects]);

  /**
   * Handle new analysis
   */
  const handleNewAnalysis = useCallback(() => {
    reset();
    setQuestion("");
  }, [reset]);

  // Permission denied
  if (hasPermission === false) {
    return (
      <SafeAreaView
        style={{ flex: 1, backgroundColor: colors.background.primary }}
        edges={["top"]}
      >
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24 }}>
          <Ionicons name="camera-off" size={64} color={colors.neon.red} />
          <Text style={{ color: colors.text.primary, fontSize: 18, marginTop: 16, textAlign: "center" }}>
            Accès à la caméra refusé
          </Text>
          <Text style={{ color: colors.text.secondary, fontSize: 14, marginTop: 8, textAlign: "center" }}>
            Veuillez autoriser l'accès dans les paramètres
          </Text>
        </View>
      </SafeAreaView>
    );
  }

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
            Vision
          </Text>
          <Text style={{ color: colors.text.secondary, fontSize: 14, marginTop: 4 }}>
            Analyse d'images avec Gemini
          </Text>
        </View>

        {currentImage && (
          <TouchableOpacity
            onPress={handleNewAnalysis}
            style={{
              paddingHorizontal: 12,
              paddingVertical: 6,
              backgroundColor: colors.background.card,
              borderRadius: 16,
            }}
          >
            <Text style={{ color: colors.neon.magenta, fontSize: 12 }}>
              Nouvelle
            </Text>
          </TouchableOpacity>
        )}
      </View>

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{
          flexGrow: 1,
          padding: 16,
        }}
      >
        {/* Image Preview or Capture */}
        {currentImage ? (
          <View style={{ marginBottom: 16 }}>
            <Image
              source={{ uri: currentImage }}
              style={{
                width: "100%",
                height: 300,
                borderRadius: 16,
                backgroundColor: colors.background.card,
              }}
              resizeMode="contain"
            />
          </View>
        ) : (
          <View
            style={{
              alignItems: "center",
              justifyContent: "center",
              paddingVertical: 40,
            }}
          >
            {/* Main Camera Button */}
            <TouchableOpacity
              onPress={handleCamera}
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

            {/* Capture Options */}
            <View
              style={{
                flexDirection: "row",
                marginTop: 32,
                gap: 16,
                width: "100%",
              }}
            >
              <TouchableOpacity
                onPress={handleCamera}
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
                onPress={handleGallery}
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
          </View>
        )}

        {/* Analysis Options */}
        {currentImage && !analysisResult && !objects.length && !extractedText && (
          <View style={{ marginBottom: 16 }}>
            {/* Mode Selection */}
            <View
              style={{
                flexDirection: "row",
                marginBottom: 16,
                gap: 8,
              }}
            >
              <TouchableOpacity
                onPress={() => setAnalysisMode("analyze")}
                style={{
                  flex: 1,
                  paddingVertical: 12,
                  backgroundColor: analysisMode === "analyze" ? colors.neon.cyan : colors.background.card,
                  borderRadius: 8,
                  alignItems: "center",
                }}
              >
                <Text
                  style={{
                    color: analysisMode === "analyze" ? colors.background.primary : colors.text.primary,
                    fontWeight: analysisMode === "analyze" ? "bold" : "normal",
                  }}
                >
                  Analyser
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => setAnalysisMode("ocr")}
                style={{
                  flex: 1,
                  paddingVertical: 12,
                  backgroundColor: analysisMode === "ocr" ? colors.neon.purple : colors.background.card,
                  borderRadius: 8,
                  alignItems: "center",
                }}
              >
                <Text
                  style={{
                    color: analysisMode === "ocr" ? colors.background.primary : colors.text.primary,
                    fontWeight: analysisMode === "ocr" ? "bold" : "normal",
                  }}
                >
                  Texte (OCR)
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                onPress={() => setAnalysisMode("objects")}
                style={{
                  flex: 1,
                  paddingVertical: 12,
                  backgroundColor: analysisMode === "objects" ? colors.neon.orange : colors.background.card,
                  borderRadius: 8,
                  alignItems: "center",
                }}
              >
                <Text
                  style={{
                    color: analysisMode === "objects" ? colors.background.primary : colors.text.primary,
                    fontWeight: analysisMode === "objects" ? "bold" : "normal",
                  }}
                >
                  Objets
                </Text>
              </TouchableOpacity>
            </View>

            {/* Question Input (only for analyze mode) */}
            {analysisMode === "analyze" && (
              <TextInput
                value={question}
                onChangeText={setQuestion}
                placeholder="Posez une question sur l'image (optionnel)"
                placeholderTextColor={colors.text.muted}
                style={{
                  backgroundColor: colors.background.card,
                  borderRadius: 12,
                  borderWidth: 1,
                  borderColor: colors.border.default,
                  padding: 16,
                  color: colors.text.primary,
                  fontSize: 16,
                  marginBottom: 16,
                }}
              />
            )}

            {/* Analyze Button */}
            <TouchableOpacity
              onPress={handleAnalyze}
              disabled={isAnalyzing}
              style={{
                backgroundColor: colors.neon.cyan,
                borderRadius: 12,
                padding: 16,
                alignItems: "center",
                opacity: isAnalyzing ? 0.7 : 1,
              }}
            >
              {isAnalyzing ? (
                <ActivityIndicator color={colors.background.primary} />
              ) : (
                <Text
                  style={{
                    color: colors.background.primary,
                    fontSize: 16,
                    fontWeight: "bold",
                  }}
                >
                  {analysisMode === "analyze"
                    ? "Analyser l'image"
                    : analysisMode === "ocr"
                    ? "Extraire le texte"
                    : "Identifier les objets"}
                </Text>
              )}
            </TouchableOpacity>
          </View>
        )}

        {/* Results Display */}
        {analysisResult && (
          <View
            style={{
              backgroundColor: colors.background.card,
              borderRadius: 16,
              padding: 16,
              marginBottom: 16,
              borderWidth: 1,
              borderColor: colors.border.default,
            }}
          >
            <Text style={{ color: colors.neon.cyan, fontSize: 12, marginBottom: 8 }}>
              Analyse:
            </Text>
            <Text style={{ color: colors.text.primary, fontSize: 16, lineHeight: 24 }}>
              {analysisResult}
            </Text>
          </View>
        )}

        {extractedText && (
          <View
            style={{
              backgroundColor: colors.background.card,
              borderRadius: 16,
              padding: 16,
              marginBottom: 16,
              borderWidth: 1,
              borderColor: colors.border.default,
            }}
          >
            <Text style={{ color: colors.neon.purple, fontSize: 12, marginBottom: 8 }}>
              Texte extrait:
            </Text>
            <Text
              style={{
                color: colors.text.primary,
                fontSize: 14,
                lineHeight: 22,
                fontFamily: "monospace",
              }}
              selectable
            >
              {extractedText}
            </Text>
          </View>
        )}

        {objects.length > 0 && (
          <View
            style={{
              backgroundColor: colors.background.card,
              borderRadius: 16,
              padding: 16,
              marginBottom: 16,
              borderWidth: 1,
              borderColor: colors.border.default,
            }}
          >
            <Text style={{ color: colors.neon.orange, fontSize: 12, marginBottom: 12 }}>
              Objets détectés ({objects.length}):
            </Text>
            {objects.map((obj, index) => (
              <View
                key={index}
                style={{
                  flexDirection: "row",
                  justifyContent: "space-between",
                  alignItems: "center",
                  paddingVertical: 8,
                  borderBottomWidth: index < objects.length - 1 ? 1 : 0,
                  borderBottomColor: colors.border.default,
                }}
              >
                <Text style={{ color: colors.text.primary, fontSize: 14 }}>
                  {obj.name}
                </Text>
                <View
                  style={{
                    backgroundColor: colors.background.primary,
                    paddingHorizontal: 8,
                    paddingVertical: 4,
                    borderRadius: 8,
                  }}
                >
                  <Text style={{ color: colors.neon.cyan, fontSize: 12 }}>
                    {Math.round(obj.confidence * 100)}%
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Error Display */}
        {error && (
          <View
            style={{
              paddingHorizontal: 16,
              paddingVertical: 12,
              backgroundColor: "rgba(255, 69, 58, 0.1)",
              borderRadius: 12,
              borderWidth: 1,
              borderColor: colors.neon.red,
              marginBottom: 16,
            }}
          >
            <Text style={{ color: colors.neon.red, fontSize: 14 }}>{error}</Text>
          </View>
        )}

        {/* Action Buttons after Results */}
        {(analysisResult || extractedText || objects.length > 0) && (
          <View style={{ flexDirection: "row", gap: 12 }}>
            <TouchableOpacity
              onPress={handleNewAnalysis}
              style={{
                flex: 1,
                backgroundColor: colors.background.card,
                borderRadius: 12,
                padding: 14,
                alignItems: "center",
                borderWidth: 1,
                borderColor: colors.border.default,
              }}
            >
              <Text style={{ color: colors.text.primary, fontWeight: "600" }}>
                Nouvelle image
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => {
                // Reset results but keep image for re-analysis
                setQuestion("");
              }}
              style={{
                flex: 1,
                backgroundColor: colors.neon.cyan,
                borderRadius: 12,
                padding: 14,
                alignItems: "center",
              }}
            >
              <Text style={{ color: colors.background.primary, fontWeight: "600" }}>
                Ré-analyser
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
