// pages/api/feedback.js
// API endpoint for handling user feedback

import axios from 'axios';

// Configuration for the backend API
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export default async function handler(req, res) {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Get parameters from request body
  const { task, solution, type } = req.body;

  // Validate required fields
  if (!task || !solution || !type) {
    return res.status(400).json({ error: 'Task, solution, and feedback type are required' });
  }

  try {
    // Forward feedback to Python backend
    const response = await axios.post(`${BACKEND_URL}/feedback`, {
      task,
      solution,
      type, // 'positive' or 'negative'
    });

    // Return success response
    return res.status(200).json({
      success: true,
      message: `${type.charAt(0).toUpperCase() + type.slice(1)} feedback saved successfully`,
    });
  } catch (error) {
    console.error('Error saving feedback:', error);
    
    // Return error message
    return res.status(500).json({
      success: false,
      error: error.response?.data?.error || 'Failed to save feedback',
    });
  }
}