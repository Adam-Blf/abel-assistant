/**
 * =============================================================================
 * CLIENT.TS - API Client Service
 * =============================================================================
 * A.B.E.L. Project - Secure HTTP client for backend communication
 * HTTPS strict with automatic token refresh
 * =============================================================================
 */

import { secureStorage } from "@services/storage/secureStore";

// API Configuration
const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";
const API_VERSION = "v1";
const API_TIMEOUT = 30000; // 30 seconds

// Request types
type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestConfig {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: unknown;
  timeout?: number;
  requireAuth?: boolean;
}

interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
}

/**
 * API Error class
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * API Client class for secure communication
 */
class ApiClient {
  private baseUrl: string;
  private refreshPromise: Promise<string | null> | null = null;

  constructor() {
    this.baseUrl = `${API_URL}/api/${API_VERSION}`;
  }

  /**
   * Build headers for request
   */
  private async buildHeaders(requireAuth: boolean): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };

    if (requireAuth) {
      const token = await secureStorage.getAccessToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Handle token refresh
   */
  private async refreshToken(): Promise<string | null> {
    // Prevent multiple concurrent refresh attempts
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      try {
        const refreshToken = await secureStorage.getRefreshToken();
        if (!refreshToken) {
          return null;
        }

        const response = await fetch(`${this.baseUrl}/auth/refresh`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (!response.ok) {
          await secureStorage.clearAuth();
          return null;
        }

        const data = await response.json();
        await secureStorage.setTokens(data.access_token, data.refresh_token);
        return data.access_token;
      } catch (error) {
        console.error("[API] Token refresh failed:", error);
        await secureStorage.clearAuth();
        return null;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  /**
   * Make HTTP request
   */
  private async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const {
      method = "GET",
      body,
      timeout = API_TIMEOUT,
      requireAuth = true,
    } = config;

    const url = `${this.baseUrl}${endpoint}`;
    const headers = await this.buildHeaders(requireAuth);

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      // Update activity on each request
      if (requireAuth) {
        await secureStorage.updateLastActivity();
      }

      const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle 401 - try token refresh
      if (response.status === 401 && requireAuth) {
        const newToken = await this.refreshToken();
        if (newToken) {
          // Retry with new token
          headers["Authorization"] = `Bearer ${newToken}`;
          const retryResponse = await fetch(url, {
            method,
            headers,
            body: body ? JSON.stringify(body) : undefined,
          });

          const retryData = await retryResponse.json();
          return {
            data: retryResponse.ok ? retryData : null,
            error: retryResponse.ok ? null : retryData.message || "Request failed",
            status: retryResponse.status,
          };
        }

        // Refresh failed
        return {
          data: null,
          error: "Session expired. Please login again.",
          status: 401,
        };
      }

      const data = await response.json();

      return {
        data: response.ok ? data : null,
        error: response.ok ? null : data.message || "Request failed",
        status: response.status,
      };
    } catch (error: any) {
      clearTimeout(timeoutId);

      if (error.name === "AbortError") {
        return {
          data: null,
          error: "Request timeout",
          status: 408,
        };
      }

      console.error("[API] Request error:", error);
      return {
        data: null,
        error: error.message || "Network error",
        status: 0,
      };
    }
  }

  // HTTP method shortcuts
  async get<T>(endpoint: string, config?: Omit<RequestConfig, "method" | "body">) {
    return this.request<T>(endpoint, { ...config, method: "GET" });
  }

  async post<T>(endpoint: string, body?: unknown, config?: Omit<RequestConfig, "method">) {
    return this.request<T>(endpoint, { ...config, method: "POST", body });
  }

  async put<T>(endpoint: string, body?: unknown, config?: Omit<RequestConfig, "method">) {
    return this.request<T>(endpoint, { ...config, method: "PUT", body });
  }

  async patch<T>(endpoint: string, body?: unknown, config?: Omit<RequestConfig, "method">) {
    return this.request<T>(endpoint, { ...config, method: "PATCH", body });
  }

  async delete<T>(endpoint: string, config?: Omit<RequestConfig, "method">) {
    return this.request<T>(endpoint, { ...config, method: "DELETE" });
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    const response = await this.get<{ status: string }>("/health", {
      requireAuth: false,
      timeout: 5000,
    });
    return response.data?.status === "healthy";
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
