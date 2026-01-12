/**
 * =============================================================================
 * USEVOICE.TS - Voice Recording & Processing Hook
 * =============================================================================
 * A.B.E.L. Project - Audio recording with expo-av
 * =============================================================================
 */

import { useState, useCallback, useRef, useEffect } from "react";
import { Audio } from "expo-av";
import * as FileSystem from "expo-file-system";
import * as Haptics from "expo-haptics";

import { apiClient } from "@services/api/client";

interface VoiceState {
  isRecording: boolean;
  isProcessing: boolean;
  duration: number;
  transcription: string | null;
  response: string | null;
  error: string | null;
}

interface VoiceResult {
  transcription: string;
  response: string;
  intent: string;
  context_used: boolean;
}

export function useVoice() {
  const [state, setState] = useState<VoiceState>({
    isRecording: false,
    isProcessing: false,
    duration: 0,
    transcription: null,
    response: null,
    error: null,
  });

  const recordingRef = useRef<Audio.Recording | null>(null);
  const durationInterval = useRef<NodeJS.Timeout | null>(null);

  /**
   * Request permissions on mount
   */
  useEffect(() => {
    (async () => {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== "granted") {
        setState((prev) => ({
          ...prev,
          error: "Permission micro refusée",
        }));
      }
    })();

    return () => {
      // Cleanup on unmount
      if (durationInterval.current) {
        clearInterval(durationInterval.current);
      }
      if (recordingRef.current) {
        recordingRef.current.stopAndUnloadAsync().catch(() => {});
      }
    };
  }, []);

  /**
   * Start recording
   */
  const startRecording = useCallback(async () => {
    try {
      // Reset state
      setState((prev) => ({
        ...prev,
        isRecording: false,
        duration: 0,
        transcription: null,
        response: null,
        error: null,
      }));

      // Configure audio mode
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      // Create recording
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      recordingRef.current = recording;

      // Start duration counter
      const startTime = Date.now();
      durationInterval.current = setInterval(() => {
        setState((prev) => ({
          ...prev,
          duration: Math.floor((Date.now() - startTime) / 1000),
        }));
      }, 100);

      // Haptic feedback
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

      setState((prev) => ({ ...prev, isRecording: true }));

      console.log("[Voice] Recording started");
    } catch (error) {
      console.error("[Voice] Start recording error:", error);
      setState((prev) => ({
        ...prev,
        error: "Impossible de démarrer l'enregistrement",
      }));
    }
  }, []);

  /**
   * Stop recording and process
   */
  const stopRecording = useCallback(async (): Promise<VoiceResult | null> => {
    try {
      if (!recordingRef.current) {
        return null;
      }

      // Stop duration counter
      if (durationInterval.current) {
        clearInterval(durationInterval.current);
        durationInterval.current = null;
      }

      setState((prev) => ({
        ...prev,
        isRecording: false,
        isProcessing: true,
      }));

      // Stop recording
      await recordingRef.current.stopAndUnloadAsync();
      const uri = recordingRef.current.getURI();
      recordingRef.current = null;

      // Haptic feedback
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

      if (!uri) {
        throw new Error("No recording URI");
      }

      console.log("[Voice] Recording stopped, URI:", uri);

      // Read file as base64
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });

      // Create form data for upload
      const formData = new FormData();
      formData.append("audio", {
        uri,
        type: "audio/m4a",
        name: "recording.m4a",
      } as any);
      formData.append("use_memory", "true");

      // Send to API
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_API_URL}/api/v1/voice/command`,
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

      const result: VoiceResult = await response.json();

      // Cleanup temp file
      await FileSystem.deleteAsync(uri, { idempotent: true }).catch(() => {});

      setState((prev) => ({
        ...prev,
        isProcessing: false,
        transcription: result.transcription,
        response: result.response,
      }));

      console.log("[Voice] Processing complete:", result.intent);

      return result;
    } catch (error) {
      console.error("[Voice] Stop recording error:", error);
      setState((prev) => ({
        ...prev,
        isRecording: false,
        isProcessing: false,
        error: "Erreur lors du traitement audio",
      }));
      return null;
    }
  }, []);

  /**
   * Cancel recording
   */
  const cancelRecording = useCallback(async () => {
    try {
      if (durationInterval.current) {
        clearInterval(durationInterval.current);
        durationInterval.current = null;
      }

      if (recordingRef.current) {
        await recordingRef.current.stopAndUnloadAsync();
        const uri = recordingRef.current.getURI();
        recordingRef.current = null;

        // Cleanup temp file
        if (uri) {
          await FileSystem.deleteAsync(uri, { idempotent: true }).catch(() => {});
        }
      }

      setState((prev) => ({
        ...prev,
        isRecording: false,
        isProcessing: false,
        duration: 0,
      }));

      console.log("[Voice] Recording cancelled");
    } catch (error) {
      console.error("[Voice] Cancel error:", error);
    }
  }, []);

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    setState({
      isRecording: false,
      isProcessing: false,
      duration: 0,
      transcription: null,
      response: null,
      error: null,
    });
  }, []);

  return {
    ...state,
    startRecording,
    stopRecording,
    cancelRecording,
    reset,
  };
}

export default useVoice;
