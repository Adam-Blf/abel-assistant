/**
 * =============================================================================
 * USE_SESSION_TIMEOUT.TS - Session Timeout Management
 * =============================================================================
 * A.B.E.L. Project - 15 minute inactivity auto-logout
 * =============================================================================
 */

import { useCallback, useEffect, useRef } from "react";
import { AppState, AppStateStatus } from "react-native";
import { secureStorage } from "@services/storage/secureStore";

interface UseSessionTimeoutOptions {
  /** Timeout in milliseconds (default: 15 minutes) */
  timeout?: number;
  /** Callback when session expires */
  onTimeout: () => void;
  /** Whether session management is enabled */
  enabled?: boolean;
}

interface UseSessionTimeoutReturn {
  /** Reset the activity timer */
  resetActivity: () => Promise<void>;
  /** Check if session is expired */
  checkSession: () => Promise<boolean>;
  /** Get remaining time in milliseconds */
  getRemainingTime: () => Promise<number>;
}

const DEFAULT_TIMEOUT = 15 * 60 * 1000; // 15 minutes

/**
 * Hook for managing session timeout with 15-minute inactivity limit
 */
export function useSessionTimeout({
  timeout = DEFAULT_TIMEOUT,
  onTimeout,
  enabled = true,
}: UseSessionTimeoutOptions): UseSessionTimeoutReturn {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const appStateRef = useRef<AppStateStatus>(AppState.currentState);

  /**
   * Clear existing timeout
   */
  const clearSessionTimeout = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  /**
   * Reset activity timer
   */
  const resetActivity = useCallback(async () => {
    if (!enabled) return;

    clearSessionTimeout();
    await secureStorage.updateLastActivity();

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      console.log("[Session] Timeout reached - logging out");
      onTimeout();
    }, timeout);
  }, [enabled, timeout, onTimeout, clearSessionTimeout]);

  /**
   * Check if session is expired
   */
  const checkSession = useCallback(async (): Promise<boolean> => {
    const isExpired = await secureStorage.isSessionExpired();

    if (isExpired && enabled) {
      onTimeout();
      return true;
    }

    return isExpired;
  }, [enabled, onTimeout]);

  /**
   * Get remaining time until timeout
   */
  const getRemainingTime = useCallback(async (): Promise<number> => {
    const lastActivity = await secureStorage.get("abel_last_activity" as any);
    if (!lastActivity) return 0;

    const elapsed = Date.now() - parseInt(lastActivity, 10);
    const remaining = timeout - elapsed;

    return Math.max(0, remaining);
  }, [timeout]);

  /**
   * Handle app state changes (background/foreground)
   */
  useEffect(() => {
    if (!enabled) return;

    const handleAppStateChange = async (nextState: AppStateStatus) => {
      const previousState = appStateRef.current;
      appStateRef.current = nextState;

      if (nextState === "active" && previousState !== "active") {
        // App came to foreground - check session
        console.log("[Session] App resumed - checking session");
        const isExpired = await checkSession();

        if (!isExpired) {
          // Reset timer if session still valid
          await resetActivity();
        }
      } else if (nextState === "background") {
        // App went to background - clear timeout
        clearSessionTimeout();
      }
    };

    const subscription = AppState.addEventListener("change", handleAppStateChange);

    return () => {
      subscription.remove();
      clearSessionTimeout();
    };
  }, [enabled, checkSession, resetActivity, clearSessionTimeout]);

  // Initial session check on mount
  useEffect(() => {
    if (enabled) {
      checkSession();
    }
  }, [enabled, checkSession]);

  return {
    resetActivity,
    checkSession,
    getRemainingTime,
  };
}

export default useSessionTimeout;
