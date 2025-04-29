# app.py - Main CodeBuddy AI Application with lazy model loading

import os
import torch
import re
import gradio as gr
import json
from datetime import datetime
from threading import Thread

# Import custom modules
from model_manager import MultiModelManager
from theme import create_theme  # Import theme configuration
from theme import get_logo_with_dimensions

# Define directories
CACHE_DIR = "models"
TRAINING_DIR = "training_data"
CHAT_HISTORY_DIR = "chat_history"

# Import application settings from theme
from theme import APP_NAME, APP_TAGLINE, APP_LOGO, PRIMARY_COLOR, SECONDARY_COLOR, AVATAR_EMOJI

# Custom CSS for styling
custom_css = """
/* Modern dark theme */
body, .gradio-container {
    background-color: #111827 !important;
    color: #F9FAFB !important;
}

.bot-avatar img {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: contain;
    background-color: #3B82F6;
}

/* Side-by-side layout for chat and code */
.chat-code-container {
    display: flex;
    flex-direction: row;
    gap: 20px;
    margin-bottom: 20px;
}

.chat-column {
    flex: 1;
    min-width: 300px;
    display: flex;
    flex-direction: column;
}

.code-column {
    flex: 1;
    min-width: 300px;
    display: flex;
    flex-direction: column;
}

/* Make sure chatbot stays in its column */
.modern-chatbot {
    height: 400px;
    overflow-y: auto;
    border-radius: 8px;
    border: 1px solid #334155;
}

/* Code display styling */
.code-display-container {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.code-display {
    flex-grow: 1;
    border-radius: 8px;
    border: 1px solid #334155;
    background-color: #1e1e1e;
    font-family: 'Fira Code', 'Cascadia Code', 'Courier New', monospace;
    height: 400px;
}

/* Button layout improvements */
.action-buttons-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 15px;
    justify-content: space-between;
}

.action-button-group {
    display: flex;
    gap: 10px;
}

.action-button {
    min-width: 100px;
}

.feedback-buttons {
    display: flex;
    gap: 10px;
    margin-top: 10px;
}

/* Enhanced language selector */
.language-selector-container {
    background-color: #1e293b;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 15px;
}

.language-options {
    display: flex;
    gap: 10px;
}

/* Responsive adjustments */
@media (max-width: 992px) {
    .chat-code-container {
        flex-direction: column;
    }
    
    .chat-column, .code-column {
        width: 100%;
    }
    
    .modern-chatbot, .code-display {
        height: 300px;
    }
}

/* AI Comparison Tab Styling and other styles remain the same */
.ai-comparison-container {
    border-radius: 8px;
    margin-bottom: 16px;
}

.comparison-column {
    padding: 10px;
    border-radius: 8px;
    background-color: #1e293b;
    transition: all 0.3s ease;
}

.comparison-column:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.response-field {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    font-family: monospace;
}

.response-field textarea {
    font-family: 'Courier New', monospace;
}

/* Enhanced Training Data Tab */
.example-details-accordion {
    margin-top: 16px;
    border: 1px solid #334155;
    border-radius: 8px;
    overflow: hidden;
}

.source-filter, .language-filter {
    padding: 10px;
    margin-bottom: 10px;
    background-color: #1e293b;
    border-radius: 8px;
}

.examples-table {
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 16px;
}

.examples-table table {
    border-collapse: separate;
    border-spacing: 0;
}

.examples-table tr {
    cursor: pointer;
    transition: background-color 0.2s;
}

.examples-table tr:hover {
    background-color: #334155;
}

.examples-table tr.selected {
    background-color: #3b82f6;
    color: white;
}

/* Button styles for the new sections */
.comparison-actions {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.note-field {
    background-color: #1e293b;
    border: 1px solid #475569;
    padding: 10px;
    border-radius: 8px;
    margin-top: 10px;
}

.section-label {
    font-weight: 600;
    margin-bottom: 8px;
    color: #94a3b8;
}

/* Status display enhancement */
.status-container {
    background-color: #1e293b;
    border-radius: 8px;
    padding: 10px;
    margin-top: 10px;
}

.status-text {
    font-family: monospace;
    color: #94a3b8;
}

/* Base styles for all messages - minimal styling */
.message {
    margin: 8px 0 !important;
}

/* Remove bubble styling ONLY for assistant messages */
.bot-message, .bot-bubble, .message.svelte-1gfkn6j:nth-child(even) {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 5px 10px !important;
}

/* Keep bubble styling for user messages */
.user-message, .user-bubble, .message.svelte-1gfkn6j:nth-child(odd) {
    background: #2d3748 !important; /* Dark blue background */
    border-radius: 12px !important;
    padding: 10px 14px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid #4a5568 !important;
}

/* Style the message container */
.messages-container {
    background: #111827 !important;
    border-radius: 8px !important;
    padding: 16px !important;
    border: 1px solid #1f2937 !important;
}

/* Make user messages visually distinct */
.user-message, .user-bubble {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

.bot-message, .bot-bubble {
    color: #a0d2eb !important;
}

/* Remove borders from chatbot component */
.modern-chatbot > div {
    border: 1px solid #1f2937 !important;
    background: #111827 !important;
    border-radius: 8px;
}

/* Enhanced styling for the code display area */
.code-display {
    border: 1px solid #27272a !important;
    border-radius: 8px !important;
    background-color: #1e1e2e !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
}

.code-display pre {
    padding: 16px !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}

"""

