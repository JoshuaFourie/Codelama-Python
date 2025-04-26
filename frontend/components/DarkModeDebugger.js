import { useEffect } from 'react';

const DarkModeDebugger = () => {
  useEffect(() => {
    // Verbose logging and forcing of dark mode
    console.group('Dark Mode Debugger');
    
    // Force inline styles
    console.log('Applying force dark mode styles');
    
    // Apply styles to critical elements
    const elementsToStyle = [
      document.documentElement, 
      document.body, 
      document.querySelector('#__next')
    ];

    elementsToStyle.forEach(el => {
      if (el) {
        el.style.backgroundColor = '#111827';
        el.style.color = '#F9FAFB';
      }
    });

    // Log system color scheme
    console.log('System Color Scheme:', window.matchMedia('(prefers-color-scheme: dark)').matches ? 'Dark' : 'Light');

    // Inspect current styles
    const bodyStyles = window.getComputedStyle(document.body);
    console.log('Computed Body Background:', bodyStyles.backgroundColor);
    console.log('Computed Body Color:', bodyStyles.color);

    // Add diagnostic overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background-color: #111827;
      color: #F9FAFB;
      padding: 10px;
      z-index: 10000;
      text-align: center;
      font-family: monospace;
    `;
    overlay.textContent = 'Dark Mode Debugger Active';
    document.body.appendChild(overlay);

    console.groupEnd();

    return () => {
      // Cleanup
      if (overlay.parentElement) {
        overlay.parentElement.removeChild(overlay);
      }
    };
  }, []);

  return null; // Render nothing, this is a side-effect component
};

export default DarkModeDebugger;