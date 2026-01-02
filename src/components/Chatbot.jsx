import React, { useState, useRef, useEffect, useCallback } from 'react';
import styles from './Chatbot.module.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isBackendReady, setIsBackendReady] = useState(false);
  const messagesEndRef = useRef(null);
  const retryCountRef = useRef(0);
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

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Check if backend is ready before sending
    if (!isBackendReady) {
      const backendHealthy = await checkBackendHealth();
      if (!backendHealthy) {
        const errorMessage = {
          id: Date.now() + 1,
          text: 'Backend server is not ready. Please ensure the backend is running on port 8000.',
          sender: 'bot'
        };
        setMessages(prev => [...prev, errorMessage]);
        return;
      }
      setIsBackendReady(true);
    }

    const userMessage = { id: Date.now(), text: inputValue, sender: 'user' };
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
          session_id: 'docusaurus-chat-session'
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Check if the response contains an error message
      if (data.message && data.message.includes('Sorry, I encountered an error processing your request')) {
        const errorMessage = {
          id: Date.now() + 1,
          text: 'The backend service is experiencing issues. The RAG functionality requires valid API keys to be configured.',
          sender: 'bot'
        };
        setMessages(prev => [...prev, errorMessage]);
      } else {
        const botMessage = {
          id: Date.now() + 1,
          text: data.message || data.answer || 'Sorry, I could not understand that.',
          sender: 'bot'
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error('Request timeout');
        const errorMessage = {
          id: Date.now() + 1,
          text: 'Request timed out. Please try again.',
          sender: 'bot'
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
          sender: 'bot'
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

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h3>Chat with AI Assistant</h3>
      </div>

      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div className={styles.welcomeMessage}>
            <p>Hello! How can I help you today?</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`${styles.message} ${
                message.sender === 'user' ? styles.userMessage : styles.botMessage
              }`}
            >
              <div className={styles.messageText}>{message.text}</div>
            </div>
          ))
        )}
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
          placeholder="Type your message here..."
          className={styles.textInput}
          rows="3"
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          className={styles.sendButton}
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default Chatbot;