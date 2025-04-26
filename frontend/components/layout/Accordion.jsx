import React, { useState } from 'react';

/**
 * Accordion component for collapsible content sections
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Title of the accordion
 * @param {React.ReactNode} props.children - Content to be shown/hidden
 * @param {boolean} props.defaultOpen - Whether accordion is open by default
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.titleClassName - CSS classes for title
 * @param {string} props.contentClassName - CSS classes for content
 * @param {string} props.iconClassName - CSS classes for expand/collapse icon
 */
const Accordion = ({
  title,
  children,
  defaultOpen = false,
  className = '',
  titleClassName = '',
  contentClassName = '',
  iconClassName = '',
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  const toggleAccordion = () => {
    setIsOpen(!isOpen);
  };
  
  return (
    <div className={`accordion ${className}`}>
      <div 
        className={`accordion-header ${titleClassName}`}
        onClick={toggleAccordion}
        style={{
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0.75rem 1rem',
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: isOpen ? '0.5rem 0.5rem 0 0' : '0.5rem',
          border: '1px solid var(--border-color)',
          transition: 'border-radius 0.2s ease',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 500 }}>
          {title}
        </h3>
        <span 
          className={`accordion-icon ${iconClassName}`}
          style={{
            transition: 'transform 0.2s ease',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          ▼
        </span>
      </div>
      
      {isOpen && (
        <div 
          className={`accordion-content ${contentClassName}`}
          style={{
            padding: '1rem',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: '0 0 0.5rem 0.5rem',
            borderLeft: '1px solid var(--border-color)',
            borderRight: '1px solid var(--border-color)',
            borderBottom: '1px solid var(--border-color)',
            animation: 'accordionFadeIn 0.3s ease',
          }}
        >
          {children}
        </div>
      )}
      
      {/* Inline styles for animations */}
      <style jsx>{`
        @keyframes accordionFadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

/**
 * AccordionGroup component for grouping multiple accordions
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Accordion components
 * @param {string} props.className - Additional CSS classes
 */
export const AccordionGroup = ({ 
  children,
  className = '',
}) => {
  return (
    <div 
      className={`accordion-group ${className}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
      }}
    >
      {children}
    </div>
  );
};

export default Accordion;