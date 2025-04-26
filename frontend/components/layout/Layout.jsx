import React from 'react';
import Header from './Header';
import Tabs from '../ui/Tabs';
import { useRouter } from 'next/router';

const Layout = ({ children }) => {
  const router = useRouter();
  
  const tabs = [
    { id: 'chat', label: 'Chat', path: '/' },
    { id: 'training', label: 'Training Data', path: '/training' },
    { id: 'about', label: 'About', path: '/about' },
  ];

  // Find active tab based on current path
  const activeTab = tabs.find(tab => tab.path === router.pathname)?.id || 'chat';

  const handleTabChange = (tabId) => {
    const tab = tabs.find(tab => tab.id === tabId);
    if (tab) {
      router.push(tab.path);
    }
  };

  return (
    <div className="app-container">
      <Header />
      <Tabs tabs={tabs} activeTab={activeTab} onChange={handleTabChange} />
      <main>
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;