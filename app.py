from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import uuid
import logging
import sys
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
from llm_provider import get_llm_provider
from presentation_engine import PresentationEngine
from document_processor import DocumentProcessor
import tempfile
import subprocess
import shutil
import atexit
import threading
import time
from slide_exporter import export_slides_as_images

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMP_FOLDER'] = 'temp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pptx', 'docx', 'txt'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Session storage (in production, use Redis or similar)
sessions = {}

# Global lock for LibreOffice processes to prevent race conditions
libreoffice_lock = threading.Lock()

def kill_soffice_processes():
    """Kill LibreOffice processes in a cross-platform way."""
    try:
        if sys.platform == 'win32':
            # Windows: use taskkill
            subprocess.run(['taskkill', '/IM', 'soffice.exe', '/F'], capture_output=True, timeout=5)
            subprocess.run(['taskkill', '/IM', 'soffice.bin', '/F'], capture_output=True, timeout=5)
        else:
            # Linux/macOS: use pkill
            subprocess.run(['pkill', '-f', 'soffice'], capture_output=True, timeout=5)
        time.sleep(1)  # Give processes time to die
    except:
        pass  # Ignore errors in cleanup

def allowed_file(filename, extensions):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(Exception)
def handle_exception(error):
    """Global error handler."""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/')
def index():
    # Simplified for DeepSeek-only application
    return render_template('index.html')

@app.route('/text-helper')
def text_helper():
    return render_template('text_helper.html')

@app.route('/api/upload/presentation', methods=['POST'])
def upload_presentation():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename, {'pptx'}):
            return jsonify({'error': 'Invalid file type. Only .pptx files are allowed.'}), 400
        
        session_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        # Parse presentation
        engine = PresentationEngine()
        structure = engine.parse_presentation(filepath)
        
        sessions[session_id] = {
            'filepath': filepath,
            'structure': structure,
            'filename': filename
        }
        
        logger.info(f"Presentation uploaded: {filename} (session: {session_id})")
        
        return jsonify({
            'session_id': session_id,
            'structure': structure
        })
        
    except Exception as e:
        logger.error(f"Error uploading presentation: {str(e)}")
        return jsonify({'error': f'Failed to process presentation: {str(e)}'}), 500

