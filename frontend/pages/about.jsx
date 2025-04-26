import React from 'react';
import Head from 'next/head';
import Layout from '../components/layout/Layout';

export default function About() {
  return (
    <>
      <Head>
        <title>About - J's CodeBuddy AI</title>
        <meta name="description" content="About J's CodeBuddy AI" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Layout>
        <div className="tab-content">
          <div className="about-content">
            <h1 className="about-title">J's CodeBuddy AI</h1>
            <p className="about-tagline">Your Python & PowerShell Coding Assistant</p>
            
            <h2>Overview</h2>
            <p>
              CodeBuddy AI is a multi-language code generation assistant that 
              supports both Python and PowerShell. The application uses a modern, 
              clean interface with a dark theme for a professional appearance.
            </p>
            
            <h2>Features</h2>
            <ul className="feature-list">
              <li>
                <strong>Multi-language Support</strong> - Intelligent code generation 
                for Python and PowerShell, with automatic language detection.
              </li>
              <li>
                <strong>Adaptive Response</strong> - Control generation parameters 
                like temperature and token length to customize outputs.
              </li>
              <li>
                <strong>Syntax Highlighting</strong> - Beautiful syntax highlighting 
                for generated code with proper indentation and formatting.
              </li>
              <li>
                <strong>Feedback System</strong> - Provide positive or negative 
                feedback to help improve future responses.
              </li>
              <li>
                <strong>Training Data Management</strong> - Save and organize examples 
                for continuous improvement.
              </li>
            </ul>
            
            <h2>How It Works</h2>
            <p>
              CodeBuddy AI uses state-of-the-art language models to generate high-quality 
              code based on your requests. The system intelligently switches between 
              specialized models for Python and PowerShell to provide the most accurate 
              and efficient code solutions.
            </p>
            
            <h3>Language Models</h3>
            <p>
              Python code is generated using CodeLlama-13b-Python, while PowerShell 
              code uses Microsoft's Phi-2 model, which has strong capabilities for 
              PowerShell coding tasks.
            </p>
            
            <h2>Usage</h2>
            <ol className="usage-steps">
              <li>
                <strong>Describe your task</strong> - Enter a description of the code 
                you need in the chat input.
              </li>
              <li>
                <strong>Choose language (optional)</strong> - Select Python, PowerShell, 
                or let the system auto-detect based on your request.
              </li>
              <li>
                <strong>Adjust settings (optional)</strong> - Fine-tune temperature and 
                token length to control creativity and response size.
              </li>
              <li>
                <strong>Generate code</strong> - Click "Send" to generate your code.
              </li>
              <li>
                <strong>Provide feedback</strong> - Use the like/dislike buttons to 
                improve future results.
              </li>
            </ol>
            
            <h2>Getting Started</h2>
            <p>
              To get started, simply navigate to the Chat tab and enter your first 
              code request. The system will automatically detect whether you need 
              Python or PowerShell code and generate an appropriate response.
            </p>
            
            <h2>Customization</h2>
            <p>
              You can customize the application by adjusting the generation parameters:
            </p>
            <ul>
              <li>
                <strong>Temperature</strong> - Controls creativity (0 = deterministic, 1 = creative)
              </li>
              <li>
                <strong>Max Tokens</strong> - Limits the length of generated responses
              </li>
            </ul>
            
            <h2>Feedback</h2>
            <p>
              Your feedback helps improve the system. Use the 👍 and 👎 buttons to rate 
              responses, or click "Learn from Current Response" to save particularly 
              useful examples for training.
            </p>
          </div>
        </div>
      </Layout>
    </>
  );
}