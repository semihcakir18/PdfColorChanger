"""
Main GUI window for the PDF Color Converter application.
Provides file selection, color scheme selection, preview, and conversion functionality.
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QComboBox, 
                              QFileDialog, QMessageBox, QScrollArea, QProgressBar,
                              QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QFont

from ..models.pdf_processor import PDFProcessor
from ..models.color_schemes import get_scheme_names, get_scheme

class ConversionWorker(QThread):
    """Worker thread for PDF conversion to keep UI responsive."""
    progress_updated = Signal(str)
    conversion_finished = Signal(bool, str)
    
    def __init__(self, processor, scheme_name, output_path):
        super().__init__()
        self.processor = processor
        self.scheme_name = scheme_name
        self.output_path = output_path
    
    def run(self):
        try:
            self.progress_updated.emit("Converting PDF colors...")
            success = self.processor.convert_colors(self.scheme_name, self.output_path)
            if success:
                self.conversion_finished.emit(True, "Conversion completed successfully!")
            else:
                self.conversion_finished.emit(False, "Conversion failed")
        except Exception as e:
            self.conversion_finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = PDFProcessor()
        self.current_file = None
        self.conversion_worker = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Color Scheme Converter")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("PDF Color Scheme Converter")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # File selection group
        file_group = QGroupBox("1. Select PDF File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; border: 1px solid gray; background-color: #f0f0f0;")
        file_layout.addWidget(self.file_label)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button)
        
        main_layout.addWidget(file_group)
        
        # Color scheme selection group
        scheme_group = QGroupBox("2. Choose Color Scheme")
        scheme_layout = QVBoxLayout(scheme_group)
        
        self.scheme_combo = QComboBox()
        self.scheme_combo.addItems(get_scheme_names())
        self.scheme_combo.currentTextChanged.connect(self.update_scheme_info)
        scheme_layout.addWidget(self.scheme_combo)
        
        self.scheme_info = QLabel()
        self.scheme_info.setWordWrap(True)
        self.scheme_info.setStyleSheet("padding: 5px; background-color: #f9f9f9; border: 1px solid #ccc; color: #333333;")
        scheme_layout.addWidget(self.scheme_info)
        
        main_layout.addWidget(scheme_group)
        
        # Preview group
        preview_group = QGroupBox("3. Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(200)
        self.preview_label = QLabel("Select a PDF file to see preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("color: gray; font-style: italic;")
        self.preview_scroll.setWidget(self.preview_label)
        preview_layout.addWidget(self.preview_scroll)
        
        main_layout.addWidget(preview_group)
        
        # Convert button and progress
        convert_layout = QVBoxLayout()
        
        self.convert_button = QPushButton("Convert PDF")
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.convert_pdf)
        self.convert_button.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }")
        convert_layout.addWidget(self.convert_button)
        
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        convert_layout.addWidget(self.progress_label)
        
        main_layout.addLayout(convert_layout)
        
        # Initialize scheme info
        self.update_scheme_info()
    
    def browse_file(self):
        """Open file dialog to select PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select PDF File", 
            "", 
            "PDF files (*.pdf)"
        )
        
        if file_path:
            try:
                if self.processor.is_valid_pdf(file_path):
                    self.processor.open_pdf(file_path)
                    self.current_file = file_path
                    self.file_label.setText(os.path.basename(file_path))
                    self.convert_button.setEnabled(True)
                    self.update_preview()
                else:
                    QMessageBox.warning(self, "Invalid File", "Please select a valid PDF file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open PDF: {str(e)}")
    
    def update_scheme_info(self):
        """Update color scheme information display."""
        scheme_name = self.scheme_combo.currentText()
        scheme = get_scheme(scheme_name)
        
        if scheme:
            info_text = f"<b>{scheme['name']}</b><br>"
            info_text += f"{scheme['description']}<br>"
            info_text += f"Background: {scheme['background_hex']} | Text: {scheme['text_hex']}<br>"
            info_text += f"Contrast Ratio: {scheme['contrast_ratio']}:1"
            self.scheme_info.setText(info_text)
    
    def update_preview(self):
        """Update the preview image."""
        if not self.processor.current_doc:
            return
        
        try:
            img_data = self.processor.get_preview_image()
            if img_data:
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                
                # Scale image to fit preview area while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(400, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_label.setText("")
            else:
                self.preview_label.setText("Could not generate preview")
        except Exception as e:
            self.preview_label.setText(f"Preview error: {str(e)}")
    
    def convert_pdf(self):
        """Start PDF conversion process."""
        if not self.current_file:
            QMessageBox.warning(self, "No File", "Please select a PDF file first.")
            return
        
        # Get output file path
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Converted PDF",
            os.path.splitext(self.current_file)[0] + "_converted.pdf",
            "PDF files (*.pdf)"
        )
        
        if not output_path:
            return
        
        # Disable UI during conversion
        self.convert_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.scheme_combo.setEnabled(False)
        
        # Start conversion in worker thread
        scheme_name = self.scheme_combo.currentText()
        self.conversion_worker = ConversionWorker(self.processor, scheme_name, output_path)
        self.conversion_worker.progress_updated.connect(self.update_progress)
        self.conversion_worker.conversion_finished.connect(self.conversion_complete)
        self.conversion_worker.start()
    
    def update_progress(self, message):
        """Update progress message."""
        self.progress_label.setText(message)
    
    def conversion_complete(self, success, message):
        """Handle conversion completion."""
        # Re-enable UI
        self.convert_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.scheme_combo.setEnabled(True)
        
        self.progress_label.setText("")
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", f"Conversion failed: {message}")
        
        # Clean up worker thread
        if self.conversion_worker:
            self.conversion_worker.wait()
            self.conversion_worker = None
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self.processor:
            self.processor.close_pdf()
        if self.conversion_worker and self.conversion_worker.isRunning():
            self.conversion_worker.terminate()
            self.conversion_worker.wait()
        event.accept()

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Application Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()