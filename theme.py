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
    
def get_logo_with_dimensions(logo_path, max_height=50):
    """
    Returns the logo path with proper dimension constraints
    to prevent stretching in the UI
    """
    if not os.path.exists(logo_path):
        print(f"Warning: Logo file not found: {logo_path}")
        return None
    
    try:
        from PIL import Image
        # Check dimensions of the logo
        img = Image.open(logo_path)
        width, height = img.size
        
        # Calculate aspect ratio to maintain proportions
        aspect_ratio = width / height
        new_height = min(max_height, height)
        new_width = int(new_height * aspect_ratio)
        
        print(f"Logo dimensions: Original {width}x{height}, Displayed as {new_width}x{new_height}")
        
        return {
            "path": logo_path,
            "width": new_width,
            "height": new_height
        }
    except Exception as e:
        print(f"Could not process logo image: {e}")
        return {"path": logo_path, "width": None, "height": max_height}
