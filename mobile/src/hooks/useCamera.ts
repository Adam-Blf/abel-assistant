/**
 * =============================================================================
 * USECAMERA.TS - Camera & Vision Hook
 * =============================================================================
 * A.B.E.L. Project - Camera capture and image analysis
 * =============================================================================
 */

import { useState, useCallback, useRef } from "react";
import { CameraView, CameraType, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system";
import * as Haptics from "expo-haptics";

interface VisionState {
  isCapturing: boolean;
  isAnalyzing: boolean;
  lastImage: string | null;
  analysis: string | null;
  objects: Array<{ name: string; category: string; description: string }>;
  extractedText: string | null;
  error: string | null;
}

interface AnalysisResult {
  description: string;
  has_text: boolean;
  question?: string;
}

interface ObjectsResult {
  objects: Array<{ name: string; category: string; description: string }>;
  count: number;
}

interface OcrResult {
  text: string;
  has_text: boolean;
}

export function useCamera() {
  const [permission, requestPermission] = useCameraPermissions();
  const [state, setState] = useState<VisionState>({
    isCapturing: false,
    isAnalyzing: false,
    lastImage: null,
    analysis: null,
    objects: [],
    extractedText: null,
    error: null,
  });

  const cameraRef = useRef<CameraView>(null);
  const [facing, setFacing] = useState<CameraType>("back");

  /**
   * Toggle camera facing
   */
  const toggleFacing = useCallback(() => {
    setFacing((current) => (current === "back" ? "front" : "back"));
  }, []);

  /**
   * Take photo with camera
   */
  const takePhoto = useCallback(async (): Promise<string | null> => {
    try {
      if (!cameraRef.current) {
        setState((prev) => ({ ...prev, error: "Caméra non disponible" }));
        return null;
      }

      setState((prev) => ({
        ...prev,
        isCapturing: true,
        error: null,
      }));

      // Haptic feedback
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.8,
        base64: true,
        exif: false,
      });

      if (!photo?.uri) {
        throw new Error("No photo captured");
      }

      setState((prev) => ({
        ...prev,
        isCapturing: false,
        lastImage: photo.uri,
      }));

      console.log("[Camera] Photo captured:", photo.uri);

      return photo.uri;
    } catch (error) {
      console.error("[Camera] Take photo error:", error);
      setState((prev) => ({
        ...prev,
        isCapturing: false,
        error: "Erreur lors de la capture",
      }));
      return null;
    }
  }, []);

  /**
   * Pick image from gallery
   */
  const pickImage = useCallback(async (): Promise<string | null> => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        quality: 0.8,
      });

      if (result.canceled || !result.assets[0]?.uri) {
        return null;
      }

      const uri = result.assets[0].uri;
      setState((prev) => ({ ...prev, lastImage: uri }));

      console.log("[Camera] Image picked:", uri);

      return uri;
    } catch (error) {
      console.error("[Camera] Pick image error:", error);
      setState((prev) => ({
        ...prev,
        error: "Erreur lors de la sélection",
      }));
      return null;
    }
  }, []);

  /**
   * Analyze image
   */
  const analyzeImage = useCallback(
    async (imageUri: string, question?: string): Promise<AnalysisResult | null> => {
      try {
        setState((prev) => ({
          ...prev,
          isAnalyzing: true,
          error: null,
        }));

        // Create form data
        const formData = new FormData();
        formData.append("image", {
          uri: imageUri,
          type: "image/jpeg",
          name: "photo.jpg",
        } as any);

        if (question) {
          formData.append("question", question);
        }

        // Send to API
        const response = await fetch(
          `${process.env.EXPO_PUBLIC_API_URL}/api/v1/vision/analyze`,
          {
            method: "POST",
            body: formData,
            headers: {
              Accept: "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const result: AnalysisResult = await response.json();

        setState((prev) => ({
          ...prev,
          isAnalyzing: false,
          analysis: result.description,
        }));

        console.log("[Camera] Analysis complete");

        return result;
      } catch (error) {
        console.error("[Camera] Analysis error:", error);
        setState((prev) => ({
          ...prev,
          isAnalyzing: false,
          error: "Erreur lors de l'analyse",
        }));
        return null;
      }
    },
    []
  );

  /**
   * Identify objects in image
   */
  const identifyObjects = useCallback(
    async (imageUri: string): Promise<ObjectsResult | null> => {
      try {
        setState((prev) => ({
          ...prev,
          isAnalyzing: true,
          error: null,
        }));

        const formData = new FormData();
        formData.append("image", {
          uri: imageUri,
          type: "image/jpeg",
          name: "photo.jpg",
        } as any);

        const response = await fetch(
          `${process.env.EXPO_PUBLIC_API_URL}/api/v1/vision/objects`,
          {
            method: "POST",
            body: formData,
            headers: {
              Accept: "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const result: ObjectsResult = await response.json();

        setState((prev) => ({
          ...prev,
          isAnalyzing: false,
          objects: result.objects,
        }));

        console.log("[Camera] Objects identified:", result.count);

        return result;
      } catch (error) {
        console.error("[Camera] Object detection error:", error);
        setState((prev) => ({
          ...prev,
          isAnalyzing: false,
          error: "Erreur lors de la détection",
        }));
        return null;
      }
    },
    []
  );

  /**
   * Extract text from image (OCR)
   */
  const extractText = useCallback(
    async (imageUri: string): Promise<OcrResult | null> => {
      try {
        setState((prev) => ({
          ...prev,
          isAnalyzing: true,
          error: null,
        }));

        const formData = new FormData();
        formData.append("image", {
          uri: imageUri,
          type: "image/jpeg",
          name: "photo.jpg",
        } as any);

        const response = await fetch(
          `${process.env.EXPO_PUBLIC_API_URL}/api/v1/vision/ocr`,
          {
            method: "POST",
            body: formData,
            headers: {
              Accept: "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const result: OcrResult = await response.json();

        setState((prev) => ({
          ...prev,
          isAnalyzing: false,
          extractedText: result.text,
        }));

        console.log("[Camera] Text extracted:", result.has_text);

        return result;
      } catch (error) {
        console.error("[Camera] OCR error:", error);
        setState((prev) => ({
          ...prev,
          isAnalyzing: false,
          error: "Erreur lors de l'extraction du texte",
        }));
        return null;
      }
    },
    []
  );

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    setState({
      isCapturing: false,
      isAnalyzing: false,
      lastImage: null,
      analysis: null,
      objects: [],
      extractedText: null,
      error: null,
    });
  }, []);

  /**
   * Cleanup temp files
   */
  const cleanup = useCallback(async () => {
    if (state.lastImage) {
      await FileSystem.deleteAsync(state.lastImage, { idempotent: true }).catch(
        () => {}
      );
    }
    reset();
  }, [state.lastImage, reset]);

  return {
    // State
    ...state,
    permission,
    facing,
    cameraRef,

    // Actions
    requestPermission,
    toggleFacing,
    takePhoto,
    pickImage,
    analyzeImage,
    identifyObjects,
    extractText,
    reset,
    cleanup,
  };
}

export default useCamera;
