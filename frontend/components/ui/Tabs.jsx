import React from 'react';

const Tabs = ({ tabs, activeTab, onChange }) => {
  return (
    <div className="tabs">
      <div className="container">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Tabs;