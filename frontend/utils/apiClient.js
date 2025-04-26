/**
 * API Client for CodeBuddy AI
 * Centralizes all API calls to backend services
 */

import axios from 'axios';

// Get backend URL from environment variable or use default
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

// Create axios instance with common configuration
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout for code generation
});

/**
 * Generate code based on prompt
 * @param {Object} params - Generation parameters
 * @param {string} params.prompt - User's prompt
 * @param {string} params.language - Language for generation ('python', 'powershell', 'auto')
 * @param {number} params.temperature - Temperature for generation (0-1)
 * @param {number} params.max_tokens - Maximum tokens to generate
 * @returns {Promise<Object>} - Generation response
 */
export const generateCode = async ({ prompt, language = 'auto', temperature = 0.2, max_tokens = 1024 }) => {
  try {
    const response = await apiClient.post('/generate', {
      prompt,
      language,
      temperature,
      max_tokens,
    });
    
    return response.data;
  } catch (error) {
    console.error('Error generating code:', error);
    throw error;
  }
};

/**
 * Save user feedback on a code generation
 * @param {Object} params - Feedback parameters
 * @param {string} params.task - Original user prompt
 * @param {string} params.solution - Generated code
 * @param {string} params.type - Feedback type ('positive' or 'negative')
 * @returns {Promise<Object>} - Feedback response
 */
export const saveFeedback = async ({ task, solution, type }) => {
  try {
    const response = await apiClient.post('/feedback', {
      task,
      solution,
      type,
    });
    
    return response.data;
  } catch (error) {
    console.error('Error saving feedback:', error);
    throw error;
  }
};

/**
 * Save training example
 * @param {Object} params - Training example parameters
 * @param {string} params.task - Original user prompt
 * @param {string} params.solution - Generated code
 * @returns {Promise<Object>} - Training response
 */
export const saveTrainingExample = async ({ task, solution }) => {
  try {
    const response = await apiClient.post('/training', {
      task,
      solution,
    });
    
    return response.data;
  } catch (error) {
    console.error('Error saving training example:', error);
    throw error;
  }
};

/**
 * Get training examples list
 * @param {string} language - Optional language filter
 * @returns {Promise<Object>} - List of training examples
 */
export const getTrainingExamples = async (language = 'All') => {
  try {
    const response = await apiClient.get('/training', {
      params: { language },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching training examples:', error);
    throw error;
  }
};

/**
 * Check API health/status
 * @returns {Promise<Object>} - API status
 */
export const checkApiStatus = async () => {
  try {
    // This would call a health endpoint on your backend
    // Using a direct call to the backend for this
    const response = await axios.get(`${BACKEND_URL}/`);
    return response.data;
  } catch (error) {
    console.error('API health check failed:', error);
    throw error;
  }
};

export default {
  generateCode,
  saveFeedback,
  saveTrainingExample,
  getTrainingExamples,
  checkApiStatus,
};