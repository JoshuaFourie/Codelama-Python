import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAppContext } from '../../context/AppContext';

const Sidebar = () => {
  const router = useRouter();
  const { sidebarOpen, toggleSidebar } = useAppContext();
  
  // Navigation items
  const navItems = [
    { path: '/', label: 'Chat', icon: '💬' },
    { path: '/training', label: 'Training Data', icon: '📚' },
    { path: '/about', label: 'About', icon: 'ℹ️' },
  ];
  
  // Additional links section
  const helpLinks = [
    { path: 'https://github.com/your-username/codebuddy-ai', label: 'GitHub Repository', external: true },
    { path: 'https://huggingface.co/models', label: 'Hugging Face Models', external: true },
  ];
  
  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="sidebar-overlay"
          onClick={toggleSidebar}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 40,
          }}
        />
      )}
      
      {/* Sidebar */}
      <div 
        className={`sidebar ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          bottom: 0,
          width: '260px',
          backgroundColor: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border-color)',
          zIndex: 50,
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform 0.3s ease-in-out',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Sidebar header */}
        <div 
          className="sidebar-header"
          style={{
            padding: '1rem',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2 style={{ margin: 0, fontSize: '1.25rem' }}>CodeBuddy AI</h2>
          <button
            onClick={toggleSidebar}
            className="close-button"
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-color)',
              cursor: 'pointer',
              fontSize: '1.5rem',
              padding: '0.25rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            ×
          </button>
        </div>
        
        {/* Navigation section */}
        <nav 
          className="sidebar-nav"
          style={{
            padding: '1rem 0',
            flexGrow: 1,
          }}
        >
          <ul
            style={{
              listStyle: 'none',
              margin: 0,
              padding: 0,
            }}
          >
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  href={item.path}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.75rem 1rem',
                    color: router.pathname === item.path ? 'var(--primary-color)' : 'var(--text-color)',
                    backgroundColor: router.pathname === item.path ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    borderLeft: router.pathname === item.path ? '3px solid var(--primary-color)' : '3px solid transparent',
                    textDecoration: 'none',
                  }}
                  onClick={() => {
                    if (window.innerWidth < 768) {
                      toggleSidebar();
                    }
                  }}
                >
                  <span style={{ marginRight: '0.75rem', fontSize: '1.25rem' }}>
                    {item.icon}
                  </span>
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        
        {/* Help & Resources section */}
        <div
          className="sidebar-help"
          style={{
            padding: '1rem',
            borderTop: '1px solid var(--border-color)',
          }}
        >
          <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginTop: 0 }}>
            Resources
          </h3>
          <ul
            style={{
              listStyle: 'none',
              margin: 0,
              padding: 0,
            }}
          >
            {helpLinks.map((link) => (
              <li key={link.path} style={{ marginBottom: '0.5rem' }}>
                {link.external ? (
                  <a
                    href={link.path}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      color: 'var(--text-secondary)',
                      textDecoration: 'none',
                      fontSize: '0.875rem',
                    }}
                  >
                    {link.label}
                    <span style={{ marginLeft: '0.25rem', fontSize: '0.75rem' }}>↗</span>
                  </a>
                ) : (
                  <Link
                    href={link.path}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      color: 'var(--text-secondary)',
                      textDecoration: 'none',
                      fontSize: '0.875rem',
                    }}
                  >
                    {link.label}
                  </Link>
                )}
              </li>
            ))}
          </ul>
        </div>
        
        {/* Sidebar footer */}
        <div
          className="sidebar-footer"
          style={{
            padding: '1rem',
            borderTop: '1px solid var(--border-color)',
            fontSize: '0.75rem',
            color: 'var(--text-secondary)',
            textAlign: 'center',
          }}
        >
          <p style={{ margin: 0 }}>
            CodeBuddy AI © {new Date().getFullYear()}
          </p>
        </div>
      </div>
      
      {/* Sidebar toggle button (for mobile) */}
      <button
        className="sidebar-toggle"
        onClick={toggleSidebar}
        style={{
          position: 'fixed',
          bottom: '1.5rem',
          left: '1.5rem',
          width: '3rem',
          height: '3rem',
          borderRadius: '50%',
          backgroundColor: 'var(--primary-color)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          border: 'none',
          cursor: 'pointer',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          zIndex: 30,
          fontSize: '1.5rem',
          // Only show on mobile
          '@media (min-width: 768px)': {
            display: 'none',
          },
        }}
      >
        ≡
      </button>
    </>
  );
};

export default Sidebar;