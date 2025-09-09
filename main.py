#!/usr/bin/env python3
"""
PDF Color Scheme Converter - Main Entry Point

A GUI application for converting PDF color schemes using PyMuPDF and PySide6.
Supports multiple predefined color schemes optimized for eye comfort and readability.
"""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from pdf_converter.views.main_window import main

if __name__ == "__main__":
    main()