@app.route('/api/upload/document', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and (file.filename.endswith('.docx') or file.filename.endswith('.txt')):
        session_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        # Process document
        processor = DocumentProcessor()
        text_content = processor.extract_text(filepath)
        
        # Generate presentation plan using LLM
        llm = get_llm_provider()
        plan = processor.generate_presentation_plan(text_content, llm)
        
        sessions[session_id] = {
            'document_filepath': filepath,
            'text_content': text_content,
            'plan': plan,
            'filename': filename
        }
        
        return jsonify({
            'session_id': session_id,
            'plan': plan
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/presentation/<session_id>/structure', methods=['GET'])
def get_structure(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(sessions[session_id].get('structure', {}))

@app.route('/api/presentation/<session_id>/slide/<int:slide_index>/preview.png', methods=['GET'])
def get_slide_preview(session_id, slide_index):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    filepath = sessions[session_id]['filepath']
    
    # Check if we have cached previews for this session
    cache_key = f"{session_id}_previews"
    if cache_key not in sessions or not os.path.exists(sessions.get(cache_key, '')):
        # Generate all slide previews
        preview_dir = generate_all_slide_previews(session_id, filepath)
        if preview_dir:
            sessions[cache_key] = preview_dir
        else:
            return generate_placeholder_image(slide_index)
    
    # Get the cached preview directory
    preview_dir = sessions[cache_key]
    
    # Use our consistent naming scheme
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    expected_filename = f"{base_name}_slide_{slide_index + 1}.png"  # slide_index is 0-based, but we name files 1-based
    png_path = os.path.join(preview_dir, expected_filename)
    
    if os.path.exists(png_path):
        logger.info(f"Found slide {slide_index + 1} preview: {expected_filename}")
        return send_file(png_path, mimetype='image/png')
    
    # Fallback: list all available PNG files and log them for debugging
    try:
        png_files = sorted([f for f in os.listdir(preview_dir) if f.endswith('.png')])
        logger.warning(f"Expected file {expected_filename} not found. Available PNG files: {png_files}")
        
        # If we have PNG files but the expected one isn't there, try to map by index
        if png_files and slide_index < len(png_files):
            fallback_path = os.path.join(preview_dir, png_files[slide_index])
            logger.info(f"Using fallback PNG file for slide {slide_index + 1}: {png_files[slide_index]}")
            return send_file(fallback_path, mimetype='image/png')
    except Exception as e:
        logger.error(f"Error accessing preview directory: {e}")
    
    logger.warning(f"No preview found for slide {slide_index + 1}, generating placeholder")
    return generate_placeholder_image(slide_index)

def generate_all_slide_previews(session_id, filepath):
    """Generate PNG previews for all slides in the presentation."""
    # Use global lock to prevent concurrent LibreOffice processes
    with libreoffice_lock:
        temp_dir = None
        try:
            # Create unique temporary directory for this session
            temp_dir = tempfile.mkdtemp(prefix=f"aippteditor_{session_id}_")
            logger.info(f"Created temp directory: {temp_dir}")
            
            # Check if LibreOffice is available
            check_cmd = ['soffice', '--version']
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.warning(f"LibreOffice not available: {result.stderr}")
                return None
            else:
                logger.info(f"LibreOffice found: {result.stdout.strip()}")
            
            # Get slide count from structure
            structure = sessions.get(session_id, {}).get('structure', {})
            total_slides = len(structure.get('slides', []))
            
            if total_slides == 0:
                logger.warning("No slides found in structure")
                return None
            
            logger.info(f"Converting presentation with {total_slides} slides to PNG")
            
            # Kill any existing LibreOffice processes to prevent conflicts
            kill_soffice_processes()
            
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            
            # First, try to convert the entire presentation to PDF
            # PDF conversion is more reliable and then we can convert PDF pages to PNG
            pdf_path = os.path.join(temp_dir, f"{base_name}.pdf")
            
            pdf_cmd = [
                'soffice',
                '--headless',
                '--invisible',
                '--nologo',
                '--nolockcheck',
                '--convert-to',
                'pdf',
                '--outdir',
                temp_dir,
                filepath
            ]
            
            logger.info(f"Converting to PDF first: {' '.join(pdf_cmd)}")
            result = subprocess.run(pdf_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.warning(f"PDF conversion failed with return code {result.returncode}")
                logger.warning(f"STDOUT: {result.stdout}")
                logger.warning(f"STDERR: {result.stderr}")
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                logger.info("PDF conversion successful, now converting to PNG")
                
                # Now convert PDF to PNG using ImageMagick or similar if available
                # First try with convert command (ImageMagick)
                try:
                    # ImageMagick uses %d for numbering, starting from 0
                    # We'll use a pattern that doesn't conflict with our final naming
                    convert_cmd = [
                        'convert',
                        '-density', '150',
                        pdf_path,
                        os.path.join(temp_dir, f"page_%d.png")
                    ]
                    result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        logger.info("ImageMagick conversion successful")
                    else:
                        raise Exception("ImageMagick conversion failed")
                        
                except Exception as e:
                    logger.warning(f"ImageMagick not available or failed: {e}")
                    
                    # Fallback: Try direct PNG conversion with LibreOffice
                    logger.info("Falling back to direct PNG conversion")
                    png_cmd = [
                        'soffice',
                        '--headless',
                        '--invisible',
                        '--nologo',
                        '--nolockcheck',
                        '--convert-to',
                        'png',
                        '--outdir',
                        temp_dir,
                        filepath
                    ]
                    
                    result = subprocess.run(png_cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        logger.error(f"PNG conversion failed: {result.stderr}")
                        return None
            else:
                # Direct PNG conversion if PDF failed
                logger.info("PDF conversion failed, trying direct PNG conversion")
                png_cmd = [
                    'soffice',
                    '--headless',
                    '--invisible',
                    '--nologo',
                    '--nolockcheck',
                    '--convert-to',
                    'png',
                    '--outdir',
                    temp_dir,
                    filepath
                ]
                
                result = subprocess.run(png_cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    logger.error(f"PNG conversion failed with return code {result.returncode}")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                    return None
            
            # Wait longer for files to be written and LibreOffice to finish
            time.sleep(3)
            
            # Verify the source file exists and has reasonable size
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Source presentation file: {file_size} bytes")
                if file_size < 1000:  # Very small file might indicate corruption
                    logger.warning(f"Source file seems unusually small: {file_size} bytes")
            else:
                logger.error(f"Source presentation file not found: {filepath}")
                return None
            
            # List all generated files
            png_files = [f for f in os.listdir(temp_dir) if f.endswith('.png')]
            logger.info(f"Generated PNG files: {png_files}")
            
            if not png_files:
                logger.warning("No PNG files were generated by LibreOffice, trying fallback method")
                # Use our fallback export method
                exported_files = export_slides_as_images(filepath, temp_dir, base_name)
                if exported_files:
                    logger.info(f"Fallback method generated {len(exported_files)} files")
                    return temp_dir
                else:
                    logger.error("Fallback method also failed")
                    return None
            
            # Sort files naturally to handle numeric suffixes correctly
            import re
            def natural_sort_key(s):
                return [int(text) if text.isdigit() else text.lower() 
                        for text in re.split('([0-9]+)', s)]
            
            png_files.sort(key=natural_sort_key)
            logger.info(f"Sorted PNG files: {png_files}")
            
            # Rename files to our consistent naming scheme
            generated_files = []
            
            # Handle different naming patterns
            if len(png_files) == 1 and total_slides > 1:
                # LibreOffice might have generated only one file for multi-slide presentation
                logger.warning("Only one PNG generated for multi-slide presentation")
                # Still rename it for slide 1
                old_path = os.path.join(temp_dir, png_files[0])
                new_filename = f"{base_name}_slide_1.png"
                new_path = os.path.join(temp_dir, new_filename)
                try:
                    os.rename(old_path, new_path)
                    generated_files.append(new_filename)
                except Exception as e:
                    logger.error(f"Failed to rename {png_files[0]}: {e}")
            else:
                # Multiple files generated - need to rename carefully to avoid overwrites
                # First, rename all files to temporary names to avoid conflicts
                temp_renames = []
                for i, png_file in enumerate(png_files):
                    old_path = os.path.join(temp_dir, png_file)
                    temp_name = f"temp_{i}_{png_file}"
                    temp_path = os.path.join(temp_dir, temp_name)
                    try:
                        os.rename(old_path, temp_path)
                        temp_renames.append((temp_path, i))
                        logger.info(f"Temporarily renamed {png_file} -> {temp_name}")
                    except Exception as e:
                        logger.error(f"Failed to temporarily rename {png_file}: {e}")
                
                # Now rename from temporary names to final names
                for temp_path, i in temp_renames:
                    slide_num = i + 1  # 1-based slide numbering
                    new_filename = f"{base_name}_slide_{slide_num}.png"
                    new_path = os.path.join(temp_dir, new_filename)
                    
                    try:
                        os.rename(temp_path, new_path)
                        generated_files.append(new_filename)
                        logger.info(f"Renamed to final name: {new_filename}")
                    except Exception as e:
                        logger.error(f"Failed to rename to final name {new_filename}: {e}")
            
            logger.info(f"Successfully generated {len(generated_files)} slide previews: {generated_files}")
            
            # If we have fewer files than expected, generate placeholders for missing slides
            if len(generated_files) < total_slides:
                logger.warning(f"Only {len(generated_files)} of {total_slides} slides were converted")
                
                # Try to use the fallback method to generate missing slides
                logger.info("Attempting to generate missing slides using fallback method")
                missing_count = total_slides - len(generated_files)
                
                # Generate placeholder images for missing slides
                for slide_num in range(len(generated_files) + 1, total_slides + 1):
                    placeholder_filename = f"{base_name}_slide_{slide_num}.png"
                    placeholder_path = os.path.join(temp_dir, placeholder_filename)
                    
                    # Create a simple placeholder
                    try:
                        from PIL import Image, ImageDraw, ImageFont
                        img = Image.new('RGB', (1024, 768), color='#f0f0f0')
                        draw = ImageDraw.Draw(img)
                        
                        text = f"Slide {slide_num}\n(Preview generation failed)"
                        try:
                            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
                        except:
                            font = ImageFont.load_default()
                        
                        # Center the text
                        draw.text((512, 384), text, fill='gray', font=font, anchor='mm')
                        img.save(placeholder_path, 'PNG')
                        
                        logger.info(f"Created placeholder for slide {slide_num}")
                    except Exception as e:
                        logger.error(f"Failed to create placeholder for slide {slide_num}: {e}")
            
            # Always return the directory even with partial results
            return temp_dir
                
        except subprocess.TimeoutExpired:
            logger.error("Conversion timed out")
            return None
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return None
        finally:
            # Clean up any remaining LibreOffice processes
            kill_soffice_processes()

def generate_placeholder_image(slide_index):
    """Generate a simple placeholder image when preview generation fails."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        logger.info(f"Generating placeholder image for slide {slide_index}")
        
        # Create a simple placeholder image
        img = Image.new('RGB', (800, 600), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"Slide {slide_index + 1}\n(Preview unavailable)"
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
            except:
                font = ImageFont.load_default()
        
        # Center the text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        
        draw.text((x, y), text, fill='#666666', font=font)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        logger.info(f"Successfully generated placeholder image for slide {slide_index}")
        return send_file(img_bytes, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Failed to generate placeholder image: {e}")
        # Return a simple text response as fallback
        from flask import Response
        return Response("Preview unavailable", mimetype='text/plain', status=500)

@app.route('/api/presentation/<session_id>/plan', methods=['POST'])
def execute_plan(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    plan = sessions[session_id].get('plan')
    if not plan:
        return jsonify({'error': 'No plan found'}), 400
    
    # Create presentation from plan
    engine = PresentationEngine()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_generated.pptx")
    
    engine.create_presentation_from_plan(plan, filepath)
    
    # Parse the new presentation
    structure = engine.parse_presentation(filepath)
    
    sessions[session_id]['filepath'] = filepath
    sessions[session_id]['structure'] = structure
    
    # Invalidate preview cache since a new presentation was created
    cache_key = f"{session_id}_previews"
    if cache_key in sessions:
        old_preview_dir = sessions[cache_key]
        # Clean up old preview directory
        if os.path.exists(old_preview_dir):
            try:
                shutil.rmtree(old_preview_dir)
                logger.info(f"Cleaned up old preview directory after plan execution: {old_preview_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup old preview directory after plan execution: {e}")
        # Remove from cache
        del sessions[cache_key]
        logger.info(f"Invalidated preview cache after plan execution for session: {session_id}")
    
    return jsonify({
        'success': True,
        'structure': structure
    })

@app.route('/api/presentation/<session_id>/edit', methods=['POST'])
def edit_presentation(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.json
    shape_id = data.get('shape_id')
    command = data.get('command')
    context_mode = data.get('context_mode', 'local')
    
    if not shape_id or not command:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    filepath = sessions[session_id]['filepath']
    structure = sessions[session_id]['structure']
    
    # DeepSeek is the only provider
    llm = get_llm_provider()
    
    # Perform edit
    engine = PresentationEngine()
    success, updated_structure = engine.edit_shape(
        filepath, 
        shape_id, 
        command, 
        context_mode, 
        structure,
        llm
    )
    
    if success:
        sessions[session_id]['structure'] = updated_structure
        
        # Invalidate preview cache since the presentation has changed
        cache_key = f"{session_id}_previews"
        if cache_key in sessions:
            old_preview_dir = sessions[cache_key]
            # Clean up old preview directory
            if os.path.exists(old_preview_dir):
                try:
                    shutil.rmtree(old_preview_dir)
                    logger.info(f"Cleaned up old preview directory after edit: {old_preview_dir}")
                except Exception as e:
                    logger.error(f"Failed to cleanup old preview directory after edit: {e}")
            # Remove from cache
            del sessions[cache_key]
            logger.info(f"Invalidated preview cache after edit for session: {session_id}")
        
        return jsonify({
            'success': True,
            'structure': updated_structure
        })
    
    return jsonify({'error': 'Edit failed'}), 500

@app.route('/api/presentation/<session_id>/download', methods=['GET'])
def download_presentation(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    filepath = sessions[session_id]['filepath']
    filename = sessions[session_id]['filename']
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/api/presentation/<session_id>/export/pdf', methods=['GET'])
def export_presentation_as_pdf(session_id):
    """Export presentation as PDF using LibreOffice."""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    filepath = sessions[session_id]['filepath']
    filename = sessions[session_id]['filename']
    
    # Use global lock to prevent concurrent LibreOffice processes
    with libreoffice_lock:
        temp_dir = None
        try:
            # Create unique temporary directory for PDF export
            temp_dir = tempfile.mkdtemp(prefix=f"pdf_export_{session_id}_")
            logger.info(f"Created temp directory for PDF export: {temp_dir}")
            
            # Check if LibreOffice is available
            check_cmd = ['soffice', '--version']
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.warning(f"LibreOffice not available for PDF export: {result.stderr}")
                return jsonify({'error': 'PDF export not available - LibreOffice not found'}), 500
            
            logger.info(f"LibreOffice found for PDF export: {result.stdout.strip()}")
            
            # Kill any existing LibreOffice processes to prevent conflicts
            kill_soffice_processes()
            
            # Convert presentation to PDF
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            pdf_filename = f"{base_name}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)
            
            pdf_cmd = [
                'soffice',
                '--headless',
                '--invisible', 
                '--nologo',
                '--nolockcheck',
                '--convert-to',
                'pdf',
                '--outdir',
                temp_dir,
                filepath
            ]
            
            logger.info(f"Converting to PDF: {' '.join(pdf_cmd)}")
            result = subprocess.run(pdf_cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"PDF conversion failed with return code {result.returncode}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return jsonify({'error': 'PDF conversion failed'}), 500
            
            # Wait for file to be written
            time.sleep(2)
            
            if os.path.exists(pdf_path):
                logger.info(f"PDF export successful: {pdf_filename}")
                # Generate download filename
                original_name = os.path.splitext(filename)[0]
                download_name = f"{original_name}.pdf"
                return send_file(pdf_path, as_attachment=True, download_name=download_name, mimetype='application/pdf')
            else:
                logger.error(f"PDF file was not created: {pdf_path}")
                return jsonify({'error': 'PDF file was not created'}), 500
                
        except subprocess.TimeoutExpired:
            logger.error("PDF conversion timed out")
            return jsonify({'error': 'PDF conversion timed out'}), 500
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return jsonify({'error': f'PDF export failed: {str(e)}'}), 500
        finally:
            # Clean up LibreOffice processes
            kill_soffice_processes()
            
            # Note: We don't clean up temp_dir immediately as send_file needs it
            # The file will be cleaned up by the OS eventually

@app.route('/api/presentation/<session_id>/build', methods=['POST'])
def build_presentation(session_id):
    """Build out the entire presentation from structured text."""
    logger.info(f"Build presentation request received for session: {session_id}")
    
    if session_id not in sessions:
        logger.error(f"Session not found: {session_id}")
        return jsonify({'error': 'Session not found'}), 404
    
    try:
        data = request.json
        structured_text = data.get('structured_text', '')
        
        logger.info(f"Structured text length: {len(structured_text)}")
        logger.info(f"Structured text preview: {structured_text[:100]}...")
        
        if not structured_text:
            logger.error("No structured text provided")
            return jsonify({'error': 'No structured text provided'}), 400
        
        # DeepSeek is the only provider
        llm = get_llm_provider()
        
        # Use presentation engine to build from structured text
        engine = PresentationEngine()
        filepath = sessions[session_id]['filepath']
        
        # Build the presentation
        success = engine.build_from_structured_text(
            filepath,
            structured_text,
            llm
        )
        
        if success:
            # Re-parse the updated presentation
            structure = engine.parse_presentation(filepath)
            sessions[session_id]['structure'] = structure
            
            # Invalidate preview cache since the presentation has changed
            cache_key = f"{session_id}_previews"
            if cache_key in sessions:
                old_preview_dir = sessions[cache_key]
                # Clean up old preview directory
                if os.path.exists(old_preview_dir):
                    try:
                        shutil.rmtree(old_preview_dir)
                        logger.info(f"Cleaned up old preview directory: {old_preview_dir}")
                    except Exception as e:
                        logger.error(f"Failed to cleanup old preview directory: {e}")
                # Remove from cache
                del sessions[cache_key]
                logger.info(f"Invalidated preview cache for session: {session_id}")
            
            logger.info(f"Presentation built from structured text (session: {session_id})")
            
            return jsonify({
                'success': True,
                'structure': structure
            })
        else:
            return jsonify({'error': 'Failed to build presentation'}), 500
            
    except Exception as e:
        logger.error(f"Error building presentation: {str(e)}")
        return jsonify({'error': f'Build failed: {str(e)}'}), 500

# Cleanup function for temporary directories
def cleanup_temp_dirs():
    """Clean up all temporary preview directories on exit."""
    for key in list(sessions.keys()):
        if key.endswith('_previews'):
            preview_dir = sessions[key]
            if os.path.exists(preview_dir):
                try:
                    shutil.rmtree(preview_dir)
                    logger.info(f"Cleaned up preview directory: {preview_dir}")
                except Exception as e:
                    logger.error(f"Failed to cleanup preview directory {preview_dir}: {e}")

# Register cleanup function
atexit.register(cleanup_temp_dirs)

if __name__ == '__main__':
    app.run(debug=True, port=5030)