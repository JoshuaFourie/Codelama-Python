import os
from gradio.themes import Base, Size, Color

# ===== CUSTOM BRANDING SETTINGS =====
APP_NAME = "J's CodeBuddy AI"
APP_TAGLINE = "Your Python & PowerShell Coding Assistant"
APP_LOGO = "logo.png"
PRIMARY_COLOR = "#3B82F6"  # Blue-600
SECONDARY_COLOR = "#93C5FD"  # Blue-300  
BACKGROUND_COLOR = "#111827"  # Gray-900
TEXT_COLOR = "#F9FAFB"  # Gray-50
AVATAR_EMOJI = "🤖"
# ===================================

# Define a modern dark theme inspired by the design
def create_theme():
    """Create and return a custom Gradio theme"""
    try:
        # For newest Gradio versions
        theme = Base(
            primary_hue=Color(
                c50="#DBEAFE",   # Very light blue
                c100="#BFDBFE", 
                c200="#93C5FD",
                c300="#60A5FA",
                c400="#3B82F6",  # Primary blue
                c500="#2563EB",
                c600="#1D4ED8",
                c700="#1E40AF",
                c800="#1E3A8A",
                c900="#172554",
                c950="#0F172A",  # Very dark blue
            ),
            neutral_hue=Color(
                c50="#F9FAFB",
                c100="#F3F4F6",
                c200="#E5E7EB",
                c300="#D1D5DB",
                c400="#9CA3AF",
                c500="#6B7280",
                c600="#4B5563",
                c700="#374151",
                c800="#1F2937",
                c900="#111827",  # Main background
                c950="#030712",  # Darker background
            )
        )
        return theme
    except Exception as e:
        print(f"Could not create custom theme. Error: {e}")
        print("Falling back to default Gradio theme.")
        return None
# Custom CSS for the theme
custom_css = """
/* Modern Dark Theme Styling */
:root {
    --primary-color: #3B82F6;
    --primary-light: #93C5FD;
    --primary-dark: #1D4ED8;
    --bg-color: #111827;
    --bg-secondary: #1F2937;
    --text-color: #F9FAFB;
    --text-secondary: #9CA3AF;
    --border-color: #374151;
}

/* Base styles */
body {
    font-family: 'Inter', system-ui, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
}

/* Header styling */
.header-container {
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 1rem;
    margin-bottom: 0;
}

.app-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    color: var(--text-color);
}

.app-tagline {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin: 0;
}

.logo-image {
    max-width: 100%;
    height: auto;
}

/* Tab styling */
.modern-tabs .tabs {
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
}

.modern-tabs .tab-nav {
    gap: 0.5rem;
    padding: 0 1rem;
}

.modern-tabs .tab-nav button {
    padding: 0.75rem 1.25rem;
    color: var(--text-secondary);
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}

.modern-tabs .tab-nav button[data-selected="true"] {
    color: var(--primary-color);
    border-bottom: 2px solid var(--primary-color);
    background-color: transparent;
}

.modern-tabs .tab-nav button:hover:not([data-selected="true"]) {
    background-color: rgba(255, 255, 255, 0.05);
}

.tab-content {
    padding: 1.5rem;
}

/* Language selector styling */
.language-selector-row {
    background-color: var(--bg-secondary);
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    align-items: center;
}

.section-label {
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
}

.language-options .wrap {
    display: flex;
    gap: 0.5rem;
}

.language-options label {
    background-color: var(--bg-color);
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    transition: all 0.2s ease;
}

.language-options label[data-checked="true"] {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.language-indicator {
    text-align: right;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

/* Chat styling */
.modern-chatbot {
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    background-color: var(--bg-secondary);
}

.modern-chatbot .bubble-bot {
    background-color: var(--bg-color);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1rem;
}

.modern-chatbot .bubble-user {
    background-color: var(--primary-dark);
    border-radius: 0.5rem;
    padding: 1rem;
}

.modern-chatbot pre {
    background-color: #0F172A;
    border-radius: 0.375rem;
    padding: 0.75rem;
    overflow-x: auto;
    border: 1px solid var(--border-color);
}

.modern-chatbot code {
    font-family: 'JetBrains Mono', monospace;
}

/* Input styling */
.input-container {
    margin-top: 1rem;
}

.modern-input textarea {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    color: var(--text-color);
    padding: 0.75rem;
    resize: none;
    transition: border-color 0.2s ease;
}

.modern-input textarea:focus {
    border-color: var(--primary-color);
    outline: none;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.send-button {
    background-color: var(--primary-color);
    color: white;
    border-radius: 0.5rem;
    font-weight: 500;
    transition: background-color 0.2s ease;
}

.send-button:hover {
    background-color: var(--primary-dark);
}

/* Accordion styling */
.settings-accordion {
    margin: 1rem 0;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    overflow: hidden;
}

.settings-accordion > .label-wrap {
    background-color: var(--bg-secondary);
    padding: 0.75rem 1rem;
}

.settings-accordion > .wrap > .content {
    background-color: var(--bg-secondary);
    padding: 1rem;
}

/* Slider styling */
.modern-slider input[type="range"] {
    height: 6px;
    background-color: var(--border-color);
    border-radius: 9999px;
}

.modern-slider input[type="range"]::-webkit-slider-thumb {
    background-color: var(--primary-color);
    border: 2px solid var(--text-color);
    height: 18px;
    width: 18px;
    border-radius: 50%;
}

/* Button styling */
.action-buttons, .feedback-buttons {
    margin-top: 1rem;
    gap: 0.5rem;
}

.action-button, .feedback-button {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-color);
    border-radius: 0.375rem;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    transition: background-color 0.2s ease;
}

.action-button:hover, .feedback-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

.feedback-button {
    padding: 0.5rem 1rem;
}

/* Table styling */
.examples-table {
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    overflow: hidden;
}

.examples-table thead tr {
    background-color: var(--bg-secondary);
}

.examples-table th, .examples-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
}

/* About page styling */
.about-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.about-tagline {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
}

.about-content h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-light);
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
}

.about-content h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}

.about-content p {
    margin-bottom: 1rem;
    line-height: 1.6;
}

.about-content ul, .about-content ol {
    margin-bottom: 1.5rem;
    margin-left: 1.5rem;
}

.about-content li {
    margin-bottom: 0.5rem;
    line-height: 1.6;
}

.feature-list li, .usage-steps li {
    padding-left: 0.5rem;
}
"""