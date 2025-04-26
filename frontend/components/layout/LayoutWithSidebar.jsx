import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import { useAppContext } from '../../context/AppContext';

/**
 * Layout component with sidebar navigation
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Main content
 */
const LayoutWithSidebar = ({ children }) => {
  const { sidebarOpen } = useAppContext();

  return (
    <div className={`app-container ${sidebarOpen ? 'sidebar-layout' : ''}`}>
      <Header />
      <Sidebar />
      
      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
      
      {/* Add responsive styles */}
      <style jsx>{`
        .main-content {
          transition: margin-left 0.3s ease-in-out;
          min-height: calc(100vh - 60px); /* Adjust based on header height */
        }
        
        @media (min-width: 768px) {
          .sidebar-layout .main-content {
            margin-left: 260px;
          }
        }
      `}</style>
    </div>
  );
};

export default LayoutWithSidebar;