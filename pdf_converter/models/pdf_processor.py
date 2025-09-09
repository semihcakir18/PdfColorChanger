"""
PDF processing module using PyMuPDF for color scheme conversion.
Handles opening, processing, and saving PDFs with new color schemes.
"""

import fitz
import os
from typing import Tuple, Optional
from .color_schemes import get_scheme

class PDFProcessor:
    def __init__(self):
        self.current_doc = None
        self.current_path = None
    
    def open_pdf(self, file_path: str) -> bool:
        """Open a PDF file for processing."""
        try:
            if self.current_doc:
                self.current_doc.close()
            
            self.current_doc = fitz.open(file_path)
            self.current_path = file_path
            return True
        except Exception as e:
            raise Exception(f"Could not open PDF: {str(e)}")
    
    def close_pdf(self):
        """Close the current PDF document."""
        if self.current_doc:
            self.current_doc.close()
            self.current_doc = None
            self.current_path = None
    
    def get_page_count(self) -> int:
        """Get the number of pages in the current PDF."""
        if not self.current_doc:
            return 0
        return len(self.current_doc)
    
    def get_preview_image(self, page_num: int = 0, dpi: int = 150) -> bytes:
        """Convert PDF page to image bytes for preview."""
        if not self.current_doc or page_num >= len(self.current_doc):
            return None
        
        try:
            page = self.current_doc[page_num]
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            return img_data
        except Exception as e:
            raise Exception(f"Could not generate preview: {str(e)}")
    
    def convert_colors(self, scheme_name: str, output_path: str) -> bool:
        """Convert PDF colors using the specified color scheme."""
        if not self.current_doc:
            raise Exception("No PDF document loaded")
        
        scheme = get_scheme(scheme_name)
        if not scheme:
            raise Exception(f"Color scheme '{scheme_name}' not found")
        
        try:
            # Open original document
            source_doc = fitz.open(self.current_path)
            
            # Create completely new document
            new_doc = fitz.open()
            
            for page_num in range(len(source_doc)):
                source_page = source_doc[page_num]
                
                # Create new page with same dimensions
                new_page = new_doc.new_page(
                    width=source_page.rect.width,
                    height=source_page.rect.height
                )
                
                # Step 1: Draw colored background
                new_page.draw_rect(
                    new_page.rect,
                    fill=scheme['background_rgb'],
                    color=None,
                    width=0
                )
                
                # Step 2: Use a more reliable text extraction method
                # Get text with better positioning information
                
                # Method 1: Try TextPage approach for better character handling
                try:
                    textpage = source_page.get_textpage()
                    text_dict = textpage.extractDICT()
                    textpage = None  # Clean up
                except:
                    # Fallback to regular text extraction
                    text_dict = source_page.get_text("dict")
                
                # Determine text color based on scheme
                if scheme_name == "Dark Mode":
                    text_color = scheme['text_rgb']  # Light text
                else:
                    text_color = (0, 0, 0)  # Black text for light backgrounds
                
                # Process each text block with better layout preservation
                for block in text_dict["blocks"]:
                    if "lines" in block:  # Text block
                        for line in block["lines"]:
                            # Process entire lines instead of individual spans to preserve layout
                            line_text_parts = []
                            line_bbox = None
                            line_fontsize = 12  # Default
                            
                            for span in line["spans"]:
                                text = span["text"]
                                if text.strip():
                                    # Smart Turkish character handling based on test results
                                    try:
                                        # Characters that work fine in PyMuPDF - keep as-is:
                                        # ç (U+00E7), ü (U+00FC), Ç (U+00C7), Ü (U+00DC), ö (U+00F6), Ö (U+00D6)
                                        
                                        # Characters that show as flying dots - replace with ASCII:
                                        problematic_chars = {
                                            '\u0131': 'i',   # ı -> i (dotless i becomes regular i)
                                            '\u0130': 'I',   # İ -> I (capital i with dot becomes regular I)
                                            '\u011F': 'g',   # ğ -> g
                                            '\u011E': 'G',   # Ğ -> G
                                            '\u015F': 's',   # ş -> s
                                            '\u015E': 'S',   # Ş -> S
                                            '\u2013': '-',   # en dash -> hyphen
                                            '\u2022': '•',   # bullet point (keep as-is, it works)
                                            '\u2019': "'",   # right single quotation mark -> apostrophe
                                        }
                                        
                                        # Apply replacements only for problematic characters
                                        for problematic_char, ascii_replacement in problematic_chars.items():
                                            text = text.replace(problematic_char, ascii_replacement)
                                            
                                    except Exception as e:
                                        pass
                                    
                                    line_text_parts.append(text)
                                    
                                    # Use first span's properties for the line
                                    if line_bbox is None:
                                        line_bbox = span["bbox"]
                                        line_fontsize = span["size"]
                            
                            # Insert the complete line as one unit for better spacing
                            if line_text_parts and line_bbox:
                                complete_line_text = "".join(line_text_parts)
                                
                                try:
                                    # Use original positioning from the first span
                                    new_page.insert_text(
                                        (line_bbox[0], line_bbox[1]),
                                        complete_line_text,
                                        fontsize=line_fontsize,
                                        color=text_color
                                    )
                                except Exception as e:
                                    # Fallback: Process spans individually if line processing fails
                                    for span in line["spans"]:
                                        text = span["text"]
                                        if text.strip():
                                            try:
                                                new_page.insert_text(
                                                    (span["bbox"][0], span["bbox"][1]),
                                                    text,
                                                    fontsize=span["size"],
                                                    color=text_color
                                                )
                                            except:
                                                continue
            
            # Save new document
            new_doc.save(output_path)
            new_doc.close()
            source_doc.close()
            return True
            
        except Exception as e:
            if 'doc_copy' in locals():
                doc_copy.close()
            raise Exception(f"Color conversion failed: {str(e)}")
    
    def is_valid_pdf(self, file_path: str) -> bool:
        """Check if file is a valid PDF."""
        try:
            test_doc = fitz.open(file_path)
            test_doc.close()
            return True
        except:
            return False