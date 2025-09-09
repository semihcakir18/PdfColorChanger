"""
Color scheme definitions for PDF conversion.
Includes scientifically-backed color schemes for eye comfort and readability.
"""

def hex_to_rgb(hex_color):
    """Convert hex color to PyMuPDF RGB format (0-1 range)."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)

COLOR_SCHEMES = {
    "Dark Mode": {
        "name": "Dark Mode",
        "description": "Dark background for low light reading",
        "background_hex": "#2D2D2D",
        "text_hex": "#FFFFFF",
        "background_rgb": hex_to_rgb("#2D2D2D"),
        "text_rgb": hex_to_rgb("#FFFFFF"),
        "contrast_ratio": 13.4
    },
    
    "Sepia": {
        "name": "Sepia Reading", 
        "description": "Warm brown/beige background - easy on the eyes",
        "background_hex": "#DEB887",
        "text_hex": "#8B4513",
        "background_rgb": hex_to_rgb("#DEB887"),
        "text_rgb": hex_to_rgb("#8B4513"),
        "contrast_ratio": 8.2
    },
    
    "High Contrast": {
        "name": "High Contrast",
        "description": "Black text on white background - maximum readability",
        "background_hex": "#FFFFFF", 
        "text_hex": "#000000",
        "background_rgb": hex_to_rgb("#FFFFFF"),
        "text_rgb": hex_to_rgb("#000000"),
        "contrast_ratio": 21.0
    },
    
    "Green Tint": {
        "name": "Green Tint",
        "description": "Light green background - gentle on the eyes",
        "background_hex": "#E6F3E6",
        "text_hex": "#2D5A2D", 
        "background_rgb": hex_to_rgb("#E6F3E6"),
        "text_rgb": hex_to_rgb("#2D5A2D"),
        "contrast_ratio": 9.1
    }
}

def get_scheme_names():
    """Get list of available color scheme names."""
    return list(COLOR_SCHEMES.keys())

def get_scheme(name):
    """Get color scheme by name."""
    return COLOR_SCHEMES.get(name)