# Create necessary directories
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(TRAINING_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

### Application Initialization

class MultiLanguageCodeBuddy:
    def __init__(self, hf_token=None):
        # Define model configurations
        self.models_config = {
            'python': {
                'model_name': 'meta-llama/CodeLlama-13b-Instruct-hf',
                'prompt_template': "Write Python code for the following request:\n\n{prompt}\n\nCode:"
            },
            'powershell': {
                'model_name': 'meta-llama/CodeLlama-13b-Instruct-hf',
                'prompt_template': "You are an expert PowerShell programmer. Write PowerShell code for the following request:\n\n{prompt}\n\nEnsure the code follows PowerShell best practices and includes comments. Provide only the code.\n\n```powershell"
            }
        }
        
        # Initialize model manager
        self.model_manager = MultiModelManager(self.models_config, cache_dir=CACHE_DIR)
        
        # Store the auth token for later use
        self.model_manager.set_auth_token(hf_token)
        
        # Status message for model loading state
        self.status_message = ""

    ### Core Functions

    def generate_code(self, prompt, chat_history=None, language=None, temperature=0.2, max_new_tokens=1024, repetition_penalty=1.1):
        """Generate code based on prompt and chat history, lazily loading models as needed"""
        self.status_message = "Detecting language..."
        yield self.status_message
        
        # Detect language if not specified
        if language is None or language == "Auto Detect":
            language = self.model_manager.detect_language(prompt)
        else:
            language = language.lower()
            
        # Update status to indicate model loading if needed
        if not self.model_manager.is_model_loaded(language):
            self.status_message = f"Loading {language.capitalize()} model. This may take a moment..."
            yield self.status_message
        
        # Generate code using the appropriate model
        self.status_message = f"Generating {language.capitalize()} code..."
        yield self.status_message
        
        # Process the response
        for response in self.model_manager.generate_code(
            prompt,
            chat_history=chat_history, 
            language=language,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            repetition_penalty=repetition_penalty
        ):
            # Format the code with appropriate syntax highlighting
            formatted_response = self.model_manager.format_code(response, language)
            yield formatted_response

    ### Training Data Management

    def save_training_example(self, task, solution, source_name=None):
        """Save a training example to the training data directory"""
        if not task or not solution:
            return "Missing task or solution"
        
        # Detect language
        language = self.model_manager.detect_language(task)
        language_name = language.capitalize()
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source = source_name if source_name else "Manual"
        filename = f"{source}_{language_name}_{timestamp}.json"
        filepath = os.path.join(TRAINING_DIR, filename)
        
        data = {
            "instruction": task,
            "response": solution,
            "source": source,
            "language": language_name,
            "timestamp": timestamp
        }
        
        try:
            with open(filepath, 'w', encoding='utf8') as f:
                json.dump(data, f, indent=2)
                
            return f"Saved {language_name} example to {filepath}"
        except Exception as e:
            return f"Error saving example: {str(e)}"

    def save_comparison_example(self, question, codebuddy_response, other_ai_response, other_ai_name, language=None):
        """Save a comparison example between CodeBuddy and another AI system"""
        if not question or not codebuddy_response or not other_ai_response:
            return "Missing question or one of the responses"
        
        # Detect language if not specified
        if not language or language == "Auto Detect":
            language = self.model_manager.detect_language(question)
        
        language_name = language.capitalize()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a more detailed filename
        filename = f"Comparison_{other_ai_name}_{language_name}_{timestamp}.json"
        filepath = os.path.join(TRAINING_DIR, filename)
        
        data = {
            "instruction": question,
            "codebuddy_response": codebuddy_response,
            "other_ai_response": other_ai_response,
            "other_ai_name": other_ai_name,
            "source": "AI_Comparison",
            "language": language_name,
            "timestamp": timestamp,
            "comparison_notes": "",  # Empty field for future annotations
        }
        
        try:
            with open(filepath, 'w', encoding='utf8') as f:
                json.dump(data, f, indent=2)
                
            return f"Saved comparison example to {filepath}"
        except Exception as e:
            return f"Error saving comparison example: {str(e)}"

    def save_positive_feedback(self, chat_history):
        """Save positive feedback for the last response"""
        if not chat_history:
            return "No conversation to provide feedback on."
        
        # Get the last user message and bot response
        last_user_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'user'), None)
        last_bot_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'assistant'), None)
        
        if not last_user_msg or not last_bot_msg:
            return "Incomplete conversation to provide feedback on."
        
        return self.save_training_example(last_user_msg['content'], last_bot_msg['content'], "Positive_Feedback")

    def save_negative_feedback(self, chat_history):
        """Save negative feedback for the last response"""
        if not chat_history:
            return "No conversation to provide feedback on."
        
        # Get the last user message and bot response
        last_user_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'user'), None)
        last_bot_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'assistant'), None)
        
        if not last_user_msg or not last_bot_msg:
            return "Incomplete conversation to provide feedback on."
        
        return self.save_training_example(last_user_msg['content'], last_bot_msg['content'], "Negative_Feedback")

    def unload_current_model(self):
        """Unload currently loaded models to free memory"""
        for language in ['python', 'powershell']:
            if self.model_manager.is_model_loaded(language):
                self.model_manager.unload_model(language)
        return "Models unloaded successfully."

    def refresh_training_examples(self, language_filter="All", source_filter="All Sources"):
        """Refresh the list of training examples with filtering options"""
        examples = []
        for filename in os.listdir(TRAINING_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(TRAINING_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf8') as f:
                        data = json.load(f)
                        
                        # Extract language and source from the data
                        file_language = data.get("language", "Unknown")
                        source_type = data.get("source", "Unknown")
                        
                        # Apply language filter if active
                        if language_filter != "All" and file_language != language_filter:
                            continue
                        
                        # Apply source filter if active
                        if source_filter != "All Sources":
                            if source_filter == "Comparison Only" and source_type != "AI_Comparison":
                                continue
                            elif source_filter == "Feedback Only" and not source_type.startswith(("Positive_Feedback", "Negative_Feedback")):
                                continue
                            elif source_filter == "Manual Only" and source_type not in [APP_NAME, "Manual"]:
                                continue
                        
                        # Format source display name
                        if source_type == "AI_Comparison":
                            display_source = f"Comparison with {data.get('other_ai_name', 'Other AI')}"
                        else:
                            display_source = source_type.replace("_", " ")
                        
                        task_preview = data["instruction"][:50] + "..." if len(data["instruction"]) > 50 else data["instruction"]
                        examples.append([
                            filename, 
                            display_source,
                            file_language,
                            data.get("timestamp", "Unknown"),
                            task_preview
                        ])
                except Exception as e:
                    if language_filter == "All":
                        examples.append([filename, f"Error: {str(e)}", "Unknown", "Error", "Could not load file"])
        
        # Sort by timestamp (newest first)
        examples.sort(key=lambda x: x[3], reverse=True)
        return examples

    def view_training_example(self, selected_row):
        """View details of the selected training example"""
        if not selected_row or len(selected_row) == 0:
            return [gr.update(value="No example selected")] * 5 + [gr.update()]
        
        filename = selected_row[0][0]  # Get filename from the first cell of the selected row
        filepath = os.path.join(TRAINING_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf8') as f:
                data = json.load(f)
            
            # Check if this is a comparison example
            is_comparison = data.get("source") == "AI_Comparison"
            
            return [
                filename,  # selected_example_name
                data.get("instruction", ""),  # example_task
                data.get("codebuddy_response" if is_comparison else "response", ""),  # example_codebuddy_response
                data.get("other_ai_name", "N/A"),  # example_other_ai
                data.get("other_ai_response", "N/A"),  # example_other_ai_response
                data.get("comparison_notes", "")  # example_notes
            ]
        except Exception as e:
            return [
                filename,
                f"Error loading example: {str(e)}",
                "",
                "",
                "",
                ""
            ]

    def save_example_notes(self, filename, notes):
        """Save notes for the selected example"""
        if not filename:
            return "No example selected"
        
        filepath = os.path.join(TRAINING_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf8') as f:
                data = json.load(f)
            
            # Update notes
            data["comparison_notes"] = notes
            
            with open(filepath, 'w', encoding='utf8') as f:
                json.dump(data, f, indent=2)
            
            return f"Notes saved for {filename}"
        except Exception as e:
            return f"Error saving notes: {str(e)}"

    def delete_training_example(self, selected_row):
        """Delete the selected training example"""
        if not selected_row or len(selected_row) == 0:
            return "No example selected", []
        
        filename = selected_row[0][0]  # Get filename from the first cell of the selected row
        filepath = os.path.join(TRAINING_DIR, filename)
        
        try:
            os.remove(filepath)
            return f"Deleted example: {filename}", self.refresh_training_examples()
        except Exception as e:
            return f"Error deleting example: {str(e)}", []

    ### Interface Setup
    def setup_interface(self):
        """Create the modernized Gradio interface using the theme module"""
        
        # Get the custom theme from our theme module
        custom_theme = create_theme()
        
        with gr.Blocks(theme=custom_theme, css=custom_css, title=APP_NAME) as interface:
            # Header with improved styling
            with gr.Row(variant="panel", elem_classes="header-container"):
                with gr.Column(scale=1, min_width=100):
                    if os.path.exists(APP_LOGO):
                        # Get properly sized logo
                        logo_config = get_logo_with_dimensions(APP_LOGO)
                        gr.Image(
                            logo_config["path"], 
                            label="", 
                            show_label=False, 
                            height=logo_config["height"],
                            width=logo_config["width"],
                            container=False, 
                            elem_classes="logo-image"
                        )
                with gr.Column(scale=5):
                    gr.Markdown(f"<h1 class='app-title'>{APP_NAME}</h1>")
                    gr.Markdown(f"<p class='app-tagline'>{APP_TAGLINE}</p>")
            
            # Tabs with modern styling
            with gr.Tabs():
                with gr.Tab("Chat", elem_classes="tab-content"):
                    with gr.Column(elem_classes="chat-container"):
                        # Side-by-side layout for chat and code
                        with gr.Row(elem_classes="chat-code-container"):
                            # Left column - Chat
                            with gr.Column(elem_classes="chat-column"):
                                gr.Markdown("<p class='section-label'>Conversation</p>")
                                logo_path = os.path.join(os.path.dirname(__file__), APP_LOGO)
                                chatbot = gr.Chatbot(
                                    height=400,
                                    avatar_images=(None, logo_path),
                                    show_copy_button=True,
                                    type='messages',
                                    elem_classes="modern-chatbot"
                                )
                                
                                # Input area with better styling
                                with gr.Row():
                                    with gr.Column(scale=5):
                                        user_input = gr.Textbox(
                                            show_label=False,
                                            placeholder="Ask me to write some Python or PowerShell code...",
                                            lines=3,
                                            elem_classes="modern-input",
                                            container=False,
                                            submit_btn=None,
                                            autofocus=True,
                                            max_lines=10
                                        )
                                    
                                    with gr.Column(scale=1, min_width=100):
                                        submit_btn = gr.Button("Send", variant="primary", elem_classes="send-button")
                            
                            # Right column - Code display
                            with gr.Column(elem_classes="code-column"):
                                gr.Markdown("<p class='section-label'>Generated Code</p>")
                                code_display = gr.Code(
                                    language="python",
                                    label="",
                                    show_label=False,
                                    lines=15,
                                    elem_classes="code-display"
                                )
                        
                        # Status message in its own container
                        with gr.Row(elem_classes="status-container"):
                            status_text = gr.Textbox(
                                label="Status", 
                                interactive=False, 
                                value="Ready - No models loaded yet",
                                elem_classes="status-text"
                            )
                        
                        # Reorganized button layout
                        with gr.Row(elem_classes="action-buttons-container"):
                            with gr.Column(elem_classes="action-button-group"):
                                clear_btn = gr.Button("Clear Conversation", elem_classes="action-button")
                                unload_btn = gr.Button("Unload Models", elem_classes="action-button")
                            
                            with gr.Column(elem_classes="action-button-group"):
                                learn_btn = gr.Button("Learn from Response", elem_classes="action-button")
                                settings_btn = gr.Button("Settings", elem_classes="action-button")
                        
                        with gr.Row(elem_classes="feedback-buttons"):
                            with gr.Column(scale=1):
                                like_btn = gr.Button("👍 Like", elem_classes="feedback-button")
                            with gr.Column(scale=1):
                                dislike_btn = gr.Button("👎 Dislike", elem_classes="feedback-button")
                        
                        # Settings accordion - MODIFIED to include language selector
                        with gr.Accordion("Settings", open=False, elem_classes="settings-accordion", visible=False) as settings_accordion:
                            # ADDED: Language selector moved here
                            with gr.Row(elem_classes="language-selector-container"):
                                with gr.Column(scale=3):
                                    gr.Markdown("<p class='section-label'>Select Programming Language</p>")
                                    language_selector = gr.Radio(
                                        choices=["Auto Detect", "Python", "PowerShell"],
                                        value="Auto Detect",
                                        label="Language Mode",
                                        interactive=True,
                                        elem_classes="language-options"
                                    )
                                with gr.Column(scale=2):
                                    language_indicator = gr.Markdown(
                                        "**Current Language**: Auto Detect", 
                                        elem_classes="language-indicator"
                                    )
                            
                            # Existing settings
                            with gr.Row():
                                temperature = gr.Slider(
                                    minimum=0.0, maximum=1.0, value=0.2, step=0.1,
                                    label="Temperature (0 = deterministic, 1 = creative)",
                                    elem_classes="modern-slider"
                                )
                            with gr.Row():
                                max_tokens = gr.Slider(
                                    minimum=128, maximum=2048, value=1024, step=128,
                                    label="Max Tokens",
                                    elem_classes="modern-slider"
                                )
                                
                            # Action buttons (already present)
                            with gr.Row(elem_classes="action-buttons"):
                                clear_settings_btn = gr.Button("Clear Conversation", elem_classes="action-button")
                                learn_settings_btn = gr.Button("Learn from Current Response", elem_classes="action-button")
                            
                            with gr.Row(elem_classes="feedback-buttons"):
                                like_settings_btn = gr.Button("👍 Like", elem_classes="feedback-button")
                                dislike_settings_btn = gr.Button("👎 Dislike", elem_classes="feedback-button")
                    
                with gr.Tab("AI Comparison", elem_classes="tab-content"):
                    gr.Markdown(f"<h2 class='section-title'>{APP_NAME} vs Other AI Systems</h2>")
                    gr.Markdown("<p class='section-description'>Compare responses between CodeBuddy and other AI systems. This helps improve our model training.</p>")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            comparison_language = gr.Radio(
                                choices=["Auto Detect", "Python", "PowerShell"],
                                value="Auto Detect",
                                label="Language",
                                interactive=True,
                                elem_classes="language-options"
                            )
                        
                        with gr.Column(scale=2):
                            other_ai_name = gr.Textbox(
                                label="Other AI System Name",
                                placeholder="e.g., ChatGPT, Claude, Gemini",
                                value="ChatGPT",
                                elem_classes="modern-input"
                            )
                    
                    question_input = gr.Textbox(
                        label="Programming Question or Task",
                        placeholder="Enter your programming question or task here...",
                        lines=3, 
                        max_lines=10,
                        elem_classes="modern-input"
                    )
                    
                    with gr.Row():
                        with gr.Column():
                            codebuddy_response = gr.Textbox(
                                label=f"{APP_NAME} Response",
                                placeholder=f"Paste the {APP_NAME} response here...",
                                lines=10,
                                elem_classes="modern-input response-field"
                            )
                        
                        with gr.Column():
                            other_ai_response = gr.Textbox(
                                label="Other AI Response",
                                placeholder="Paste the other AI system's response here...",
                                lines=10,
                                elem_classes="modern-input response-field"
                            )
                    
                    save_comparison_btn = gr.Button("Save Comparison Example", variant="primary", elem_classes="action-button")
                    comparison_status = gr.Textbox(label="Status", interactive=False, elem_classes="status-text")
                    
                    # Optional: Add buttons to copy from chat history
                    with gr.Row(elem_classes="comparison-actions"):
                        copy_from_chat_btn = gr.Button("Copy Last Question & Response from Chat", elem_classes="action-button")
                    
                with gr.Tab("Training Data", elem_classes="tab-content"):
                    gr.Markdown(f"<h2 class='section-title'>{APP_NAME} Training Data Management</h2>")
                    gr.Markdown("<p class='section-description'>Organize and export your training examples for both Python and PowerShell.</p>")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            # Language filter with modern styling
                            training_language_filter = gr.Radio(
                                choices=["All", "Python", "PowerShell"],
                                value="All",
                                label="Language Filter",
                                interactive=True,
                                elem_classes="language-filter"
                            )
                        
                        with gr.Column(scale=1):
                            # Add source type filter
                            training_source_filter = gr.Radio(
                                choices=["All Sources", "Comparison Only", "Feedback Only", "Manual Only"],
                                value="All Sources",
                                label="Source Filter",
                                interactive=True,
                                elem_classes="source-filter"
                            )
                    
                    # Examples list with improved styling
                    training_examples_list = gr.Dataframe(
                        headers=["Filename", "Source", "Language", "Timestamp", "Task Preview"],
                        datatype=["str", "str", "str", "str", "str"],
                        label="Saved Training Examples",
                        elem_classes="examples-table",
                        interactive=True  # Make selectable
                    )
                    
                    with gr.Row():
                        refresh_examples_btn = gr.Button("Refresh List", elem_classes="action-button")
                        view_example_btn = gr.Button("View Selected Example", elem_classes="action-button")
                        delete_example_btn = gr.Button("Delete Selected", variant="stop", elem_classes="action-button")
                    
                    # Add a collapsible section to view example details
                    with gr.Accordion("Example Details", open=False, elem_classes="example-details-accordion"):
                        selected_example_name = gr.Textbox(label="Filename", interactive=False)
                        
                        with gr.Tabs() as example_detail_tabs:
                            with gr.Tab("Question/Task"):
                                example_task = gr.Textbox(label="Programming Task", lines=5, interactive=False)
                            
                            with gr.Tab(f"{APP_NAME} Response"):
                                example_codebuddy_response = gr.Textbox(label=f"{APP_NAME} Response", lines=10, interactive=False)
                            
                            with gr.Tab("Other AI Response"):
                                example_other_ai = gr.Textbox(label="AI System", interactive=False)
                                example_other_ai_response = gr.Textbox(label="Response", lines=10, interactive=False)
                            
                            with gr.Tab("Comparison Notes"):
                                example_notes = gr.Textbox(label="Notes", lines=5, interactive=True, elem_classes="note-field")
                                save_notes_btn = gr.Button("Save Notes", elem_classes="action-button")
                    
                with gr.Tab("About", elem_classes="tab-content"):
                    # About content remains the same as in the previous version
                    gr.Markdown(f"<h1 class='about-title'>{APP_NAME}</h1>")
                    gr.Markdown(f"<p class='about-tagline'>{APP_TAGLINE}</p>")
                    
                    # About content (same as previous version)
                    gr.Markdown("""
                    <div class="about-content">
                        <!-- Content remains the same -->
                    </div>
                    """)
            
            # Define all functions first before connecting any buttons
            
            # Function to toggle settings visibility
            def toggle_settings():
                return gr.update(visible=not settings_accordion.visible)
            
            # Enhanced model unloading function
            def unload_models_enhanced():
                # Unload all currently loaded models
                models_unloaded = []
                for language in ['python', 'powershell']:
                    if self.model_manager.is_model_loaded(language):
                        self.model_manager.unload_model(language)
                        models_unloaded.append(language.capitalize())
                
                # Force additional cleanup
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                if models_unloaded:
                    return f"Unloaded models: {', '.join(models_unloaded)}. GPU memory freed."
                else:
                    return "No models were loaded to unload."
            
            # Language detection functions
            def detect_and_update_language(message):
                if not message:
                    return "Auto Detect", "**Current Language**: Auto Detect"
                
                # Use the model manager's language detection
                detected_language = self.model_manager.detect_language(message)
                language_name = detected_language.capitalize()
                
                return "Auto Detect", f"**Current Language**: {language_name}"

            def set_language(choice):
                if choice == "Auto Detect":
                    return "**Current Language**: Auto Detect"
                
                return f"**Current Language**: {choice}"
            
            # Clear conversation handler
            def clear_all():
                return [], gr.update(value="Conversation cleared", visible=True), gr.update(value="", language="python")
            
            # Save current response function
            def save_current_response(chat_history):
                if len(chat_history) == 0:
                    return gr.update(value="No conversation to learn from.", visible=True)
                
                # Get the last user message and bot response
                last_user_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'user'), None)
                last_bot_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'assistant'), None)
                
                if not last_user_msg or not last_bot_msg:
                    return gr.update(value="Incomplete conversation to learn from.", visible=True)
                result = self.save_training_example(last_user_msg['content'], last_bot_msg['content'], APP_NAME)
                return gr.update(value=result, visible=True)
            
            # Function to copy from chat history to comparison tab
            def copy_from_chat(chat_history):
                if not chat_history or len(chat_history) < 2:
                    return "", "", gr.update(value="No complete conversation found in chat history.", visible=True)
                
                # Get the last user message and bot response
                last_user_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'user'), None)
                last_bot_msg = next((msg for msg in reversed(chat_history) if msg.get('role') == 'assistant'), None)
                
                if not last_user_msg or not last_bot_msg:
                    return "", "", gr.update(value="Incomplete conversation in chat history.", visible=True)
                
                # Return the contents to populate the comparison fields
                return (
                    last_user_msg['content'],  # question
                    last_bot_msg['content'],   # codebuddy response
                    gr.update(value="Copied from chat history!", visible=True)
                )
            # Modified respond function to handle the new layout
            def respond(message, chat_history, lang_choice, temp, max_len):
                if not message.strip():
                    return "", chat_history, gr.update(value="Empty message", visible=True), gr.update(value="", language="python")
                
                # Convert chat_history to new message format if it's not already
                if chat_history and isinstance(chat_history[0], list):
                    chat_history = [
                        {"role": "user", "content": msg[0]} if isinstance(msg[0], str) else msg[0]
                        for msg in chat_history
                    ]
                
                # Append new user message
                chat_history.append({
                    "role": "user", 
                    "content": message
                })
                
                # Yield chat_history to update UI with user message first
                yield "", chat_history, gr.update(value="Processing your request...", visible=True), gr.update(value="", language="python")
                
                # Process language selection
                selected_language = None if lang_choice == "Auto Detect" else lang_choice.lower()
                
                # Set a default display language for code highlighting that's compatible with Gradio
                if selected_language == "powershell":
                    display_language = "bash"  # Use bash highlighting for PowerShell as it's close enough
                else:
                    display_language = selected_language if selected_language else "python"
                
                # Before generating, ensure we unload any other models to free memory
                if selected_language and selected_language != "auto detect":
                    # Unload other language models if they're loaded
                    other_language = "powershell" if selected_language == "python" else "python"
                    if self.model_manager.is_model_loaded(other_language):
                        self.model_manager.unload_model(other_language)
                        yield "", chat_history, gr.update(
                            value=f"Unloaded {other_language.capitalize()} model to free memory",
                            visible=True
                        ), gr.update(value="", language=display_language)
                
                # Use generator to stream responses
                bot_response = ""
                code_content = ""
                for response in self.generate_code(
                    message,
                    chat_history=chat_history,
                    language=selected_language,
                    temperature=temp, 
                    max_new_tokens=max_len
                ):
                    # If the response is a status message, update status
                    if response == self.status_message:
                        yield "", chat_history, gr.update(value=response, visible=True), gr.update(value="", language=display_language)
                        continue
                    
                    # Otherwise, it's generated code - extract actual code from markdown
                    bot_response = response
                    
                    # Extract code from markdown code blocks
                    code_match = re.search(r'```(?:\w+)?\s*\n([\s\S]*?)\n```', response)
                    if code_match:
                        code_content = code_match.group(1).strip()
                        # Update detected language from the code block if present
                        lang_match = re.search(r'```(\w+)', response)
                        if lang_match:
                            detected_lang = lang_match.group(1).lower()
                            # Map PowerShell to bash for display purposes
                            if detected_lang == "powershell":
                                display_language = "bash"
                            else:
                                display_language = detected_lang
                
                # MODIFIED: Extract explanation text before and after the code block
                explanation_before = ""
                explanation_after = ""
                
                # Get text before the code block
                before_match = re.match(r'^(.*?)```', bot_response, re.DOTALL)
                if before_match:
                    explanation_before = before_match.group(1).strip()
                
                # Get text after the code block
                after_match = re.search(r'```[\w]*\n[\s\S]*?\n```\s*([\s\S]*)', bot_response)
                if after_match:
                    explanation_after = after_match.group(1).strip()
                
                # Create a simplified chat response without the code block
                if explanation_before or explanation_after:
                    chat_response = ""
                    if explanation_before:
                        chat_response += explanation_before
                    
                    # Add a note about the code being in the code panel
                    chat_response += "\n\n*The generated code is available in the code panel.*" if explanation_before else "*The generated code is available in the code panel.*"
                    
                    if explanation_after:
                        chat_response += "\n\n" + explanation_after
                else:
                    # If no explanations were found, provide a simple message
                    chat_response = "I've generated the requested code. Please see the code panel for the implementation."
                
                # Add the simplified response to chat history
                chat_history.append({
                    "role": "assistant", 
                    "content": chat_response  # Only explanation text, no code
                })
                
                # Get the language that was actually used if not detected earlier
                if not selected_language:
                    selected_language = self.model_manager.detect_language(message)
                
                # Ensure we're using a supported language for the Gradio code component
                if selected_language == "powershell":
                    display_message = f"Code generation complete using PowerShell model (displayed with bash syntax highlighting)"
                else:
                    display_message = f"Code generation complete using {selected_language.capitalize()} model"
                
                yield "", chat_history, gr.update(
                    value=display_message, 
                    visible=True
                ), gr.update(value=code_content, language=display_language)
            
            # Settings button connection
            settings_btn.click(
                fn=toggle_settings,
                inputs=[],
                outputs=[settings_accordion]
            )
            
            # Unload models button
            unload_btn.click(
                fn=unload_models_enhanced,
                inputs=None,
                outputs=status_text
            )
            
            # Language detection and selection
            user_input.change(
                fn=detect_and_update_language,
                inputs=[user_input],
                outputs=[language_selector, language_indicator]
            )
            
            language_selector.change(
                fn=set_language,
                inputs=[language_selector],
                outputs=[language_indicator]
            )
            
            # Connect the clear buttons
            clear_btn.click(
                fn=clear_all,
                inputs=None,
                outputs=[chatbot, status_text, code_display]
            )
            
            clear_settings_btn.click(
                fn=clear_all,
                inputs=None,
                outputs=[chatbot, status_text, code_display]
            )
            
            # Connect the learn buttons
            learn_btn.click(
                fn=save_current_response,
                inputs=[chatbot],
                outputs=[status_text]
            )
            
            learn_settings_btn.click(
                fn=save_current_response,
                inputs=[chatbot],
                outputs=[status_text]
            )
            
            # Connect the feedback buttons
            like_btn.click(
                fn=lambda chat_history: self.save_positive_feedback(chat_history), 
                inputs=[chatbot], 
                outputs=[status_text]
            )
            
            dislike_btn.click(
                fn=lambda chat_history: self.save_negative_feedback(chat_history), 
                inputs=[chatbot], 
                outputs=[status_text]
            )
            
            like_settings_btn.click(
                fn=lambda chat_history: self.save_positive_feedback(chat_history), 
                inputs=[chatbot], 
                outputs=[status_text]
            )
            
            dislike_settings_btn.click(
                fn=lambda chat_history: self.save_negative_feedback(chat_history), 
                inputs=[chatbot], 
                outputs=[status_text]
            )
            
            # Stream responses to show generation progress
            submit_btn.click(
                fn=respond,
                inputs=[user_input, chatbot, language_selector, temperature, max_tokens],
                outputs=[user_input, chatbot, status_text, code_display],
                queue=True
            )

            user_input.submit(
                fn=respond,
                inputs=[user_input, chatbot, language_selector, temperature, max_tokens],
                outputs=[user_input, chatbot, status_text, code_display],
                queue=True
            )
            
            # Connect the AI comparison tab buttons
            save_comparison_btn.click(
                fn=self.save_comparison_example,
                inputs=[question_input, codebuddy_response, other_ai_response, other_ai_name, comparison_language],
                outputs=[comparison_status]
            )
            
            # Connect the copy from chat button
            copy_from_chat_btn.click(
                fn=copy_from_chat,
                inputs=[chatbot],
                outputs=[question_input, codebuddy_response, comparison_status]
            )
            
            # Connect all the training data tab functions
            refresh_examples_btn.click(
                fn=lambda language, source: self.refresh_training_examples(language, source),
                inputs=[training_language_filter, training_source_filter],
                outputs=[training_examples_list]
            )

            training_language_filter.change(
                fn=lambda language, source: self.refresh_training_examples(language, source),
                inputs=[training_language_filter, training_source_filter],
                outputs=[training_examples_list]
            )

            training_source_filter.change(
                fn=lambda language, source: self.refresh_training_examples(language, source),
                inputs=[training_language_filter, training_source_filter],
                outputs=[training_examples_list]
            )

            view_example_btn.click(
                fn=self.view_training_example,
                inputs=[training_examples_list],
                outputs=[
                    selected_example_name,
                    example_task,
                    example_codebuddy_response,
                    example_other_ai,
                    example_other_ai_response,
                    example_notes
                ]
            )

            save_notes_btn.click(
                fn=self.save_example_notes,
                inputs=[selected_example_name, example_notes],
                outputs=status_text
            )

            delete_example_btn.click(
                fn=self.delete_training_example,
                inputs=[training_examples_list],
                outputs=[status_text, training_examples_list]
            )
            
            # Initial load of training examples
            training_examples_list.value = self.refresh_training_examples()
        
        return interface
   
# Main entry point
if __name__ == "__main__":
    print(f"\nStarting {APP_NAME}...")
    
    # Get Hugging Face token if needed
    hf_token = os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not hf_token:
        import getpass
        print("\nYou need a Hugging Face token to access the models.")
        print("Get your token at: https://huggingface.co/settings/tokens")
        hf_token = getpass.getpass("\nEnter your Hugging Face token: ")
    
    # Create and launch the app
    try:
        app = MultiLanguageCodeBuddy(hf_token=hf_token)
        interface = app.setup_interface()
        interface.launch(share=False)  # Set share=True for a public link
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nTo use this application, you need:")
        print("1. A Hugging Face account")
        print("2. Accept the model licenses at Hugging Face")
        print("3. Generate a Hugging Face token at: https://huggingface.co/settings/tokens")