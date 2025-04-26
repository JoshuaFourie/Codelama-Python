import React, { useState, useEffect } from 'react';
import Button from '../ui/Button';

const TrainingDataManager = () => {
  const [examples, setExamples] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [languageFilter, setLanguageFilter] = useState('All');
  
  // Fetch training examples on mount and when filter changes
  useEffect(() => {
    fetchTrainingExamples();
  }, [languageFilter]);
  
  const fetchTrainingExamples = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/training?language=${languageFilter}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch training examples');
      }
      
      const data = await response.json();
      setExamples(data.examples || []);
    } catch (err) {
      console.error('Error fetching training examples:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleLanguageFilterChange = (e) => {
    setLanguageFilter(e.target.value);
  };
  
  const handleRefresh = () => {
    fetchTrainingExamples();
  };

  return (
    <div className="training-manager">
      <h2>Training Data Management</h2>
      <p className="description">
        Organize and export your training examples for both Python and PowerShell.
      </p>
      
      <div className="filter-container" style={{ marginTop: '1rem', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div>
            <label htmlFor="language-filter" className="filter-label">Language Filter:</label>
            <select
              id="language-filter"
              value={languageFilter}
              onChange={handleLanguageFilterChange}
              className="filter-select"
              style={{
                backgroundColor: 'var(--bg-secondary)',
                color: 'var(--text-color)',
                border: '1px solid var(--border-color)',
                padding: '0.5rem',
                borderRadius: '0.25rem'
              }}
            >
              <option value="All">All</option>
              <option value="Python">Python</option>
              <option value="PowerShell">PowerShell</option>
            </select>
          </div>
          
          <Button onClick={handleRefresh} disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Refresh List'}
          </Button>
        </div>
      </div>
      
      {error && (
        <div className="error-message" style={{ color: 'var(--error-color)', marginBottom: '1rem' }}>
          Error: {error}
        </div>
      )}
      
      <div className="examples-table-container">
        <table className="examples-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Source</th>
              <th>Language</th>
              <th>Timestamp</th>
              <th>Task Preview</th>
            </tr>
          </thead>
          <tbody>
            {examples.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '1rem' }}>
                  {isLoading ? 'Loading examples...' : 'No training examples found.'}
                </td>
              </tr>
            ) : (
              examples.map((example, index) => (
                <tr key={index}>
                  <td>{example.filename}</td>
                  <td>{example.source}</td>
                  <td>{example.language}</td>
                  <td>{example.timestamp}</td>
                  <td>{example.taskPreview}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TrainingDataManager;