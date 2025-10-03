import os
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.services.ocr_service import OCRService

ocr_bp = Blueprint('ocr', __name__)

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Check if the uploaded file size is within limits."""
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    return file_size <= MAX_FILE_SIZE

@ocr_bp.route('/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from uploaded image or PDF file.
    
    Returns:
        JSON response with extracted text or error message
    """
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not allowed. Supported types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Validate file size
        if not validate_file_size(file):
            return jsonify({
                'success': False,
                'error': f'File size too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Create temporary file to save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Extract text using OCR service
            extracted_text, file_type = OCRService.extract_text(temp_file_path)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Return success response
            return jsonify({
                'success': True,
                'text': extracted_text,
                'file_type': file_type,
                'filename': secure_filename(file.filename)
            }), 200
            
        except Exception as ocr_error:
            # Clean up temporary file in case of error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            return jsonify({
                'success': False,
                'error': f'OCR processing failed: {str(ocr_error)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@ocr_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the OCR service."""
    return jsonify({
        'success': True,
        'message': 'OCR service is running',
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE // (1024*1024)
    }), 200

@ocr_bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get list of supported file formats."""
    return jsonify({
        'success': True,
        'formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE // (1024*1024)
    }), 200
