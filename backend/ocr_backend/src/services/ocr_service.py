import os
import tempfile
from typing import Union, Tuple
import pytesseract
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path
import io

class OCRService:
    """
    Service class for extracting text from images and PDF files using OCR.
    Supports both regular text-based PDFs and scanned PDFs.
    """
    
    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """
        Detect if the file is an image or PDF based on file extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: 'image' or 'pdf'
            
        Raises:
            ValueError: If file type is not supported
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            return 'image'
        elif file_extension == '.pdf':
            return 'pdf'
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """
        Extract text from an image file using Tesseract OCR.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text
            
        Raises:
            Exception: If OCR processing fails
        """
        try:
            # Open and process the image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, lang='eng')
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text from a PDF file. Handles both text-based and scanned PDFs.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text
            
        Raises:
            Exception: If PDF processing fails
        """
        try:
            extracted_text = ""
            
            # First, try to extract text directly from PDF (for text-based PDFs)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    # If we get meaningful text, add it
                    if page_text and page_text.strip():
                        extracted_text += page_text + "\n"
            
            # If we got substantial text from direct extraction, return it
            if len(extracted_text.strip()) > 50:  # Threshold for meaningful text
                return extracted_text.strip()
            
            # If direct extraction didn't work well, use OCR on PDF pages
            return OCRService._extract_text_from_pdf_with_ocr(pdf_path)
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def _extract_text_from_pdf_with_ocr(pdf_path: str) -> str:
        """
        Extract text from PDF using OCR (for scanned PDFs).
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text
        """
        try:
            # Convert PDF pages to images
            pages = convert_from_path(pdf_path, dpi=300)
            
            extracted_text = ""
            
            for page_num, page_image in enumerate(pages):
                # Save page as temporary image
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    page_image.save(temp_file.name, 'PNG')
                    
                    # Extract text from the page image
                    page_text = OCRService.extract_text_from_image(temp_file.name)
                    extracted_text += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
                    
                    # Clean up temporary file
                    os.unlink(temp_file.name)
            
            return extracted_text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF using OCR: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, str]:
        """
        Main method to extract text from either an image or PDF file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Tuple[str, str]: (extracted_text, file_type)
            
        Raises:
            Exception: If file processing fails
        """
        try:
            # Detect file type
            file_type = OCRService.detect_file_type(file_path)
            
            # Extract text based on file type
            if file_type == 'image':
                text = OCRService.extract_text_from_image(file_path)
            elif file_type == 'pdf':
                text = OCRService.extract_text_from_pdf(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            return text, file_type
            
        except Exception as e:
            raise Exception(f"Failed to extract text: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Test the OCR service
    ocr = OCRService()
    
    # Example usage
    try:
        # Replace with actual file paths for testing
        # text, file_type = ocr.extract_text("/path/to/your/file.pdf")
        # print(f"File type: {file_type}")
        # print(f"Extracted text: {text}")
        pass
    except Exception as e:
        print(f"Error: {e}")
