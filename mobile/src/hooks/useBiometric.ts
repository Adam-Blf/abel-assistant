/**
 * =============================================================================
 * USE_BIOMETRIC.TS - Biometric Authentication Hook
 * =============================================================================
 * A.B.E.L. Project - Face ID / Touch ID / Fingerprint support
 * Uses expo-local-authentication
 * =============================================================================
 */

import { useCallback, useEffect, useState } from "react";
import * as LocalAuthentication from "expo-local-authentication";
import { secureStorage } from "@services/storage/secureStore";

export type BiometricType = "fingerprint" | "facial" | "iris" | "none";

interface BiometricState {
  isAvailable: boolean;
  biometricType: BiometricType;
  isEnabled: boolean;
  isEnrolled: boolean;
}

interface UseBiometricReturn extends BiometricState {
  authenticate: (reason?: string) => Promise<boolean>;
  enableBiometric: () => Promise<boolean>;
  disableBiometric: () => Promise<void>;
  checkBiometric: () => Promise<void>;
}

/**
 * Hook for biometric authentication
 */
export function useBiometric(): UseBiometricReturn {
  const [state, setState] = useState<BiometricState>({
    isAvailable: false,
    biometricType: "none",
    isEnabled: false,
    isEnrolled: false,
  });

  /**
   * Check biometric availability and status
   */
  const checkBiometric = useCallback(async () => {
    try {
      // Check hardware support
      const hasHardware = await LocalAuthentication.hasHardwareAsync();

      // Check if enrolled
      const isEnrolled = await LocalAuthentication.isEnrolledAsync();

      // Get supported types
      const supportedTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();

      // Determine biometric type
      let biometricType: BiometricType = "none";
      if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
        biometricType = "facial";
      } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
        biometricType = "fingerprint";
      } else if (supportedTypes.includes(LocalAuthentication.AuthenticationType.IRIS)) {
        biometricType = "iris";
      }

      // Check if user enabled biometric in app
      const isEnabled = await secureStorage.isBiometricEnabled();

      setState({
        isAvailable: hasHardware && isEnrolled,
        biometricType,
        isEnabled,
        isEnrolled,
      });
    } catch (error) {
      console.error("[Biometric] Check failed:", error);
      setState((prev) => ({ ...prev, isAvailable: false }));
    }
  }, []);

  /**
   * Authenticate with biometric
   */
  const authenticate = useCallback(async (reason?: string): Promise<boolean> => {
    try {
      if (!state.isAvailable) {
        console.warn("[Biometric] Not available");
        return false;
      }

      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: reason || "Authentification A.B.E.L.",
        cancelLabel: "Annuler",
        disableDeviceFallback: false,
        fallbackLabel: "Utiliser le code",
      });

      if (result.success) {
        // Update last activity on successful auth
        await secureStorage.updateLastActivity();
        return true;
      }

      console.warn("[Biometric] Auth failed:", result.error);
      return false;
    } catch (error) {
      console.error("[Biometric] Auth error:", error);
      return false;
    }
  }, [state.isAvailable]);

  /**
   * Enable biometric authentication
   */
  const enableBiometric = useCallback(async (): Promise<boolean> => {
    try {
      // First verify user can authenticate
      const success = await authenticate("Activer l'authentification biométrique");

      if (success) {
        await secureStorage.setBiometricEnabled(true);
        setState((prev) => ({ ...prev, isEnabled: true }));
        return true;
      }

      return false;
    } catch (error) {
      console.error("[Biometric] Enable failed:", error);
      return false;
    }
  }, [authenticate]);

  /**
   * Disable biometric authentication
   */
  const disableBiometric = useCallback(async (): Promise<void> => {
    try {
      await secureStorage.setBiometricEnabled(false);
      setState((prev) => ({ ...prev, isEnabled: false }));
    } catch (error) {
      console.error("[Biometric] Disable failed:", error);
    }
  }, []);

  // Check biometric on mount
  useEffect(() => {
    checkBiometric();
  }, [checkBiometric]);

  return {
    ...state,
    authenticate,
    enableBiometric,
    disableBiometric,
    checkBiometric,
  };
}

export default useBiometric;
