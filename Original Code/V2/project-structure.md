# CodeBuddy AI Project Structure

## Overview

CodeBuddy AI is a multi-language code generation assistant that supports both Python and PowerShell. The application uses a modern, clean interface with a dark theme for a professional appearance.

## File Organization

```
codebuddy-ai/
├── app.py                  # Main application entry point
├── model_manager.py        # Multi-model handling for different languages
├── theme.py                # Theme configuration and styling settings
├── styles.css              # Custom CSS styles for the application
├── logo.png                # Application logo image
├── models/                 # Directory for cached model files
├── training_data/          # Storage for training examples
└── chat_history/           # User feedback and conversation logs
    ├── positive_feedback/  # Positive feedback examples
    └── negative_feedback/  # Negative feedback examples
```

## Key Components

### Main Application (app.py)

The core application file that initializes the UI and connects all components. It handles user interactions, code generation requests, and manages the application state.

### Model Manager (model_manager.py)

Handles loading and switching between language models:
- Loads appropriate models based on detected language
- Implements efficient model switching to save memory
- Provides language detection capabilities
- Formats code responses for display

### Theme Configuration (theme.py)

Contains all theming and styling definitions:
- Color palette variables
- Application branding settings
- Gradio theme configuration
- Custom CSS for UI components

### Styles (styles.css)

External CSS file with detailed styling:
- Component-specific styling rules
- Responsive design adjustments
- Code syntax highlighting
- UI element customization

## Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Enter your Hugging Face token when prompted
4. Access the web interface at http://127.0.0.1:7860

## Customization

You can customize the application by modifying:
- Color scheme: Edit variables in `theme.py`
- Branding: Update app name, tagline, and logo in `theme.py`
- UI elements: Modify component styling in `styles.css`
- Models: Change or add models in the `models_config` dictionary in `app.py`