/**
 * API Client for RAG Chatbot Service
 * Handles communication between frontend and backend API
 */

class ApiClient {
  constructor(config = {}) {
    // Configuration with fallbacks in order of priority:
    // 1. Constructor config parameter
    // 2. Environment variable
    // 3. Fallback based on NODE_ENV
    // 4. Default value
    this.baseUrl = config.baseUrl ||
                   (typeof process !== 'undefined' && process.env?.REACT_APP_API_BASE_URL) ||
                   (typeof window !== 'undefined' && window.APP_CONFIG?.apiBaseUrl) ||
                   'http://localhost:8000';

    this.timeout = config.timeout ||
                   (typeof process !== 'undefined' && process.env?.REACT_APP_API_TIMEOUT && parseInt(process.env.REACT_APP_API_TIMEOUT)) ||
                   30000; // 30 seconds default timeout

    this.retryAttempts = config.retryAttempts ||
                         (typeof process !== 'undefined' && process.env?.REACT_APP_API_RETRY_ATTEMPTS && parseInt(process.env.REACT_APP_API_RETRY_ATTEMPTS)) ||
                         3;

    this.retryDelay = config.retryDelay ||
                      (typeof process !== 'undefined' && process.env?.REACT_APP_API_RETRY_DELAY && parseInt(process.env.REACT_APP_API_RETRY_DELAY)) ||
                      1000; // 1 second default
  }

  /**
   * Makes an API request with proper error handling and retry logic
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: this.timeout,
    };

    const requestOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    };

    // Implement retry logic
    let lastError;
    for (let attempt = 0; attempt <= this.retryAttempts; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          // Don't retry on 4xx client errors (except 408, 409, 429)
          if (response.status >= 400 && response.status < 500 &&
              ![408, 409, 429].includes(response.status)) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
          }
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        lastError = error;

        // If this was the last attempt, throw the error
        if (attempt === this.retryAttempts) {
          break;
        }

        // Check if it's a timeout or network error that might be worth retrying
        if (error.name === 'AbortError' || error.message.includes('fetch')) {
          console.warn(`Request failed (attempt ${attempt + 1}), retrying in ${this.retryDelay}ms...`, error.message);
          await this.delay(this.retryDelay);
          continue;
        }

        // For other errors, break out of retry loop
        break;
      }
    }

    // If we get here, all retries failed
    if (lastError.name === 'AbortError') {
      throw new Error('Request timeout after ' + this.retryAttempts + ' retry attempts');
    }
    throw lastError;
  }

  /**
   * Delay helper function for retry logic
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Send a chat message to the backend
   */
  async sendChatMessage(message, options = {}) {
    const payload = {
      message: message,
      ...options,
    };

    return this.makeRequest('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get chat history for a session
   */
  async getChatHistory(sessionId) {
    return this.makeRequest(`/api/v1/chat/history/${sessionId}`);
  }

  /**
   * Create a new chat session
   */
  async createChatSession(options = {}) {
    return this.makeRequest('/api/v1/chat/session', {
      method: 'POST',
      body: JSON.stringify(options),
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Health check to verify backend connectivity
   */
  async checkHealth() {
    return this.makeRequest('/health');
  }
}

// Export a singleton instance with default configuration
const apiClient = new ApiClient();

export default apiClient;

// For environments that don't support ES6 modules
if (typeof window !== 'undefined') {
  window.ApiClient = apiClient;
}