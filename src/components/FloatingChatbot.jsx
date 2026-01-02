import React, { useState, useEffect, useRef, useCallback } from 'react';
import styles from './FloatingChatbot.module.css';

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isBackendReady, setIsBackendReady] = useState(false);
  const messagesEndRef = useRef(null);
  const retryCountRef = useRef(0);
  const welcomeMessageShownRef = useRef(false);
  const maxRetries = 3;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend health before first message
  const checkBackendHealth = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      return response.ok && data.status === 'healthy';
    } catch (error) {
      console.error('Backend health check failed:', error);
      return false;
    }
  }, []);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Check if backend is ready before sending
    if (!isBackendReady) {
      const backendHealthy = await checkBackendHealth();
      if (!backendHealthy) {
        const errorMessage = {
          id: Date.now() + 1,
          text: 'Backend server is not ready. Please ensure the backend is running on port 8000.',
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
        return;
      }
      setIsBackendReady(true);
    }

    const userMessage = { id: Date.now(), text: inputValue, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    retryCountRef.current = 0; // Reset retry count for new message

    try {
      // Add timeout to prevent hanging requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          session_id: 'floating-chat-session'
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('API Response:', data); // Debug log

      // Check if the response contains an error message
      if (data.message && data.message.includes('Sorry, I encountered an error processing your request')) {
        const errorMessage = {
          id: Date.now() + 1,
          text: 'The backend service is experiencing issues. The RAG functionality requires valid API keys to be configured.',
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      } else {
        const botMessage = {
          id: Date.now() + 1,
          text: data.message || data.answer || 'I can help you find information about books. What would you like to know?',
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error('Request timeout');
        const errorMessage = {
          id: Date.now() + 1,
          text: 'Request timed out. Please try again.',
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      } else {
        console.error('Error sending message:', error);
        // Check if it's a network error or a backend processing error
        let errorMessageText = 'Sorry, I encountered an error processing your request. Please try again.';

        // If the error is related to backend processing (like RAG errors), provide more specific message
        if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
          errorMessageText = 'Cannot connect to the backend server. Please ensure the backend is running on port 8000.';
        } else if (error.message.includes('500') || error.message.includes('502') || error.message.includes('503')) {
          errorMessageText = 'The backend server is experiencing issues. Please try again later.';
        }

        const errorMessage = {
          id: Date.now() + 1,
          text: errorMessageText,
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const welcomeMessage = {
    id: 1,
    text: "Hello! I'm your book assistant. Ask me about books, authors, genres, or specific titles you're looking for.",
    sender: 'bot',
    timestamp: new Date()
  };

  useEffect(() => {
    if (isOpen && messages.length === 0 && !welcomeMessageShownRef.current) {
      setMessages([welcomeMessage]);
      welcomeMessageShownRef.current = true;
    }
  }, [isOpen, messages.length]);

  return (
    <>
      {/* Floating Chat Button */}
      <button
        className={`${styles.chatButton} ${isOpen ? styles.hidden : styles.visible}`}
        onClick={toggleChat}
        aria-label="Open chat"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H17L14.25 20.74C14.188 20.822 14.111 20.89 14.023 20.94C13.935 20.99 13.838 21.021 13.737 21.031C13.636 21.041 13.533 21.03 13.435 20.999C13.337 20.968 13.246 20.918 13.168 20.85L11.278 19.44C10.628 19.78 9.888 19.98 9.118 20H9C4.03 20 1 16.97 1 12S4.03 4 9 4 17 7.03 17 12C17 12.77 16.86 13.51 16.59 14.19L20.07 17.59C20.36 17.24 20.67 16.91 21 16.59V15Z" fill="white"/>
        </svg>
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatContainer}>
          <div className={styles.chatHeader}>
            <h4>Book Assistant</h4>
            <button
              className={styles.closeButton}
              onClick={toggleChat}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>

          <div className={styles.messagesContainer}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`${styles.message} ${
                  message.sender === 'user' ? styles.userMessage : styles.botMessage
                }`}
              >
                <div className={styles.messageText}>{message.text}</div>
                <div className={styles.messageTime}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className={styles.message + ' ' + styles.botMessage}>
                <div className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className={styles.inputContainer}>
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about books, authors, or genres..."
              className={styles.textInput}
              rows="1"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              className={styles.sendButton}
              disabled={isLoading || !inputValue.trim()}
              aria-label="Send message"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingChatbot;