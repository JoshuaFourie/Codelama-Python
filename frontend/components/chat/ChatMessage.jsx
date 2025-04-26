import React from 'react';
import CodeBlock from './CodeBlock';

const ChatMessage = ({ message }) => {
  const { role, content } = message;
  
  // Function to detect if content contains code
  const detectCodeBlock = (content) => {
    // Check for markdown code block syntax
    const codeBlockRegex = /```([a-zA-Z0-9]*)\n([\s\S]*?)```/g;
    return codeBlockRegex.test(content);
  };
  
  // Function to render content with code blocks
  const renderContent = (content) => {
    // Parse content for code blocks
    const codeBlockRegex = /```([a-zA-Z0-9]*)\n([\s\S]*?)```/g;
    
    // If no code blocks, return content as is
    if (!detectCodeBlock(content)) {
      return <p>{content}</p>;
    }
    
    // Split content by code blocks
    const parts = [];
    let lastIndex = 0;
    let match;
    
    // Reset regex lastIndex
    codeBlockRegex.lastIndex = 0;
    
    // Extract all code blocks and text parts
    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.slice(lastIndex, match.index)
        });
      }
      
      // Add code block
      parts.push({
        type: 'code',
        language: match[1] || 'plaintext',
        content: match[2]
      });
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text after last code block
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex)
      });
    }
    
    // Render all parts
    return parts.map((part, index) => {
      if (part.type === 'text') {
        return <p key={index}>{part.content}</p>;
      } else {
        return (
          <CodeBlock
            key={index}
            code={part.content}
            language={part.language}
          />
        );
      }
    });
  };

  return (
    <div className={`message message-${role === 'user' ? 'user' : 'bot'}`}>
      {renderContent(content)}
    </div>
  );
};

export default ChatMessage;