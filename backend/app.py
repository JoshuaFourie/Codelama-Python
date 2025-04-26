#!/usr/bin/env python
# backend/app.py - FastAPI backend for CodeBuddy AI

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the model manager
from model_manager import MultiModelManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define directories
CACHE_DIR = "models"
TRAINING_DIR = "training_data"
CHAT_HISTORY_DIR = "chat_history"

# Create necessary directories
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(TRAINING_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
os.makedirs(os.path.join(CHAT_HISTORY_DIR, "positive_feedback"), exist_ok=True)
os.makedirs(os.path.join(CHAT_HISTORY_DIR, "negative_feedback"), exist_ok=True)

# Models configuration
MODELS_CONFIG = {
    'python': {
        'model_name': 'meta-llama/CodeLlama-13b-Python-hf',
        'prompt_template': "Write Python code for the following request:\n\n{prompt}\n\nCode:"
    },
    'powershell': {
        'model_name': 'microsoft/phi-2',  # A good general model that handles PowerShell well
        'prompt_template': "You are an expert PowerShell programmer. Write PowerShell code for the following request:\n\n{prompt}\n\nEnsure the code follows PowerShell best practices and includes comments. Provide only the code.\n\n```powershell"
    }
}

# Create the FastAPI app
app = FastAPI(
    title="CodeBuddy AI API",
    description="Backend API for CodeBuddy AI code generation assistant",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get Hugging Face token from environment
HF_TOKEN = os.environ.get("HUGGING_FACE_HUB_TOKEN")

# Initialize model manager
model_manager = None

# Pydantic models for request/response validation
class GenerateRequest(BaseModel):
    prompt: str
    language: Optional[str] = "auto"
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 1024
    repetition_penalty: Optional[float] = 1.1

class GenerateResponse(BaseModel):
    code: str
    language: str

class FeedbackRequest(BaseModel):
    task: str
    solution: str
    type: str  # 'positive' or 'negative'

class FeedbackResponse(BaseModel):
    success: bool
    message: str

class TrainingRequest(BaseModel):
    task: str
    solution: str

class TrainingResponse(BaseModel):
    success: bool
    message: str
    id: str

class TrainingExample(BaseModel):
    filename: str
    source: str
    language: str
    timestamp: str
    taskPreview: str

class TrainingListResponse(BaseModel):
    success: bool
    examples: List[TrainingExample]

# Dependency to initialize and get model manager
def get_model_manager():
    global model_manager
    if model_manager is None:
        logger.info("Initializing model manager...")
        model_manager = MultiModelManager(MODELS_CONFIG, cache_dir=CACHE_DIR)
        # Load Python model by default
        model_manager.load_model('python', HF_TOKEN)
        logger.info("Model manager initialized")
    return model_manager

# Routes
@app.get("/")
async def root():
    return {"message": "CodeBuddy AI API is running"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_code(
    request: GenerateRequest,
    manager: MultiModelManager = Depends(get_model_manager)
):
    try:
        # Log request
        logger.info(f"Generating code for prompt: {request.prompt[:50]}...")
        
        # Determine language
        language = request.language
        if language == "auto":
            language = manager.detect_language(request.prompt)
            logger.info(f"Detected language: {language}")
        
        # Generate code
        code_generator = manager.generate_code(
            request.prompt,
            language=language,
            temperature=request.temperature,
            max_new_tokens=request.max_tokens,
            repetition_penalty=request.repetition_penalty
        )
        
        # Get response (this is a generator, take first item)
        code = next(code_generator)
        
        # Clean up response - remove markdown formatting
        if code.startswith("```"):
            code = code.strip()
            # Remove the first line (```language)
            code = '\n'.join(code.split('\n')[1:])
            # Remove the last line (```)
            if code.endswith("```"):
                code = code[:-3].strip()
        
        return {"code": code, "language": language}
    
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", response_model=FeedbackResponse)
async def save_feedback(request: FeedbackRequest):
    try:
        # Validate feedback type
        if request.type not in ["positive", "negative"]:
            raise HTTPException(status_code=400, detail="Feedback type must be 'positive' or 'negative'")
        
        # Determine language for the file
        language = get_model_manager().detect_language(request.task)
        language_name = language.capitalize()
        
        # Format timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        feedback_dir = "positive_feedback" if request.type == "positive" else "negative_feedback"
        filename = f"{feedback_dir}_{language_name}_{timestamp}.json"
        filepath = os.path.join(CHAT_HISTORY_DIR, feedback_dir, filename)
        
        # Prepare data
        data = {
            "instruction": request.task,
            "response": request.solution,
            "source": f"{request.type.capitalize()}_Feedback",
            "language": language_name,
            "timestamp": timestamp
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=2)
        
        return {
            "success": True,
            "message": f"{request.type.capitalize()} feedback saved to {filename}"
        }
    
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/training", response_model=TrainingResponse)
async def save_training_example(request: TrainingRequest):
    try:
        # Determine language
        language = get_model_manager().detect_language(request.task)
        language_name = language.capitalize()
        
        # Format timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename
        filename = f"Manual_{language_name}_{timestamp}.json"
        filepath = os.path.join(TRAINING_DIR, filename)
        
        # Prepare data
        data = {
            "instruction": request.task,
            "response": request.solution,
            "source": "Manual",
            "language": language_name,
            "timestamp": timestamp
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=2)
        
        return {
            "success": True,
            "message": f"Training example saved to {filename}",
            "id": filename
        }
    
    except Exception as e:
        logger.error(f"Error saving training example: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/training", response_model=TrainingListResponse)
async def get_training_examples(
    language: str = Query("All", description="Filter examples by language")
):
    try:
        examples = []
        
        # List all JSON files in the training directory
        for filename in os.listdir(TRAINING_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(TRAINING_DIR, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf8') as f:
                        data = json.load(f)
                        
                        # Extract language from the data
                        file_language = data.get("language", "Unknown")
                        
                        # Filter by language if filter is active
                        if language != "All" and file_language != language:
                            continue
                        
                        # Create a preview of the task
                        task_preview = data["instruction"][:50] + "..." if len(data["instruction"]) > 50 else data["instruction"]
                        
                        # Add to examples list
                        examples.append({
                            "filename": filename,
                            "source": data.get("source", "Unknown"),
                            "language": file_language,
                            "timestamp": data.get("timestamp", "Unknown"),
                            "taskPreview": task_preview
                        })
                except Exception as e:
                    # If error reading file, add with error info if not filtering
                    if language == "All":
                        examples.append({
                            "filename": filename,
                            "source": "Error",
                            "language": "Unknown",
                            "timestamp": "Error",
                            "taskPreview": f"Error reading file: {str(e)}"
                        })
        
        # Sort examples by timestamp (newest first)
        examples.sort(key=lambda x: x["timestamp"] if x["timestamp"] != "Unknown" and x["timestamp"] != "Error" else "", reverse=True)
        
        return {
            "success": True,
            "examples": examples
        }
    
    except Exception as e:
        logger.error(f"Error fetching training examples: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Log startup
    logger.info(f"Starting CodeBuddy AI API on port {port}")
    
    # Start the server
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)