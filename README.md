# J's CodeBuddy AI 🤖

## Overview
J's CodeBuddy AI is an advanced, multi-language programming assistant focused on Python and PowerShell code generation. Powered by CodeLlama-13B-Instruct, this application provides intelligent code generation, training data management, and AI comparison features.

## 🌟 Features
- **Multi-Language Support**: 
  - Python code generation
  - PowerShell script creation
  - Automatic language detection

- **AI-Powered Code Generation**:
  - Contextual understanding
  - Code block generation
  - Explanation of generated code

- **Training Data Management**:
  - Save and organize training examples
  - Compare responses from different AI systems
  - Filter and review training data

- **Customizable Settings**:
  - Temperature control for creativity
  - Maximum token length
  - Language-specific prompts

## 🚀 Installation

### Prerequisites
- Python 3.8+
- CUDA-capable GPU recommended
- Hugging Face account

### Setup Steps
1. Clone the repository:
```bash
git clone https://github.com/JoshuaFourie/Codelama-Python.git
cd codebuddy-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Hugging Face Token:
- Go to [Hugging Face Tokens](https://huggingface.co/settings/tokens)
- Create a new token with read access
- Either set an environment variable:
  ```bash
  export HUGGING_FACE_HUB_TOKEN='your_token_here'
  ```
  Or input the token when prompted during application startup

### Running the Application
```bash
python launcher.py
```

## 🛠 Configuration
- Modify `theme.py` to customize app branding
- Adjust model configurations in `model_manager.py`

## 📊 System Requirements
- **Recommended**:
  - GPU with 16GB+ VRAM
  - 32GB RAM
  - AMD Ryzen 7800X3D or equivalent
- **Minimum**:
  - 16GB RAM
  - CUDA-capable GPU
  - Python 3.8+

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments
- [Hugging Face](https://huggingface.co/)
- [CodeLlama](https://ai.meta.com/research/publications/code-llama-open-foundation-models-for-code/)
- [Gradio](https://www.gradio.app/)

