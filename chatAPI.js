// src/utils/chatAPI.js
// Safe API utility that works in both SSR and browser environments
const getAPIBaseUrl = () => {
  // Only access window in browser environment
  if (typeof window !== 'undefined') {
    // For localhost development, use the API server
    if (window.location.hostname === 'localhost') {
      return 'http://localhost:8000';
    } else {
      // For production, use relative path that will be handled by the proxy
      return '';
    }
  }
  // This fallback should not be reached in practice since the chatbot
  // will only be rendered in the browser, but included for completeness
  return '';
};

const API_BASE_URL = getAPIBaseUrl();

export const chatAPI = {
  async sendMessage(messages, userId = null) {
    try {
      const url = API_BASE_URL ? `${API_BASE_URL}/chat` : '/api/chat';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages,
          user_id: userId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message to chat API:', error);
      throw error;
    }
  },

  async sendBookMessage(messages, userId = null) {
    try {
      const url = API_BASE_URL ? `${API_BASE_URL}/book-chat` : '/api/book-chat';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages,
          user_id: userId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message to book chat API:', error);
      throw error;
    }
  },
};