import React, { useState, useEffect, useRef } from 'react';

/**
 * Slider component with custom styling
 * 
 * @param {Object} props - Component props
 * @param {number} props.min - Minimum value
 * @param {number} props.max - Maximum value
 * @param {number} props.step - Step increment
 * @param {number} props.value - Current value
 * @param {Function} props.onChange - Change handler function
 * @param {string} props.label - Label text
 * @param {boolean} props.showValue - Whether to show value
 * @param {string} props.valuePrefix - Prefix for displayed value
 * @param {string} props.valueSuffix - Suffix for displayed value
 * @param {string} props.className - Additional CSS classes
 * @param {number} props.decimals - Number of decimal places to display
 */
const Slider = ({
  min = 0,
  max = 100,
  step = 1,
  value,
  onChange,
  label = '',
  showValue = true,
  valuePrefix = '',
  valueSuffix = '',
  className = '',
  decimals = 1,
}) => {
  // Local state for controlled component
  const [localValue, setLocalValue] = useState(value);
  const sliderRef = useRef(null);
  
  // Update local value when prop value changes
  useEffect(() => {
    setLocalValue(value);
  }, [value]);
  
  // Handle slider change
  const handleChange = (e) => {
    const newValue = parseFloat(e.target.value);
    setLocalValue(newValue);
    
    if (onChange) {
      onChange(newValue);
    }
  };
  
  // Format display value
  const formatValue = (val) => {
    if (typeof val !== 'number') return '';
    
    const formattedValue = step < 1 
      ? val.toFixed(decimals) 
      : val.toString();
      
    return `${valuePrefix}${formattedValue}${valueSuffix}`;
  };
  
  // Calculate background gradient for track
  const calculateTrackBackground = () => {
    const percentage = ((localValue - min) / (max - min)) * 100;
    return `linear-gradient(to right, var(--primary-color) 0%, var(--primary-color) ${percentage}%, var(--border-color) ${percentage}%, var(--border-color) 100%)`;
  };
  
  return (
    <div className={`slider-container ${className}`}>
      {label && (
        <div className="slider-header" style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '0.5rem' 
        }}>
          <label className="slider-label" style={{ 
            fontSize: '0.875rem',
            color: 'var(--text-secondary)'
          }}>
            {label}
          </label>
          
          {showValue && (
            <span className="slider-value" style={{ 
              fontSize: '0.875rem',
              color: 'var(--text-color)',
              fontWeight: '500'
            }}>
              {formatValue(localValue)}
            </span>
          )}
        </div>
      )}
      
      <div className="slider-track-container" style={{ position: 'relative' }}>
        <input
          ref={sliderRef}
          type="range"
          min={min}
          max={max}
          step={step}
          value={localValue}
          onChange={handleChange}
          className="slider-input"
          style={{
            width: '100%',
            height: '6px',
            appearance: 'none',
            background: calculateTrackBackground(),
            borderRadius: '9999px',
            outline: 'none',
            marginTop: '0.75rem',
            marginBottom: '0.75rem',
            cursor: 'pointer',
          }}
        />
        
        {/* Tick marks for significant values */}
        <div className="slider-ticks" style={{
          display: 'flex',
          justifyContent: 'space-between',
          position: 'absolute',
          left: '0',
          right: '0',
          bottom: '-12px',
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{min}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{max}</span>
        </div>
      </div>
      
      {/* Custom styles for cross-browser compatibility */}
      <style jsx>{`
        .slider-input::-webkit-slider-thumb {
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background-color: var(--primary-color);
          border: 2px solid var(--text-color);
          cursor: pointer;
          transition: transform 0.1s ease;
        }
        
        .slider-input::-moz-range-thumb {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background-color: var(--primary-color);
          border: 2px solid var(--text-color);
          cursor: pointer;
          transition: transform 0.1s ease;
        }
        
        .slider-input::-webkit-slider-thumb:hover,
        .slider-input::-webkit-slider-thumb:active {
          transform: scale(1.1);
        }
        
        .slider-input::-moz-range-thumb:hover,
        .slider-input::-moz-range-thumb:active {
          transform: scale(1.1);
        }
      `}</style>
    </div>
  );
};

export default Slider;