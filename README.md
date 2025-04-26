# CodeBuddy AI - Next.js Implementation

A modern, responsive code generation assistant for Python and PowerShell, built with Next.js and FastAPI.

## Project Overview

CodeBuddy AI is a multi-language code generation assistant that supports both Python and PowerShell. The application uses a modern, clean interface with a dark theme for a professional appearance.

## Features

- **Modern UI**: Clean, dark-themed interface with responsive design
- **Multi-language support**: Automatic detection between Python and PowerShell
- **Customizable generation**: Adjust temperature and token length for different results
- **Syntax highlighting**: Beautiful code display with proper formatting
- **Training data management**: Save examples for continuous improvement
- **Feedback system**: Provide positive/negative feedback on responses

## Project Structure

```
codebuddy-ai/
├── frontend/                  # Next.js frontend application
│   ├── components/            # React components
│   ├── pages/                 # Next.js pages and API routes
│   ├── styles/                # CSS styles
│   ├── public/                # Static assets
│   └── package.json           # Frontend dependencies
│
├── backend/                   # Python backend
│   ├── app.py                 # FastAPI application
│   ├── model_manager.py       # Model management
│   └── requirements.txt       # Python dependencies
```

## Setup Instructions

### Prerequisites

- Node.js 16+ and npm/yarn
- Python 3.8+
- A Hugging Face account and API token

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set your Hugging Face token:
   ```
   export HUGGING_FACE_HUB_TOKEN=your_token_here
   ```
   On Windows: `set HUGGING_FACE_HUB_TOKEN=your_token_here`

5. Start the backend server:
   ```
   python app.py
   ```
   The API will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```
   or `yarn install`

3. Start the development server:
   ```
   npm run dev
   ```
   or `yarn dev`

4. Access the application at http://localhost:3000

## Environment Variables

### Backend
- `HUGGING_FACE_HUB_TOKEN` - Your Hugging Face API token
- `PORT` - Port for the backend server (default: 5000)

### Frontend
- `BACKEND_URL` - URL for the backend API (default: http://localhost:5000)

## Usage Guide

1. **Starting a conversation**: Enter your code request in the input field
2. **Language selection**: Choose Python, PowerShell, or Auto Detect
3. **Adjusting settings**: Open the Settings accordion to modify temperature and max tokens
4. **Managing training data**: Use the Training Data tab to view and filter saved examples
5. **Providing feedback**: Use the 👍 and 👎 buttons to rate responses

## Model Information

- **Python code**: Generated using CodeLlama-13b-Python
- **PowerShell code**: Generated using Microsoft's Phi-2 model

## Credits

Built with:
- Next.js - React framework
- FastAPI - Python API framework
- Transformers - Hugging Face's NLP library
- PrismJS - Syntax highlighting
