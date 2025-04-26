/**
 * Language detector utility for CodeBuddy AI
 * Helps detect programming language from input text
 */

/**
 * Detects programming language from prompt
 * @param {string} prompt - Input text to analyze
 * @returns {string} - Detected language ('python' or 'powershell')
 */
export const detectLanguage = (prompt) => {
    if (!prompt) return 'python'; // Default to Python if prompt is empty
    
    const promptLower = prompt.toLowerCase();
    
    // PowerShell detection keywords
    const powershellKeywords = [
      // PowerShell cmdlet naming patterns
      'get-', 'set-', 'new-', 'remove-', 'add-', 'install-', 'invoke-', 'import-',
      'export-', 'start-', 'stop-', 'restart-', 'out-', 'update-', 'convert-', 'test-',
      
      // PowerShell specific technologies
      'windows', 'azure', 'active directory', 'ad ', 'exchange', 'registry',
      'powershell', 'cmdlet', 'winrm', 'pssession', '.ps1', 'wmi', 'cim',
      
      // PowerShell specific syntax
      '$_', '${', '$env:', '@(', '$profile', '$home', '$psscriptroot',
      '-contains', '-eq', '-ne', '-gt', '-lt', '-match', 'foreach-object',
      'where-object', 'select-object'
    ];
    
    // Python detection keywords
    const pythonKeywords = [
      // Python syntax
      'def ', 'import ', 'from ', 'class ', 'if __name__ == "__main__"',
      'with open', 'with as', 'print(', 'for in', 'while', 'try:', 'except:',
      'raise ', 'return ', 'yield ', 'async def', 'await ',
      
      // Python libraries
      'pandas', 'numpy', 'matplotlib', 'sklearn', 'tensorflow', 'pytorch',
      'flask', 'django', 'fastapi', 'requests', 'os.path', 'pathlib', 'pip install'
    ];
    
    // Count matches for each language
    let powershellMatches = 0;
    let pythonMatches = 0;
    
    // Check for PowerShell keywords
    for (const keyword of powershellKeywords) {
      if (promptLower.includes(keyword)) {
        powershellMatches++;
      }
    }
    
    // Check for Python keywords
    for (const keyword of pythonKeywords) {
      if (promptLower.includes(keyword)) {
        pythonMatches++;
      }
    }
    
    // Determine language based on keyword matches
    if (powershellMatches > pythonMatches) {
      return 'powershell';
    }
    
    // Default to Python
    return 'python';
  };
  
  /**
   * Gets display name for a language
   * @param {string} language - Language code ('python', 'powershell', 'auto')
   * @returns {string} - Display name for the language
   */
  export const getLanguageDisplay = (language) => {
    const displayMap = {
      'python': 'Python',
      'powershell': 'PowerShell',
      'auto': 'Auto Detect'
    };
    
    return displayMap[language] || 'Unknown';
  };
  
  /**
   * Gets file extension for a language
   * @param {string} language - Language code
   * @returns {string} - File extension (.py, .ps1, etc.)
   */
  export const getLanguageExtension = (language) => {
    const extensionMap = {
      'python': '.py',
      'powershell': '.ps1',
      'javascript': '.js',
      'typescript': '.ts',
      'html': '.html',
      'css': '.css',
      'bash': '.sh'
    };
    
    return extensionMap[language] || '.txt';
  };
  
  /**
   * Gets prism language class for syntax highlighting
   * @param {string} language - Language code or name
   * @returns {string} - Prism language class
   */
  export const getPrismLanguage = (language) => {
    if (!language) return 'language-markup';
    
    const langMap = {
      'py': 'python',
      'python': 'python',
      'ps1': 'powershell',
      'powershell': 'powershell',
      'js': 'javascript',
      'javascript': 'javascript',
      'ts': 'typescript',
      'typescript': 'typescript',
      'html': 'markup',
      'xml': 'markup',
      'css': 'css',
      'sh': 'bash',
      'bash': 'bash',
      'sql': 'sql'
    };
    
    const normalized = language.toLowerCase();
    return `language-${langMap[normalized] || 'markup'}`;
  };
  
  export default {
    detectLanguage,
    getLanguageDisplay,
    getLanguageExtension,
    getPrismLanguage
  };