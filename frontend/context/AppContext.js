import React, { createContext, useContext, useState, useEffect } from 'react';

// Create the context
const AppContext = createContext();

// Context provider component
export const AppProvider = ({ children }) => {
  // Chat state
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Language settings
  const [language, setLanguage] = useState('auto');
  const [detectedLanguage, setDetectedLanguage] = useState('Auto Detect');
  
  // Generation settings
  const [settings, setSettings] = useState({
    temperature: 0.2,
    maxTokens: 1024,
  });
  
  // Notifications and UI state
  const [statusMessage, setStatusMessage] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Theme state (if you want to add light/dark mode toggle)
  const [theme, setTheme] = useState('dark');

  // Clear status message after delay
  useEffect(() => {
    if (statusMessage) {
      const timer = setTimeout(() => {
        setStatusMessage('');
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [statusMessage]);
  
  // Add a message to the chat
  const addMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };
  
  // Clear all messages
  const clearMessages = () => {
    setMessages([]);
    setStatusMessage('Conversation cleared');
  };
  
  // Update language setting and detected language
  const updateLanguage = (newLanguage) => {
    setLanguage(newLanguage);
    if (newLanguage !== 'auto') {
      setDetectedLanguage(newLanguage.charAt(0).toUpperCase() + newLanguage.slice(1));
    } else {
      setDetectedLanguage('Auto Detect');
    }
  };
  
  // Update generation settings
  const updateSettings = (newSettings) => {
    setSettings(prev => ({
      ...prev,
      ...newSettings
    }));
  };
  
  // Toggle sidebar
  const toggleSidebar = () => {
    setSidebarOpen(prev => !prev);
  };
  
  // Toggle theme
  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };
  
  // Context value object
  const contextValue = {
    // State
    messages,
    isLoading,
    language,
    detectedLanguage,
    settings,
    statusMessage,
    sidebarOpen,
    theme,
    
    // Actions
    setMessages,
    setIsLoading,
    addMessage,
    clearMessages,
    updateLanguage,
    updateSettings,
    setStatusMessage,
    toggleSidebar,
    toggleTheme
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook for using the context
export const useAppContext = () => {
  const context = useContext(AppContext);
  
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  
  return context;
};

export default AppContext;