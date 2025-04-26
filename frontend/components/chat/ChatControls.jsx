import React, { useState, useRef, useEffect } from 'react';
import Button from '../ui/Button';

const ChatControls = ({ onSendMessage, isLoading }) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef(null);
  
  // Adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);
  
  // Handle input change
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };
  
  // Handle send message
  const handleSendMessage = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue);
      setInputValue('');
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };
  
  // Handle key press (Ctrl+Enter to send)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="input-container">
      <textarea
        ref={textareaRef}
        className="input-textarea"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        placeholder="Ask me to write some Python or PowerShell code..."
        disabled={isLoading}
        rows={1}
      />
      <Button
        className="button-primary"
        onClick={handleSendMessage}
        disabled={isLoading || !inputValue.trim()}
      >
        {isLoading ? 'Generating...' : 'Send'}
      </Button>
    </div>
  );
};

export default ChatControls;