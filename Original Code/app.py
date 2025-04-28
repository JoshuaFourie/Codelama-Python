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

# Define directories
CACHE_DIR = "models"
TRAINING_DIR = "training_data"
CHAT_HISTORY_DIR = "chat_history"

# Import application settings from theme
from theme import APP_NAME, APP_TAGLINE, APP_LOGO, PRIMARY_COLOR, SECONDARY_COLOR, AVATAR_EMOJI

# Add this CSS directly to your existing app.py file
custom_css = """
/* Modern dark theme */
body, .gradio-container {
    background-color: #111827 !important;
    color: #F9FAFB !important;
}

/* AI Comparison Tab Styling */
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
.code-display-container {
    margin-top: 10px;
    margin-bottom: 15px;
}

.code-display {
    border-radius: 8px;
    border: 1px solid #334155;
    background-color: #1e1e1e;
    font-family: 'Fira Code', 'Cascadia Code', 'Courier New', monospace;
}

.code-display pre {
    margin: 0;
}

.code-display .cm-editor {
    background-color: #1e1e1e;
}

.section-label {
    font-weight: 600;
    margin-bottom: 8px;
    color: #94a3b8;
}

/* Adjust chatbot to accommodate code display */
.modern-chatbot {
    margin-bottom: 0;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .comparison-actions {
        flex-direction: column;
    }
    
    .action-button {
        width: 100%;
        margin-bottom: 8px;
    }
}
"""

