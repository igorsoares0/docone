import os
import subprocess
import platform
from flask import current_app
from PyPDF2 import PdfReader

class DocumentConverter:
    """Service for converting documents to PDF"""

    @staticmethod
    def convert_to_pdf(input_path, output_path):
        """
        Convert DOCX/PPTX to PDF
        Returns: True if successful, False otherwise
        """
        try:
            file_ext = input_path.rsplit('.', 1)[1].lower() if '.' in input_path else ''

            # If already PDF, just copy or return input path
            if file_ext == 'pdf':
                return True

            # Determine conversion method based on platform
            system = platform.system()

            if system == 'Linux':
                # Use LibreOffice in headless mode (production)
                return DocumentConverter._convert_with_libreoffice(input_path, output_path)
            else:
                # Use docx2pdf for Windows/Mac (development)
                return DocumentConverter._convert_with_docx2pdf(input_path, output_path)

        except Exception as e:
            current_app.logger.error(f"Error converting document: {str(e)}")
            return False

    @staticmethod
    def _convert_with_libreoffice(input_path, output_path):
        """Convert using LibreOffice (Linux)"""
        try:
            output_dir = os.path.dirname(output_path)

            result = subprocess.run([
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                input_path
            ], check=True, timeout=60, capture_output=True)

            # LibreOffice creates file with same base name but .pdf extension
            input_basename = os.path.basename(input_path)
            base_name = os.path.splitext(input_basename)[0]
            generated_pdf = os.path.join(output_dir, f"{base_name}.pdf")

            # Rename to expected output path if different
            if os.path.exists(generated_pdf) and generated_pdf != output_path:
                os.rename(generated_pdf, output_path)

            return os.path.exists(output_path)

        except subprocess.TimeoutExpired:
            current_app.logger.error("LibreOffice conversion timeout")
            return False
        except subprocess.CalledProcessError as e:
            current_app.logger.error(f"LibreOffice conversion failed: {e.stderr}")
            return False
        except Exception as e:
            current_app.logger.error(f"LibreOffice conversion error: {str(e)}")
            return False

    @staticmethod
    def _convert_with_docx2pdf(input_path, output_path):
        """Convert using docx2pdf (Windows/Mac)"""
        try:
            from docx2pdf import convert
            convert(input_path, output_path)
            return os.path.exists(output_path)
        except Exception as e:
            current_app.logger.error(f"docx2pdf conversion error: {str(e)}")
            return False

    @staticmethod
    def get_pdf_page_count(pdf_path):
        """Get number of pages in PDF"""
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            current_app.logger.error(f"Error reading PDF page count: {str(e)}")
            return None

    @staticmethod
    def get_pdf_path_for_document(file_path, file_type):
        """
        Determine PDF path for a document
        If already PDF, return same path
        If DOCX/PPTX, return path with .pdf extension
        """
        if file_type == 'pdf':
            return file_path

        # Replace extension with .pdf
        base_path = os.path.splitext(file_path)[0]
        return f"{base_path}.pdf"
