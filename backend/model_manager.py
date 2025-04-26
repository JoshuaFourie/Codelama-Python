# model_manager.py - Improved model management with tokenization handling

import os
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig
)

class MultiModelManager:
    def __init__(self, models_config, cache_dir="models"):
        """
        Initialize the multi-model manager with improved tokenization handling
        
        :param models_config: Dictionary of model configurations
        :param cache_dir: Directory to cache model files
        """
        self.models_config = models_config
        self.cache_dir = cache_dir
        self.loaded_models = {}
        self.loaded_tokenizers = {}
    
    def _configure_quantization(self):
        """
        Configure 4-bit quantization for efficient model loading
        """
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
    
    def load_model(self, language, hf_token=None):
        """
        Load a model with improved tokenization and quantization
        
        :param language: Language of the model to load
        :param hf_token: Hugging Face authentication token
        :return: Loaded model and tokenizer
        """
        if language in self.loaded_models:
            return self.loaded_models[language], self.loaded_tokenizers[language]
        
        # Get model configuration
        model_config = self.models_config.get(language.lower())
        if not model_config:
            raise ValueError(f"No model configuration found for language: {language}")
        
        model_name = model_config['model_name']
        
        # Authentication for private models
        auth_kwargs = {}
        if hf_token:
            auth_kwargs['token'] = hf_token
        
        # Load tokenizer with improved settings
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            **auth_kwargs,
            cache_dir=self.cache_dir,
            # Improved tokenizer configuration
            padding_side='left',
            truncation_side='left',
            use_fast=True
        )
        
        # Ensure pad token is set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id
        
        # Load model with 4-bit quantization
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **auth_kwargs,
            cache_dir=self.cache_dir,
            quantization_config=self._configure_quantization(),
            device_map='auto'  # Automatically distribute across available devices
        )
        
        # Update model configuration for padding and generation
        model.config.pad_token_id = tokenizer.pad_token_id
        model.config.eos_token_id = tokenizer.eos_token_id
        
        # Store loaded models
        self.loaded_models[language] = model
        self.loaded_tokenizers[language] = tokenizer
        
        return model, tokenizer
    
    def generate_code(self, prompt, language=None, 
                      temperature=0.2, max_new_tokens=1024, 
                      repetition_penalty=1.1):
        """
        Generate code with improved token handling
        
        :param prompt: Input prompt for code generation
        :param language: Specific language to use (optional)
        :param temperature: Sampling temperature
        :param max_new_tokens: Maximum number of tokens to generate
        :param repetition_penalty: Penalty for repeating tokens
        :yield: Generated code responses
        """
        # Detect language if not specified
        if language is None:
            language = self.detect_language(prompt)
        
        # Load model and tokenizer
        model, tokenizer = self.load_model(language)
        
        # Prepare input with attention mask
        inputs = tokenizer(
            prompt, 
            return_tensors="pt", 
            padding=True, 
            truncation=True,
            max_length=1024  # Prevent extremely long inputs
        )
        
        # Move inputs to the same device as the model
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate code with explicit attention mask and improved settings
        generated_ids = model.generate(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id
        )
        
        # Decode generated tokens
        generated_text = tokenizer.decode(
            generated_ids[0][inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        )
        
        yield generated_text
    
    def detect_language(self, prompt):
        """
        Detect programming language from the prompt
        
        :param prompt: Input text to analyze
        :return: Detected language (default to 'python')
        """
        # Simple language detection based on keywords
        prompt_lower = prompt.lower()
        
        # PowerShell detection
        powershell_keywords = ['get-', 'set-', 'new-', 'remove-', 'invoke-', 
                                'windows', 'azure', 'active directory', 
                                'powershell', 'cmdlet']
        if any(keyword in prompt_lower for keyword in powershell_keywords):
            return 'powershell'
        
        # Default to Python
        return 'python'
    
    def format_code(self, code, language):
        """
        Format code with basic syntax highlighting
        
        :param code: Generated code
        :param language: Programming language
        :return: Formatted code
        """
        # Basic code formatting
        return f"```{language}\n{code}\n```"