# Create necessary directories
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(TRAINING_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

class MultiLanguageCodeBuddy:
    def __init__(self, hf_token=None):
        # Define model configurations - MODIFIED TO USE CODELLAMA 13B INSTRUCT FOR BOTH LANGUAGES
        models_config = {
            'python': {
                'model_name': 'meta-llama/CodeLlama-13b-Instruct-hf',
                'prompt_template': "Write Python code for the following request:\n\n{prompt}\n\nCode:"
            },
            'powershell': {
                'model_name': 'meta-llama/CodeLlama-13b-Instruct-hf',  # Same model for PowerShell
                'prompt_template': "You are an expert PowerShell programmer. Write PowerShell code for the following request:\n\n{prompt}\n\nEnsure the code follows PowerShell best practices and includes comments. Provide only the code.\n\n```powershell"
            }
        }
        
        # Initialize model manager
        self.model_manager = MultiModelManager(models_config, cache_dir=CACHE_DIR)
        
        # Store the auth token for later use but don't load any models yet
        self.model_manager.set_auth_token(hf_token)
        
        # Status message for model loading state
        self.status_message = ""
    
    def generate_code(self, prompt, chat_history=None, language=None, temperature=0.2, max_new_tokens=1024, repetition_penalty=1.1):
        """Generate code based on prompt and chat history, lazily loading models as needed"""
        self.status_message = "Detecting language..."
        yield self.status_message
        
        # Detect which language is being requested if not specified
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

    def setup_interface(self):
        """Create the modernized Gradio interface using the theme module"""
        
        # Get the custom theme from our theme module
        custom_theme = create_theme()
        
        with gr.Blocks(theme=custom_theme, css=custom_css, title=APP_NAME) as interface:
            # Header with improved styling
            with gr.Row(variant="panel", elem_classes="header-container"):
                with gr.Column(scale=1, min_width=100):
                    if os.path.exists(APP_LOGO):
                        gr.Image(APP_LOGO, label="", show_label=False, height=50, container=False, elem_classes="logo-image")
                with gr.Column(scale=5):
                    gr.Markdown(f"<h1 class='app-title'>{APP_NAME}</h1>")
                    gr.Markdown(f"<p class='app-tagline'>{APP_TAGLINE}</p>")
            
            # Tabs with modern styling
            with gr.Tab("Chat", elem_classes="tab-content"):
                with gr.Column(elem_classes="chat-container"):
                    # Language selector with improved styling
                    with gr.Row(elem_classes="language-selector-row"):
                        with gr.Column(scale=2, elem_classes="language-selector-container"):
                            gr.Markdown("<p class='section-label'>Language</p>")
                            language_selector = gr.Radio(
                                choices=["Auto Detect", "Python", "PowerShell"],
                                value="Auto Detect",
                                label="",
                                show_label=False,
                                interactive=True,
                                elem_classes="language-options"
                            )
                        with gr.Column(scale=3, elem_classes="language-indicator-container"):
                            language_indicator = gr.Markdown(
                                "**Current Language Mode**: Auto Detect", 
                                elem_classes="language-indicator"
                            )
                    
                    # Improved chat display
                    chatbot = gr.Chatbot(
                        height=400,  # Reduced height to make room for code display
                        avatar_images=(None, AVATAR_EMOJI),
                        show_copy_button=True,
                        type='messages',
                        elem_classes="modern-chatbot"
                    )
                    
                    # Add a separate code display component
                    with gr.Row(elem_classes="code-display-container"):
                        gr.Markdown("<p class='section-label'>Generated Code</p>")
                        code_display = gr.Code(
                            language="python",
                            label="",
                            show_label=False,
                            lines=15,
                            elem_classes="code-display"
                        )
                    
                    # Input area with better styling
                    with gr.Row(elem_classes="input-container"):
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
                        
                        # Status message - Now visible by default to show model loading status
                        status_text = gr.Textbox(
                            label="Status", 
                            interactive=False, 
                            value="Ready - No models loaded yet",
                            elem_classes="status-text"
                        )
                        
                        # Settings with accordion styling
                        with gr.Accordion("Settings", open=False, elem_classes="settings-accordion"):
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
                            # New option to unload models
                            with gr.Row():
                                unload_btn = gr.Button("Unload Models (Free Memory)", elem_classes="action-button")
                        
                        # Action buttons with improved styling
                        with gr.Row(elem_classes="action-buttons"):
                            clear_btn = gr.Button("Clear Conversation", elem_classes="action-button")
                            learn_btn = gr.Button("Learn from Current Response", elem_classes="action-button")
                        
                        with gr.Row(elem_classes="feedback-buttons"):
                            like_btn = gr.Button("👍 Like", elem_classes="feedback-button")
                            dislike_btn = gr.Button("👎 Dislike", elem_classes="feedback-button")
                
                # AI Comparison Tab
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
                
                # Training Data Tab
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
                
                # About Tab
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
            
            # Connect event handlers
            def detect_and_update_language(message):
                if not message:
                    return "Auto Detect", "**Current Language Mode**: Auto Detect"
                
                # Use the model manager's language detection
                detected_language = self.model_manager.detect_language(message)
                language_name = detected_language.capitalize()
                
                return "Auto Detect", f"**Current Language Mode**: {language_name}"

            def set_language(choice):
                if choice == "Auto Detect":
                    return "**Current Language Mode**: Auto Detect"
                
                return f"**Current Language Mode**: {choice}"

            # Connect language detection to input
            user_input.change(
                fn=detect_and_update_language,
                inputs=[user_input],
                outputs=[language_selector, language_indicator]
            )
            
            # Connect language selector to indicator
            language_selector.change(
                fn=set_language,
                inputs=[language_selector],
                outputs=[language_indicator]
            )
            
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
                detected_language = selected_language if selected_language else "python"  # Default language for code display
                
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
                        yield "", chat_history, gr.update(value=response, visible=True), gr.update(value="", language=detected_language)
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
                            detected_language = lang_match.group(1).lower()
                
                # Create a cleaner chat response without the code block
                chat_response = "I've generated the requested code. You can see it in the code panel below."
                
                # Add bot response to chat history, but with the cleaner message
                chat_history.append({
                    "role": "assistant", 
                    "content": chat_response
                })
                
                # Get the language that was actually used if not detected earlier
                if not detected_language:
                    detected_language = self.detect_language(message)
                
                yield "", chat_history, gr.update(
                    value=f"Code generation complete using {detected_language.capitalize()} model", 
                    visible=True
                ), gr.update(value=code_content, language=detected_language)

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

            # Update unload models handler
            unload_btn.click(
                fn=self.unload_current_model,
                inputs=None,
                outputs=status_text
            )

            # Modify clear conversation handler
            def clear_all():
                return [], gr.update(value="Conversation cleared", visible=True), gr.update(value="", language="python")

            # Update the clear conversation handler
            clear_btn.click(
                fn=clear_all,
                inputs=None,
                outputs=[chatbot, status_text, code_display]
            )
            
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
            
            # Connect learn button
            learn_btn.click(
                fn=save_current_response,
                inputs=[chatbot],
                outputs=[status_text]
            )
            
            # Connect feedback buttons with lambda to correctly pass self
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