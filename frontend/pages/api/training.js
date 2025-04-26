// pages/api/training.js
// API endpoint for managing training examples

import axios from 'axios';

// Configuration for the backend API
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export default async function handler(req, res) {
  // Handle different HTTP methods
  if (req.method === 'GET') {
    return getTrainingExamples(req, res);
  } else if (req.method === 'POST') {
    return saveTrainingExample(req, res);
  } else {
    return res.status(405).json({ error: 'Method not allowed' });
  }
}

// GET - Retrieve training examples
async function getTrainingExamples(req, res) {
  try {
    // Get language filter from query params
    const { language } = req.query;
    
    // Fetch examples from Python backend
    const response = await axios.get(`${BACKEND_URL}/training`, {
      params: { language: language || 'All' }
    });
    
    // Return examples
    return res.status(200).json({
      success: true,
      examples: response.data.examples,
    });
  } catch (error) {
    console.error('Error fetching training examples:', error);
    
    // Return error message
    return res.status(500).json({
      success: false,
      error: error.response?.data?.error || 'Failed to fetch training examples',
    });
  }
}

// POST - Save a new training example
async function saveTrainingExample(req, res) {
  // Get parameters from request body
  const { task, solution } = req.body;
  
  // Validate required fields
  if (!task || !solution) {
    return res.status(400).json({ error: 'Task and solution are required' });
  }
  
  try {
    // Forward to Python backend
    const response = await axios.post(`${BACKEND_URL}/training`, {
      task,
      solution,
    });
    
    // Return success response
    return res.status(200).json({
      success: true,
      message: 'Training example saved successfully',
      id: response.data.id,
    });
  } catch (error) {
    console.error('Error saving training example:', error);
    
    // Return error message
    return res.status(500).json({
      success: false,
      error: error.response?.data?.error || 'Failed to save training example',
    });
  }
}