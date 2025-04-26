import React from 'react';

const LanguageSelector = ({ language, detectedLanguage, onLanguageChange }) => {
  const languages = [
    { id: 'auto', label: 'Auto Detect' },
    { id: 'python', label: 'Python' },
    { id: 'powershell', label: 'PowerShell' },
  ];

  return (
    <div className="language-selector">
      <div className="container">
        <div className="row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <p className="section-label">Language</p>
            <div className="language-options">
              {languages.map((lang) => (
                <div
                  key={lang.id}
                  className={`language-option ${language === lang.id ? 'active' : ''}`}
                  onClick={() => onLanguageChange(lang.id)}
                >
                  {lang.label}
                </div>
              ))}
            </div>
          </div>
          <div className="language-indicator">
            <p><strong>Current Language Mode</strong>: {detectedLanguage}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LanguageSelector;