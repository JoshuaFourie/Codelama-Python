import React, { useState, useEffect } from 'react';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-powershell';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-markup';
import 'prismjs/components/prism-css';

const CodeBlock = ({ code, language }) => {
  const [isCopied, setIsCopied] = useState(false);
  
  // Normalize language for Prism
  const normalizeLanguage = (lang) => {
    const langMap = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'html': 'markup',
      'xml': 'markup',
      'sh': 'bash',
      'ps': 'powershell',
      'ps1': 'powershell',
      'plaintext': 'markup'
    };
    
    return langMap[lang.toLowerCase()] || lang.toLowerCase() || 'markup';
  };
  
  // Highlight code when component mounts or code changes
  useEffect(() => {
    Prism.highlightAll();
  }, [code, language]);
  
  // Handle copy to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setIsCopied(true);
      
      // Reset copied state after 2 seconds
      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };
  
  const normalizedLanguage = normalizeLanguage(language);
  const displayLang = language ? language.toUpperCase() : 'CODE';

  return (
    <div className="code-block">
      <div className="code-header">
        <span className="code-language">{displayLang}</span>
        <button className="copy-button" onClick={handleCopy}>
          {isCopied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div className="code-content">
        <pre>
          <code className={`language-${normalizedLanguage}`}>
            {code}
          </code>
        </pre>
      </div>
    </div>
  );
};

export default CodeBlock;