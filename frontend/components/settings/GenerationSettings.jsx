import React, { useState } from 'react';

const GenerationSettings = ({ settings, onSettingsChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const handleTemperatureChange = (e) => {
    const value = parseFloat(e.target.value);
    onSettingsChange({ temperature: value });
  };
  
  const handleMaxTokensChange = (e) => {
    const value = parseInt(e.target.value, 10);
    onSettingsChange({ maxTokens: value });
  };
  
  const toggleOpen = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="settings-container">
      <div className="settings-header" onClick={toggleOpen}>
        <h3>Settings</h3>
        <span>{isOpen ? '▲' : '▼'}</span>
      </div>
      
      {isOpen && (
        <div className="settings-content">
          <div className="slider-container">
            <label className="slider-label">
              Temperature (0 = deterministic, 1 = creative): {settings.temperature.toFixed(1)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.temperature}
              onChange={handleTemperatureChange}
              className="slider"
            />
          </div>
          
          <div className="slider-container">
            <label className="slider-label">
              Max Tokens: {settings.maxTokens}
            </label>
            <input
              type="range"
              min="128"
              max="2048"
              step="128"
              value={settings.maxTokens}
              onChange={handleMaxTokensChange}
              className="slider"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerationSettings;