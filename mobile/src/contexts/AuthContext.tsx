/**
 * =============================================================================
 * AUTH_CONTEXT.TSX - Authentication Context Provider
 * =============================================================================
 * A.B.E.L. Project - Global authentication state management
 * Handles login, logout, token refresh, and session management
 * =============================================================================
 */

import React, {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useState,
  useMemo,
  ReactNode,
} from "react";
import { secureStorage } from "@services/storage/secureStore";
import { apiClient } from "@services/api/client";
import { useSessionTimeout } from "@hooks/useSessionTimeout";

// User type
interface User {
  id: string;
  email: string;
  name?: string;
}

// Auth state
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Auth context value
interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name?: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<boolean>;
}

// Create context
const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Auth Provider component
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  /**
   * Handle session timeout
   */
  const handleTimeout = useCallback(async () => {
    console.log("[Auth] Session timeout - logging out");
    await secureStorage.clearAuth();
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  // Session timeout hook
  const { resetActivity } = useSessionTimeout({
    timeout: 15 * 60 * 1000, // 15 minutes
    onTimeout: handleTimeout,
    enabled: state.isAuthenticated,
  });

  /**
   * Check existing session on mount
   */
  const checkSession = useCallback(async () => {
    try {
      const token = await secureStorage.getAccessToken();
      const isExpired = await secureStorage.isSessionExpired();

      if (!token || isExpired) {
        await secureStorage.clearAuth();
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
        return;
      }

      // Verify token with backend
      const response = await apiClient.get<User>("/auth/me");

      if (response.data) {
        setState({
          user: response.data,
          isAuthenticated: true,
          isLoading: false,
        });
        await resetActivity();
      } else {
        await secureStorage.clearAuth();
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    } catch (error) {
      console.error("[Auth] Session check failed:", error);
      await secureStorage.clearAuth();
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, [resetActivity]);

  useEffect(() => {
    checkSession();
  }, [checkSession]);

  /**
   * Login with email and password
   */
  const login = useCallback(
    async (email: string, password: string): Promise<boolean> => {
      try {
        setState((prev) => ({ ...prev, isLoading: true }));

        const response = await apiClient.post<{
          access_token: string;
          refresh_token: string;
          user: User;
        }>(
          "/auth/login",
          { email, password },
          { requireAuth: false }
        );

        if (response.data) {
          await secureStorage.setTokens(
            response.data.access_token,
            response.data.refresh_token
          );
          await secureStorage.setUserId(response.data.user.id);

          setState({
            user: response.data.user,
            isAuthenticated: true,
            isLoading: false,
          });

          await resetActivity();
          return true;
        }

        setState((prev) => ({ ...prev, isLoading: false }));
        return false;
      } catch (error) {
        console.error("[Auth] Login failed:", error);
        setState((prev) => ({ ...prev, isLoading: false }));
        return false;
      }
    },
    [resetActivity]
  );

  /**
   * Register new user
   */
  const register = useCallback(
    async (email: string, password: string, name?: string): Promise<boolean> => {
      try {
        setState((prev) => ({ ...prev, isLoading: true }));

        const response = await apiClient.post<{
          access_token: string;
          refresh_token: string;
          user: User;
        }>(
          "/auth/register",
          { email, password, name },
          { requireAuth: false }
        );

        if (response.data) {
          await secureStorage.setTokens(
            response.data.access_token,
            response.data.refresh_token
          );
          await secureStorage.setUserId(response.data.user.id);

          setState({
            user: response.data.user,
            isAuthenticated: true,
            isLoading: false,
          });

          await resetActivity();
          return true;
        }

        setState((prev) => ({ ...prev, isLoading: false }));
        return false;
      } catch (error) {
        console.error("[Auth] Register failed:", error);
        setState((prev) => ({ ...prev, isLoading: false }));
        return false;
      }
    },
    [resetActivity]
  );

  /**
   * Logout user
   */
  const logout = useCallback(async (): Promise<void> => {
    try {
      // Notify backend (optional, non-blocking)
      apiClient.post("/auth/logout").catch(() => {});

      await secureStorage.clearAuth();
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    } catch (error) {
      console.error("[Auth] Logout error:", error);
      // Still clear local state
      await secureStorage.clearAuth();
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  /**
   * Refresh session manually
   */
  const refreshSession = useCallback(async (): Promise<boolean> => {
    await resetActivity();
    return true;
  }, [resetActivity]);

  // Memoize context value
  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      register,
      logout,
      refreshSession,
    }),
    [state, login, register, logout, refreshSession]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access auth context
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

export default AuthContext;
