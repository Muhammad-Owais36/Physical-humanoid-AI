import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';

/**
 * ChatInterface React component for the RAG Chatbot
 * Provides a chat interface that connects to the backend API
 */
const ChatInterface = ({ config = {} }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [sessionId, setSessionId] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Configuration with multiple fallback sources
  const getConfig = () => {
    // Priority order for configuration:
    // 1. Component props (passed configuration)
    // 2. Docusaurus theme config (from window)
    // 3. Environment variables
    // 4. Default values

    const docusaurusConfig = typeof window !== 'undefined' && window.__themeConfig ?
                             window.__themeConfig.apiConfig : {};

    const defaultConfig = {
      apiBaseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      maxMessageLength: 2000,
      retryAttempts: 3,
      retryDelay: 1000,
    };

    // Combine configurations with proper fallbacks
    return {
      apiBaseUrl: config.apiBaseUrl ||
                  docusaurusConfig.baseUrl ||
                  defaultConfig.apiBaseUrl,
      timeout: config.timeout ||
               docusaurusConfig.timeout ||
               defaultConfig.timeout,
      maxMessageLength: config.maxMessageLength ||
                        defaultConfig.maxMessageLength,
      retryAttempts: config.retryAttempts ||
                     docusaurusConfig.retryAttempts ||
                     defaultConfig.retryAttempts,
      retryDelay: config.retryDelay ||
                  docusaurusConfig.retryDelay ||
                  defaultConfig.retryDelay,
    };
  };

  const chatConfig = getConfig();

  // Function to scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat session and load history on component mount
  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Check API connectivity
        const response = await fetch(`${chatConfig.apiBaseUrl}/health`);
        if (response.ok) {
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('error');
        }

        // Add welcome message
        setMessages([
          {
            id: 'welcome',
            role: 'assistant',
            content: 'Hello! I\'m your RAG chatbot assistant. Ask me anything about the book content.',
            timestamp: new Date(),
          }
        ]);

        setIsInitialized(true);
      } catch (err) {
        setConnectionStatus('error');
        console.error('Chat initialization failed:', err);

        // Still add welcome message even if connection failed
        setMessages([
          {
            id: 'welcome',
            role: 'assistant',
            content: 'Hello! I\'m your RAG chatbot assistant. Ask me anything about the book content.',
            timestamp: new Date(),
          }
        ]);

        setError('Unable to connect to the backend service. Some features may not work properly.');
        setIsInitialized(true);
      }
    };

    initializeChat();
  }, [chatConfig.apiBaseUrl]);

  // Function to validate input before sending
  const validateInput = (value) => {
    if (!value || !value.trim()) {
      return 'Message cannot be empty';
    }

    if (value.length > chatConfig.maxMessageLength) {
      return `Message too long. Maximum ${chatConfig.maxMessageLength} characters.`;
    }

    // Check for potentially harmful content
    if (/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi.test(value)) {
      return 'Message contains invalid content';
    }

    return null; // Valid
  };

  // Function to send message to backend with enhanced error handling
  const sendMessage = async () => {
    if (isLoading) {
      return;
    }

    const validationError = validateInput(inputValue);
    if (validationError) {
      setError(validationError);
      return;
    }

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), chatConfig.timeout);

      const response = await fetch(`${chatConfig.apiBaseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          session_id: sessionId,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Update session ID if new one was provided
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const botMessage = {
        id: `bot-${Date.now()}`,
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
        sources: data.sources || [],
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error sending message:', err);

      // Handle different types of errors
      let errorMessage = 'Failed to send message';
      if (err.name === 'AbortError') {
        errorMessage = 'Request timeout. Please try again.';
      } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
        errorMessage = 'Network error. Please check your connection.';
      } else if (err.message.includes('404')) {
        errorMessage = 'Chat endpoint not found. Please check the API configuration.';
      } else {
        errorMessage = `Failed to send message: ${err.message}`;
      }

      setError(errorMessage);

      // Add error message to chat
      const errorMessageObj = {
        id: `error-${Date.now()}`,
        role: 'system',
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessageObj]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  // Handle key down in input
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Render message content with source citations
  const renderMessageContent = (message) => {
    if (message.isError) {
      return <div className="error-message">{message.content}</div>;
    }

    return (
      <div>
        <div className="message-text">{message.content}</div>
        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <strong>Sources:</strong>
            <ul>
              {message.sources.map((source, index) => (
                <li key={index}>
                  <a href={source} target="_blank" rel="noopener noreferrer">
                    {source}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="chat-interface" role="main" aria-label="RAG Chat Interface">
      <div className="chat-header" role="banner">
        <h3 id="chat-title">RAG Chatbot</h3>
        <div
          className={`connection-status ${connectionStatus}`}
          aria-label={`Connection status: ${connectionStatus}`}
          role="status"
          aria-live="polite"
        >
          <span className="status-indicator" aria-hidden="true"></span>
          <span className="status-text">
            {connectionStatus === 'connected' ? 'Connected' :
             connectionStatus === 'error' ? 'Connection Error' : 'Connecting...'}
          </span>
          <button
            className="refresh-connection"
            onClick={async () => {
              try {
                const response = await fetch(`${chatConfig.apiBaseUrl}/health`);
                if (response.ok) {
                  setConnectionStatus('connected');
                  setError(null);
                } else {
                  setConnectionStatus('error');
                }
              } catch (err) {
                setConnectionStatus('error');
                setError('Unable to connect to the backend service.');
              }
            }}
            title="Refresh connection"
            aria-label="Refresh connection"
          >
            <span aria-hidden="true">↻</span>
          </button>
        </div>
      </div>

      <div
        className="chat-messages"
        aria-live="polite"
        aria-relevant="additions"
        aria-labelledby="chat-title"
      >
        {messages.length === 0 ? (
          <div className="welcome-message" role="status" aria-live="polite">
            <p>Hello! I'm your RAG chatbot assistant. Ask me anything about the book content.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.role} ${message.isError ? 'error' : ''}`}
              role="listitem"
              aria-label={`${message.role} message: ${message.content.substring(0, 50)}${message.content.length > 50 ? '...' : ''}`}
            >
              <div className="message-content">
                {renderMessageContent(message)}
              </div>
              <div className="message-timestamp" aria-label={`Sent at ${message.timestamp ? message.timestamp.toLocaleTimeString() : ''}`}>
                {message.timestamp ? message.timestamp.toLocaleTimeString() : ''}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message bot" role="status" aria-live="polite">
            <div className="message-content">
              <div className="typing-indicator" aria-label="Assistant is typing">
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      {error && (
        <div className="chat-error" role="alert" aria-live="assertive">
          {error}
        </div>
      )}

      <form className="chat-input-form" onSubmit={handleSubmit} role="form" aria-label="Chat input form">
        <label htmlFor="chat-input" className="sr-only">Type your message</label>
        <textarea
          id="chat-input"
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the book content..."
          disabled={isLoading}
          rows="1"
          className="chat-input"
          aria-required="true"
          aria-invalid={!!error}
          aria-describedby={error ? "chat-error" : undefined}
        />
        <button
          type="submit"
          disabled={isLoading || !inputValue.trim()}
          className="chat-send-button"
          aria-label="Send message"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>

      {/* Screen reader only element for errors */}
      {error && (
        <div id="chat-error" className="sr-only" aria-live="assertive">
          Error: {error}
        </div>
      )}
    </div>
  );
};

export default ChatInterface;