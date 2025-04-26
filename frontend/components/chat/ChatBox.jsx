import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatControls from './ChatControls';
import LanguageSelector from './LanguageSelector';
import GenerationSettings from '../settings/GenerationSettings';
import Button from '../ui/Button';

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [language, setLanguage] = useState('auto');
  const [detectedLanguage, setDetectedLanguage] = useState('Auto Detect');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    temperature: 0.2,
    maxTokens: 1024,
  });
  const [statusMessage, setStatusMessage] = useState('');
  
  const messagesEndRef = useRef(null);
  
  // Automatically scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // Function to detect language from prompt
  const detectLanguage = (prompt) => {
    // Simple language detection based on keywords (you can expand this)
    const promptLower = prompt.toLowerCase();
    
    const powershellKeywords = [
      'get-', 'set-', 'new-', 'remove-', 'invoke-',
      'windows', 'azure', 'active directory',
      'powershell', 'cmdlet'
    ];
    
    if (powershellKeywords.some(keyword => promptLower.includes(keyword))) {
      return 'powershell';
    }
    
    // Default to Python
    return 'python';
  };
  
  // Handle message sending
  const handleSendMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: message 
    }]);
    
    // Set loading state
    setIsLoading(true);
    setError(null);
    
    try {
      // Auto-detect language if set to auto
      let languageToUse = language;
      if (language === 'auto') {
        languageToUse = detectLanguage(message);
        setDetectedLanguage(languageToUse.charAt(0).toUpperCase() + languageToUse.slice(1));
      }
      
      // Make API request to your backend
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: message,
          language: languageToUse,
          temperature: settings.temperature,
          max_tokens: settings.maxTokens,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate code');
      }
      
      const data = await response.json();
      
      // Add bot response
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response,
        language: languageToUse
      }]);
    } catch (err) {
      console.error('Error generating code:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle language change
  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    if (newLanguage !== 'auto') {
      setDetectedLanguage(newLanguage.charAt(0).toUpperCase() + newLanguage.slice(1));
    } else {
      setDetectedLanguage('Auto Detect');
    }
  };
  
  // Handle settings change
  const handleSettingsChange = (newSettings) => {
    setSettings(prev => ({
      ...prev,
      ...newSettings
    }));
  };
  
  // Clear conversation
  const handleClearConversation = () => {
    setMessages([]);
    setStatusMessage('Conversation cleared');
    
    // Clear status message after 3 seconds
    setTimeout(() => {
      setStatusMessage('');
    }, 3000);
  };
  
  // Save positive feedback
  const handlePositiveFeedback = async () => {
    if (messages.length < 2) {
      setStatusMessage('No conversation to provide feedback on');
      return;
    }
    
    try {
      // Get last user and bot messages
      const lastUserMessage = messages.filter(m => m.role === 'user').pop();
      const lastBotMessage = messages.filter(m => m.role === 'assistant').pop();
      
      if (!lastUserMessage || !lastBotMessage) {
        setStatusMessage('Incomplete conversation for feedback');
        return;
      }
      
      // Send feedback to API
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: lastUserMessage.content,
          solution: lastBotMessage.content,
          type: 'positive',
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save feedback');
      }
      
      setStatusMessage('Positive feedback saved');
    } catch (err) {
      console.error('Error saving feedback:', err);
      setStatusMessage(`Error: ${err.message}`);
    }
    
    // Clear status message after 3 seconds
    setTimeout(() => {
      setStatusMessage('');
    }, 3000);
  };
  
  // Save negative feedback
  const handleNegativeFeedback = async () => {
    if (messages.length < 2) {
      setStatusMessage('No conversation to provide feedback on');
      return;
    }
    
    try {
      // Get last user and bot messages
      const lastUserMessage = messages.filter(m => m.role === 'user').pop();
      const lastBotMessage = messages.filter(m => m.role === 'assistant').pop();
      
      if (!lastUserMessage || !lastBotMessage) {
        setStatusMessage('Incomplete conversation for feedback');
        return;
      }
      
      // Send feedback to API
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: lastUserMessage.content,
          solution: lastBotMessage.content,
          type: 'negative',
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save feedback');
      }
      
      setStatusMessage('Negative feedback saved');
    } catch (err) {
      console.error('Error saving feedback:', err);
      setStatusMessage(`Error: ${err.message}`);
    }
    
    // Clear status message after 3 seconds
    setTimeout(() => {
      setStatusMessage('');
    }, 3000);
  };
  
  // Save example for learning
  const handleLearnFromResponse = async () => {
    if (messages.length < 2) {
      setStatusMessage('No conversation to learn from');
      return;
    }
    
    try {
      // Get last user and bot messages
      const lastUserMessage = messages.filter(m => m.role === 'user').pop();
      const lastBotMessage = messages.filter(m => m.role === 'assistant').pop();
      
      if (!lastUserMessage || !lastBotMessage) {
        setStatusMessage('Incomplete conversation to learn from');
        return;
      }
      
      // Send training example to API
      const response = await fetch('/api/training', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: lastUserMessage.content,
          solution: lastBotMessage.content,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save training example');
      }
      
      setStatusMessage('Training example saved');
    } catch (err) {
      console.error('Error saving training example:', err);
      setStatusMessage(`Error: ${err.message}`);
    }
    
    // Clear status message after 3 seconds
    setTimeout(() => {
      setStatusMessage('');
    }, 3000);
  };

  return (
    <div className="chat-section">
      <LanguageSelector 
        language={language} 
        detectedLanguage={detectedLanguage}
        onLanguageChange={handleLanguageChange} 
      />
      
      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
                Start a conversation by sending a message below.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage 
                key={index} 
                message={message} 
              />
            ))
          )}
          
          {isLoading && (
            <div className="message message-bot">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          {error && (
            <div className="message message-error">
              Error: {error}
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <ChatControls 
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
      
      <GenerationSettings 
        settings={settings}
        onSettingsChange={handleSettingsChange}
      />
      
      <div className="action-buttons">
        <Button onClick={handleClearConversation}>
          Clear Conversation
        </Button>
        <Button onClick={handleLearnFromResponse}>
          Learn from Current Response
        </Button>
      </div>
      
      <div className="feedback-buttons">
        <Button onClick={handlePositiveFeedback}>
          👍 Like
        </Button>
        <Button onClick={handleNegativeFeedback}>
          👎 Dislike
        </Button>
      </div>
      
      {statusMessage && (
        <div className="status-message">
          {statusMessage}
        </div>
      )}
    </div>
  );
};

export default ChatBox;