# model_manager.py - Optimized for Ryzen 7800X3D CPU and RTX 4070 GPU with focus on CodeLlama-13B-Instruct

import os
import gc
import torch
import psutil
import numpy as np
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig
)

class MultiModelManager:
    def __init__(self, models_config, cache_dir="models"):
        """
        Initialize the model manager optimized for 7800X3D and RTX 4070
        with focus on CodeLlama-13B-Instruct model
        
        :param models_config: Dictionary of model configurations
        :param cache_dir: Directory to cache model files
        """
        self.models_config = {
            'python': {
                'model_name': 'meta-llama/CodeLlama-13b-Instruct-hf',
                'prompt_template': "Write Python code for the following request:\n\n{prompt}\n\nCode:",
                'supports_chat': True
            },
            'powershell': {
                'model_name': 'meta-llama/CodeLlama-13b-Instruct-hf',
                'prompt_template': "You are an expert PowerShell programmer. Write PowerShell code for the following request:\n\n{prompt}\n\nEnsure the code follows PowerShell best practices and includes comments. Provide only the code.\n\n```powershell",
                'supports_chat': True
            }
        }
        self.cache_dir = cache_dir
        self.loaded_models = {}
        self.loaded_tokenizers = {}
        
        # Detect CPU topology and configure for optimal performance
        self.cpu_info = self._get_cpu_info()
        self._configure_cpu()
        
        # Configure GPU for optimal performance
        self.gpu_info = self._configure_gpu()
        
        # Initialize thread pools for parallel operations
        self._setup_thread_pools()
        
        # Initialize authentication token for later use
        self.hf_token = None
        
        # Performance mode (balanced, speed, memory)
        self.performance_mode = "balanced"
        
        # Print system information
        self._print_system_info()

    def _get_cpu_info(self):
        """
        Get detailed CPU information optimized for 7800X3D
        """
        cpu_info = {
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'frequency': psutil.cpu_freq(),
            'architecture': os.uname().machine if hasattr(os, 'uname') else "unknown"
        }
        
        # Try to identify if this is a 7800X3D specifically
        try:
            import cpuinfo
            detailed_info = cpuinfo.get_cpu_info()
            cpu_info['model_name'] = detailed_info.get('brand_raw', 'Unknown')
            cpu_info['is_7800x3d'] = '7800X3D' in cpu_info['model_name']
        except:
            cpu_info['model_name'] = 'AMD Ryzen CPU (details unavailable)'
            cpu_info['is_7800x3d'] = True  # Assume true based on user input
            
        return cpu_info

    def _configure_cpu(self):
        """
        Configure for optimal performance on Ryzen 7800X3D
        """
        # Determine optimal worker counts based on CPU
        physical_cores = self.cpu_info['cores_physical']
        logical_cores = self.cpu_info['cores_logical']
        
        # For 7800X3D (8 cores, 16 threads)
        if self.cpu_info.get('is_7800x3d', False):
            # Use specific optimizations for 7800X3D with its 3D V-Cache
            print("Optimizing for AMD Ryzen 7800X3D with 3D V-Cache...")
            
            # V-Cache optimizations - adjust process affinity for cache-sensitive tasks
            self.inference_thread_count = physical_cores  # Use physical cores for inference
            self.tokenization_thread_count = logical_cores  # Use all logical cores for tokenization
            
            # Set optimal PyTorch thread settings for 7800X3D
            torch.set_num_threads(physical_cores)
            torch.set_num_interop_threads(2)  # Lower interop threads for 7800X3D's architecture
        else:
            # Generic CPU configuration
            self.inference_thread_count = max(2, physical_cores - 2)  # Reserve some cores
            self.tokenization_thread_count = logical_cores // 2
            
            # Default PyTorch threading
            torch.set_num_threads(physical_cores)
            
        # Configure numpy to use MKL if available
        try:
            np.show_config()  # This might show if MKL is being used
        except:
            pass

    def _setup_thread_pools(self):
        """
        Create optimized thread pools for parallel processing
        """
        # Thread pool for tokenization (I/O bound)
        self.tokenizer_pool = ThreadPoolExecutor(
            max_workers=self.tokenization_thread_count,
            thread_name_prefix="tokenizer"
        )
        
        # Process pool for CPU-intensive tasks
        # Using fewer workers to avoid oversubscription
        self.cpu_pool = ProcessPoolExecutor(
            max_workers=max(2, self.cpu_info['cores_physical'] // 2),
            mp_context=multiprocessing.get_context('spawn')  # Avoid fork issues
        )

    def _configure_gpu(self):
        """
        Configure GPU settings optimized for RTX 4070
        """
        gpu_info = {'available': False}
        
        # PyTorch configuration
        if torch.cuda.is_available():
            gpu_info['available'] = True
            gpu_info['count'] = torch.cuda.device_count()
            gpu_info['name'] = torch.cuda.get_device_name(0)
            
            try:
                gpu_info['capability'] = torch.cuda.get_device_capability(0)
            except:
                gpu_info['capability'] = (0, 0)
            
            # Enable TF32 precision (faster on RTX 30/40 series)
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Set to benchmark mode for optimized kernel selection
            torch.backends.cudnn.benchmark = True
            
            # For RTX 4070, enable additional optimizations
            if 'RTX 40' in gpu_info['name']:
                gpu_info['rtx40_series'] = True
                # Optimize memory allocation strategy for Ada Lovelace architecture
                os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
            else:
                gpu_info['rtx40_series'] = False
            
            # Configure PyTorch memory allocation
            torch.cuda.empty_cache()
        
        return gpu_info
    
    def _print_system_info(self):
        """
        Print detailed system information
        """
        print("\n" + "="*50)
        print(" SYSTEM INFORMATION")
        print("="*50)
        
        # CPU Information
        print("\nCPU Information:")
        print(f"  Model:          {self.cpu_info.get('model_name', 'Unknown')}")
        print(f"  Physical cores: {self.cpu_info['cores_physical']}")
        print(f"  Logical cores:  {self.cpu_info['cores_logical']}")
        if self.cpu_info.get('frequency'):
            print(f"  Frequency:      {self.cpu_info['frequency'].current/1000:.2f} GHz")
        print(f"  Architecture:   {self.cpu_info['architecture']}")
        print(f"  Optimized for 7800X3D: {self.cpu_info.get('is_7800x3d', False)}")
        
        # Memory Information
        mem = psutil.virtual_memory()
        print(f"\nSystem Memory: {mem.total / (1024**3):.1f} GB total, {mem.available / (1024**3):.1f} GB available")
        
        # GPU Information
        if self.gpu_info['available']:
            print("\nGPU Information:")
            print(f"  Device:       {self.gpu_info['name']}")
            print(f"  CUDA Version: {torch.version.cuda}")
            print(f"  RTX 40 Series: {self.gpu_info.get('rtx40_series', False)}")
            print(f"  Compute Capability: {self.gpu_info['capability']}")
            
            # Get GPU memory
            total_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  Memory:       {total_mem:.2f} GB")
        else:
            print("\nNo CUDA-capable GPU detected")
        
        # Thread Pool Configuration
        print("\nThread Pool Configuration:")
        print(f"  Inference threads:    {self.inference_thread_count}")
        print(f"  Tokenization threads: {self.tokenization_thread_count}")
        
        print("\nPyTorch Configuration:")
        print(f"  Threads:             {torch.get_num_threads()}")
        print(f"  Interop Threads:     {torch.get_num_interop_threads()}")
        print(f"  TF32 Enabled:        {torch.backends.cuda.matmul.allow_tf32}")
        print("="*50 + "\n")

    def _configure_quantization(self, optimize_for_rtx40=True):
        """
        Configure 4-bit quantization optimized for RTX 4070 
        with focus on CodeLlama-13B-Instruct
        """
        # Enhanced settings for RTX 40 series (Ada Lovelace architecture)
        if optimize_for_rtx40 and self.gpu_info.get('rtx40_series', False):
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_storage=torch.uint8  # More efficient on newer GPUs
            )
        
        # Default settings for other GPUs
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
    
    def set_auth_token(self, hf_token):
        """
        Set the Hugging Face authentication token for later use
        
        :param hf_token: Hugging Face authentication token
        """
        self.hf_token = hf_token
    
    def set_performance_mode(self, mode):
        """
        Set the performance mode for the model manager
        
        :param mode: 'balanced', 'speed', or 'memory'
        """
        valid_modes = ['balanced', 'speed', 'memory']
        if mode not in valid_modes:
            print(f"Invalid mode: {mode}. Using 'balanced' instead.")
            mode = 'balanced'
            
        self.performance_mode = mode
        print(f"Performance mode set to: {mode}")
        
        return mode
    
    def _parallel_tokenize(self, tokenizer, prompt, **kwargs):
        """
        Tokenize input in a separate thread to leverage multi-core CPU
        """
        return tokenizer(prompt, **kwargs)
    
    def load_model(self, language, hf_token=None):
        """
        Lazy load a model with enhanced memory management
        
        :param language: Language of the model to load
        :param hf_token: Hugging Face authentication token
        :return: Loaded model and tokenizer
        """
        # Import necessary libraries here to ensure they're available
        from transformers import BitsAndBytesConfig
        
        # Use instance token if not provided
        if hf_token is None:
            hf_token = self.hf_token
            
        # Check if model is already loaded
        if language in self.loaded_models:
            return self.loaded_models[language], self.loaded_tokenizers[language]
        
        # Get model configuration
        model_config = self.models_config.get(language.lower())
        if not model_config:
            raise ValueError(f"No model configuration found for language: {language}")
        
        model_name = model_config['model_name']
        print(f"\nLoading {language} model: {model_name}...")
        
        # Check if we need to unload other models to make room
        if torch.cuda.is_available():
            # Check if we have other models loaded
            other_languages = [lang for lang in self.loaded_models.keys() if lang != language]
            if other_languages:
                print(f"Unloading other models to make room for {language} model...")
                for other_lang in other_languages:
                    self.unload_model(other_lang)
        
        # Clear memory before loading new model
        self._optimize_memory()
        
        # Check available GPU memory before loading
        if torch.cuda.is_available():
            available_memory = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)
            available_gb = available_memory / (1024**3)
            print(f"Available GPU memory before loading: {available_gb:.2f} GB")
        
        # Authentication for private models
        auth_kwargs = {}
        if hf_token:
            auth_kwargs['token'] = hf_token
        
        # Use thread pool for tokenizer loading to leverage multi-core
        tokenizer_future = self.tokenizer_pool.submit(
            AutoTokenizer.from_pretrained,
            model_name, 
            **auth_kwargs,
            cache_dir=self.cache_dir,
            padding_side='left',
            truncation_side='left',
            use_fast=True
        )
        
        # For CodeLlama-13B-Instruct, use 4-bit quantization with memory optimizations
        print(f"Loading {language} model with PyTorch...")
        
        # Configure quantization - for 4-bit quantization without CPU offloading
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        
        try:
            # Try to load the model with 4-bit quantization, keeping everything on GPU
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **auth_kwargs,
                cache_dir=self.cache_dir,
                quantization_config=bnb_config,
                device_map={"": 0},  # Put everything on GPU
                torch_dtype=torch.float16,  # Use half precision for better performance
            )
        except Exception as e:
            print(f"Error loading model with 4-bit quantization: {e}")
            print("\nRetrying with full 16-bit precision (no quantization)...")
            
            # If the first attempt fails, try without quantization
            self._optimize_memory()
            
            try:
                # Attempt to load without quantization, but with CPU offloading
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    **auth_kwargs,
                    cache_dir=self.cache_dir,
                    torch_dtype=torch.float16,
                    device_map="auto",  # Let HF decide the best device map
                    offload_folder="offload_folder"
                )
            except Exception as e2:
                print(f"Error loading with 16-bit precision: {e2}")
                print("\nFinal attempt with 8-bit quantization...")
                
                # Last resort: try 8-bit quantization which has better CPU offload support
                # Create a new BitsAndBytesConfig for 8-bit quantization
                bnb_config_8bit = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0
                )
                
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    **auth_kwargs,
                    cache_dir=self.cache_dir,
                    quantization_config=bnb_config_8bit,
                    device_map="auto",
                    torch_dtype=torch.float16
                )
        
        # Retrieve tokenizer from future
        tokenizer = tokenizer_future.result()
        
        # Ensure pad token is set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id
            
        # Update model configuration
        model.config.pad_token_id = tokenizer.pad_token_id
        model.config.eos_token_id = tokenizer.eos_token_id
        
        # Apply Flash Attention optimization for CodeLlama if available
        try:
            from transformers.utils.import_utils import is_flash_attn_available
            if is_flash_attn_available():
                print("Using Flash Attention 2 for improved performance")
                model.config._attn_implementation = "flash_attention_2"
        except:
            pass
        
        # Store loaded models
        self.loaded_models[language] = model
        self.loaded_tokenizers[language] = tokenizer
        
        # Print memory usage after loading
        self._print_memory_usage()
        
        print(f"{language} model loaded successfully.")
        return model, tokenizer

    def get_available_gpu_memory(self):
        """
        Get the available GPU memory in GB
        
        :return: A dictionary of device ID to available memory in GB, or empty dict if no GPU
        """
        available_memory = {}
        
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                total = torch.cuda.get_device_properties(i).total_memory
                reserved = torch.cuda.memory_reserved(i)
                allocated = torch.cuda.memory_allocated(i)
                available = total - reserved
                
                available_memory[i] = {
                    'total_gb': total / (1024**3),
                    'reserved_gb': reserved / (1024**3),
                    'allocated_gb': allocated / (1024**3),
                    'available_gb': available / (1024**3)
                }
        
        return available_memory
  
    def _optimize_memory(self):
        """
        Optimize memory usage with enhanced cleanup
        """
        # Force garbage collection multiple times
        for _ in range(3):
            gc.collect()
        
        # Clear PyTorch CUDA cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
            # Try to trim memory on CUDA if available (newer PyTorch versions)
            try:
                torch.cuda.memory._dump_snapshot()
                torch.cuda.memory.reset_peak_memory_stats()
                
                # On newer PyTorch versions, try to use cudart functionality
                if hasattr(torch.cuda, 'cudart'):
                    torch.cuda.cudart().cudaDeviceSynchronize()
            except:
                pass
   
    def _print_memory_usage(self):
        """
        Print current system memory usage
        """
        mem = psutil.virtual_memory()
        print(f"System Memory: {mem.used / (1024**3):.2f} GB used of {mem.total / (1024**3):.2f} GB ({mem.percent}%)")
        
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                allocated = torch.cuda.memory_allocated(i) / (1024 ** 3)
                cached = torch.cuda.memory_reserved(i) / (1024 ** 3)
                total = torch.cuda.get_device_properties(i).total_memory / (1024 ** 3)
                print(f"GPU {i} Memory: {allocated:.2f} GB allocated, {cached:.2f} GB cached of {total:.2f} GB total")
   
    def unload_model(self, language):
        """
        Unload a model to free up memory with enhanced cleanup
        """
        if language in self.loaded_models:
            print(f"Unloading {language} model...")
            
            # Store references to be deleted
            model_to_unload = self.loaded_models[language]
            tokenizer_to_unload = self.loaded_tokenizers[language]
            
            # Remove references from dictionaries
            if language in self.loaded_models:
                del self.loaded_models[language]
            if language in self.loaded_tokenizers:
                del self.loaded_tokenizers[language]
            
            # Explicitly move model to CPU first (helps with memory release)
            if hasattr(model_to_unload, 'to'):
                try:
                    model_to_unload.to('cpu')
                except:
                    pass
            
            # Delete model and tokenizer references
            del model_to_unload
            del tokenizer_to_unload
            
            # Extra aggressive memory cleanup
            self._optimize_memory()
            
            print(f"{language} model unloaded.")
            return True
        
        return False
            
    def is_model_loaded(self, language):
        """
        Check if a specific model is loaded
        """
        return language in self.loaded_models
    
    def generate_code(self, prompt, chat_history=None, language=None, temperature=0.2, max_new_tokens=1024, repetition_penalty=1.1):
        """
        Generate code with improved prompt handling
        
        :param prompt: User's current message
        :param chat_history: Optional conversation history
        :param language: Programming language
        :param temperature: Sampling temperature
        :param max_new_tokens: Maximum number of tokens to generate
        :param repetition_penalty: Penalty for repeating tokens
        :yield: Generated code responses
        """
        # Detect language if not specified
        if language is None:
            language = self.detect_language(prompt)
        
        # Lazy load model and tokenizer if not already loaded
        model, tokenizer = self.load_model(language)
        
        # Format the prompt using the new chat prompt method
        formatted_prompt = self._format_chat_prompt(prompt, chat_history, language)
        
        # Generate with optimized settings for RTX 4070 and 7800X3D
        try:
            # Process the response with PyTorch optimizations
            for partial_response in self._generate_with_pytorch(
                model, tokenizer, formatted_prompt, 
                temperature, max_new_tokens, repetition_penalty
            ):
                # Clean the model response before yielding
                cleaned_response = self._clean_model_response(partial_response)
                yield cleaned_response
                
            # If in memory-saving mode, unload the model after use
            if self.performance_mode == "memory":
                Thread(target=self.unload_model, args=(language,)).start()
                    
        except Exception as e:
            print(f"Error during generation: {e}")
            # Try with safe fallback settings
            for partial_response in self._generate_with_pytorch_safe(
                model, tokenizer, formatted_prompt, 
                temperature, max_new_tokens, repetition_penalty
            ):
                # Clean the model response before yielding
                cleaned_response = self._clean_model_response(partial_response)
                yield cleaned_response
                
    def _generate_with_pytorch(self, model, tokenizer, prompt, 
                              temperature, max_new_tokens, repetition_penalty):
        """
        Generate code with PyTorch optimized for 7800X3D and RTX 4070
        - Further optimized for CodeLlama-13B-Instruct
        """
        # Run tokenization in thread pool to leverage multiple cores
        tokenizer_future = self.tokenizer_pool.submit(
            self._parallel_tokenize,
            tokenizer,
            prompt, 
            return_tensors="pt", 
            padding=True, 
            truncation=True,
            max_length=1024
        )
        
        # Get tokenized inputs
        inputs = tokenizer_future.result()
        
        # Move inputs to the same device as the model
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generation settings optimized for CodeLlama-13B-Instruct
        with torch.no_grad(), torch.amp.autocast('cuda'):  # Use automatic mixed precision
            generated_ids = model.generate(
                input_ids=inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                repetition_penalty=repetition_penalty,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                use_cache=True,
                top_k=50,
                top_p=0.95,
                num_beam_groups=1,
                num_beams=2,  # Set `num_beams` > 1 to align with `early_stopping`
                early_stopping=False,  # Unset `early_stopping` if `num_beams` is 1
                return_dict_in_generate=False
            )
        
        # Run decode in thread pool to leverage multiple cores
        decode_future = self.tokenizer_pool.submit(
            tokenizer.decode,
            generated_ids[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )
        
        # Get decoded text
        generated_text = decode_future.result()
        
        yield generated_text
        
    def _generate_with_pytorch_safe(self, model, tokenizer, prompt, 
                                  temperature, max_new_tokens, repetition_penalty):
        """
        Generate code with PyTorch using safe settings (fallback mode)
        """
        # Simpler tokenization without threading
        inputs = tokenizer(
            prompt, 
            return_tensors="pt", 
            padding=True, 
            truncation=True,
            max_length=1024
        )
        
        # Move inputs to the same device as the model
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Use safer generation settings
        with torch.no_grad():  # Disable gradient tracking
            # Use more conservative settings
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
        
    def _format_chat_prompt(self, current_message, chat_history=None, language=None):
        """
        Format prompt with chat history for different model types
        
        :param current_message: Current user message
        :param chat_history: Optional list of previous messages
        :param language: Language for prompt template
        :return: Formatted prompt string
        """
        # Ensure language is lowercase and valid
        language = language.lower() if language else 'python'
        
        # Get model config for this language
        model_config = self.models_config.get(language, {})
        model_name = model_config.get('model_name', '').lower()
        supports_chat = model_config.get('supports_chat', False)
        
        # If no chat history or chat not supported, just use the template
        if not chat_history or len(chat_history) == 0 or not supports_chat:
            template = model_config.get('prompt_template', "{prompt}")
            return template.format(prompt=current_message)
        
        # Format for CodeLlama-Instruct (based on Llama 2 chat format)
        if "codellama" in model_name and "instruct" in model_name:
            return self._format_codellama_instruct_prompt(current_message, chat_history, language)
        # Format for Phi-2
        elif "phi" in model_name:
            return self._format_phi_prompt(current_message, chat_history, language)
        # Default format as fallback
        else:
            return self._format_standard_prompt(current_message, chat_history, language)

    def _format_codellama_instruct_prompt(self, current_message, chat_history, language):
        """Format specifically for CodeLlama Instruct models"""
        # System message for code generation
        if language == 'python':
            system_message = "You are a helpful coding assistant specialized in Python. Write clean, efficient, and well-commented Python code that solves the user's problem."
        elif language == 'powershell':
            system_message = "You are a helpful coding assistant specialized in PowerShell. Write clean, efficient, and well-commented PowerShell code that solves the user's problem."
        else:
            system_message = "You are a helpful coding assistant. Write clean, efficient, and well-commented code that solves the user's problem."
        
        # Start with the system message in the Llama 2 / CodeLlama Instruct format
        formatted_prompt = f"<s>[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n"
        
        # Add conversation history (limited to last 5 exchanges to avoid context overflow)
        history_pairs = []
        user_messages = []
        assistant_messages = []
        
        for msg in chat_history[-10:]:  # Limit to last 10 messages
            role = msg.get('role', '').lower()
            content = msg.get('content', '')
            
            if role == 'user':
                user_messages.append(content)
            elif role == 'assistant' and user_messages:
                # Pair the most recent user message with this assistant response
                history_pairs.append((user_messages.pop(), content))
            
        # Add any remaining user messages
        user_messages.extend(assistant_messages)  # Combine any unpaired messages
        
        # Format the conversation history
        for user_msg, assistant_msg in history_pairs:
            formatted_prompt += f"{user_msg} [/INST] {assistant_msg} </s><s>[INST] "
        
        # Add the current message
        formatted_prompt += f"{current_message} [/INST] "
        
        return formatted_prompt

    def _format_phi_prompt(self, current_message, chat_history, language):
        """Format specific to Microsoft Phi models"""
        # System prompt for code generation
        if language == 'python':
            system_prompt = "You are a helpful Python programming assistant. Write clean, efficient Python code."
        elif language == 'powershell':
            system_prompt = "You are a helpful PowerShell programming assistant. Write clean, efficient PowerShell code."
        else:
            system_prompt = "You are a helpful programming assistant. Write clean, efficient code."
        
        # Format the conversation history
        conversation = [f"System: {system_prompt}"]
        
        # Add previous messages
        for msg in chat_history[-5:]:  # Limit to last 5 messages to avoid context window issues
            role = msg.get('role', '').lower()
            content = msg.get('content', '')
            
            if role == 'user':
                conversation.append(f"Human: {content}")
            elif role == 'assistant':
                conversation.append(f"Assistant: {content}")
        
        # Add the current message if not already in history
        if not chat_history or chat_history[-1].get('role') != 'user':
            conversation.append(f"Human: {current_message}")
        
        # Signal for the model to respond
        conversation.append("Assistant:")
        
        return "\n".join(conversation)

    def _format_standard_prompt(self, current_message, chat_history, language):
        """Standard instruction format for many models"""
        # System prompt for code generation based on language
        if language == 'python':
            system_prompt = "You are a helpful Python programming assistant. Write clean, efficient Python code."
        elif language == 'powershell':
            system_prompt = "You are a helpful PowerShell programming assistant. Write clean, efficient PowerShell code."
        else:
            system_prompt = "You are a helpful programming assistant. Write clean, efficient code."
        
        # Format the conversation history
        conversation = [f"System: {system_prompt}"]
        
        # Add previous messages
        for msg in chat_history[-5:]:  # Limit context
            role = msg.get('role', '').lower()
            content = msg.get('content', '')
            
            if role == 'user':
                conversation.append(f"User: {content}")
            elif role == 'assistant':
                conversation.append(f"Assistant: {content}")
        
        # Add the current message if not already in history
        if not chat_history or chat_history[-1].get('role') != 'user':
            conversation.append(f"User: {current_message}")
        
        # Signal for the model to respond
        conversation.append("Assistant:")
        
        return "\n\n".join(conversation)

    def _clean_model_response(self, response_text):
        """Clean up any template tags or formatting artifacts from model responses"""
        # Remove common template tags that might appear in output
        tags_to_remove = [
            "</s>", "<s>", "[INST]", "[/INST]", "<<SYS>>", "<</SYS>>",
            "<|assistant|>", "<|user|>", "<|system|>", 
            "<|im_start|>", "<|im_end|>",
            "<|assistant_name|>", "<|assistant_description|>",
            "</s>", "<s>", "<pad>"
        ]
        
        result = response_text
        for tag in tags_to_remove:
            result = result.replace(tag, "")
        
        # Remove any lines that are just template tags
        lines = result.split("\n")
        cleaned_lines = [line for line in lines if not (
            line.strip().startswith("<|") and line.strip().endswith("|>") or
            line.strip().startswith("[") and line.strip().endswith("]")
        )]
        
        # Join the cleaned lines
        cleaned_text = "\n".join(cleaned_lines)
        
        return cleaned_text.strip()
         
    def detect_language(self, prompt):
        """
        Detect programming language from the prompt
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
        Format code with basic syntax highlighting and remove unwanted delimiters
        """
        # Process in thread pool to utilize multiple cores
        def process_code(code_text, lang):
            # Remove "Answer: " prefix
            if code_text.startswith("Answer: "):
                code_text = code_text[len("Answer: "):]
            
            # Remove LaTeX-like code delimiters
            code_text = code_text.replace("\\begin{code}", "").replace("\\end{code}", "").strip()
            
            # CodeLlama-Instruct specific: remove markdown code blocks if present
            if code_text.startswith("```") and lang.lower() in code_text[:20].lower():
                lines = code_text.split('\n')
                if lines[-1].strip() == "```":
                    code_text = '\n'.join(lines[1:-1])
            
            # Basic code formatting
            return f"```{lang}\n{code_text}\n```"
        
        # Submit to thread pool
        future = self.tokenizer_pool.submit(process_code, code, language)
        return future.result()
    
    def shutdown(self):
        """
        Clean shutdown all resources
        """
        print("Shutting down model manager...")
        
        # Unload all models
        for language in list(self.loaded_models.keys()):
            self.unload_model(language)
        
        # Shutdown thread pools
        self.tokenizer_pool.shutdown()
        self.cpu_pool.shutdown()
        
        # Final memory cleanup
        self._optimize_memory()
        
        print("Model manager shutdown complete.")