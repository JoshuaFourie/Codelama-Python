// pages/api/generate.js
// API endpoint for code generation

import axios from 'axios';

// Configuration for the backend API
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000';

export default async function handler(req, res) {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Get parameters from request body
  const { prompt, language, temperature, max_tokens } = req.body;

  // Validate required fields
  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required' });
  }

  try {
    // Forward request to Python backend
    const response = await axios.post(`${BACKEND_URL}/generate`, {
      prompt,
      language: language || 'auto',
      temperature: temperature || 0.2,
      max_tokens: max_tokens || 1024,
    });

    // Return the generated code
    return res.status(200).json({
      success: true,
      response: response.data.code,
      language: response.data.language,
    });
  } catch (error) {
    console.error('Error generating code:', error);
    
    // Return error message
    return res.status(500).json({
      success: false,
      error: error.response?.data?.error || 'Failed to generate code',
    });
  }
}