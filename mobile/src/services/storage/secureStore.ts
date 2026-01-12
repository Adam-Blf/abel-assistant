/**
 * =============================================================================
 * SECURE_STORE.TS - Secure Token Storage
 * =============================================================================
 * A.B.E.L. Project - Encrypted storage for sensitive data
 * Uses expo-secure-store (Keychain iOS / Keystore Android)
 * =============================================================================
 */

import * as SecureStore from "expo-secure-store";

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: "abel_access_token",
  REFRESH_TOKEN: "abel_refresh_token",
  USER_ID: "abel_user_id",
  BIOMETRIC_ENABLED: "abel_biometric_enabled",
  SESSION_EXPIRY: "abel_session_expiry",
  LAST_ACTIVITY: "abel_last_activity",
} as const;

type StorageKey = (typeof STORAGE_KEYS)[keyof typeof STORAGE_KEYS];

/**
 * Secure storage service for sensitive data
 */
class SecureStorageService {
  /**
   * Store a value securely
   */
  async set(key: StorageKey, value: string): Promise<void> {
    try {
      await SecureStore.setItemAsync(key, value, {
        keychainAccessible: SecureStore.WHEN_UNLOCKED,
      });
    } catch (error) {
      console.error(`[SecureStore] Error setting ${key}:`, error);
      throw new Error(`Failed to store ${key}`);
    }
  }

  /**
   * Retrieve a value from secure storage
   */
  async get(key: StorageKey): Promise<string | null> {
    try {
      return await SecureStore.getItemAsync(key);
    } catch (error) {
      console.error(`[SecureStore] Error getting ${key}:`, error);
      return null;
    }
  }

  /**
   * Delete a value from secure storage
   */
  async delete(key: StorageKey): Promise<void> {
    try {
      await SecureStore.deleteItemAsync(key);
    } catch (error) {
      console.error(`[SecureStore] Error deleting ${key}:`, error);
    }
  }

  /**
   * Store authentication tokens
   */
  async setTokens(accessToken: string, refreshToken?: string): Promise<void> {
    await this.set(STORAGE_KEYS.ACCESS_TOKEN, accessToken);
    if (refreshToken) {
      await this.set(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
    }
    // Set session expiry (15 minutes from now)
    const expiry = Date.now() + 15 * 60 * 1000;
    await this.set(STORAGE_KEYS.SESSION_EXPIRY, expiry.toString());
    await this.updateLastActivity();
  }

  /**
   * Get access token
   */
  async getAccessToken(): Promise<string | null> {
    return this.get(STORAGE_KEYS.ACCESS_TOKEN);
  }

  /**
   * Get refresh token
   */
  async getRefreshToken(): Promise<string | null> {
    return this.get(STORAGE_KEYS.REFRESH_TOKEN);
  }

  /**
   * Clear all authentication data (logout)
   */
  async clearAuth(): Promise<void> {
    await Promise.all([
      this.delete(STORAGE_KEYS.ACCESS_TOKEN),
      this.delete(STORAGE_KEYS.REFRESH_TOKEN),
      this.delete(STORAGE_KEYS.USER_ID),
      this.delete(STORAGE_KEYS.SESSION_EXPIRY),
      this.delete(STORAGE_KEYS.LAST_ACTIVITY),
    ]);
  }

  /**
   * Update last activity timestamp
   */
  async updateLastActivity(): Promise<void> {
    await this.set(STORAGE_KEYS.LAST_ACTIVITY, Date.now().toString());
  }

  /**
   * Check if session is expired (15 min timeout)
   */
  async isSessionExpired(): Promise<boolean> {
    const lastActivity = await this.get(STORAGE_KEYS.LAST_ACTIVITY);
    if (!lastActivity) return true;

    const timeout = 15 * 60 * 1000; // 15 minutes
    return Date.now() - parseInt(lastActivity, 10) > timeout;
  }

  /**
   * Store user ID
   */
  async setUserId(userId: string): Promise<void> {
    await this.set(STORAGE_KEYS.USER_ID, userId);
  }

  /**
   * Get user ID
   */
  async getUserId(): Promise<string | null> {
    return this.get(STORAGE_KEYS.USER_ID);
  }

  /**
   * Enable/disable biometric authentication
   */
  async setBiometricEnabled(enabled: boolean): Promise<void> {
    await this.set(STORAGE_KEYS.BIOMETRIC_ENABLED, enabled ? "true" : "false");
  }

  /**
   * Check if biometric is enabled
   */
  async isBiometricEnabled(): Promise<boolean> {
    const value = await this.get(STORAGE_KEYS.BIOMETRIC_ENABLED);
    return value === "true";
  }
}

// Export singleton instance
export const secureStorage = new SecureStorageService();
export default secureStorage;
