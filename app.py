from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
import subprocess
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    if not file.filename.endswith('.eml'):
        return 'Please upload an EML file', 400
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Run the decode-spam-headers.py script with the uploaded file
        script_path = os.path.join(BASE_DIR, 'decode-spam-headers.py')
        output_file = os.path.join(BASE_DIR, 'test.html')
        
        # Run the script from the correct directory
        subprocess.run(['python', script_path, filepath], 
                     check=True,
                     cwd=BASE_DIR)  # Set the working directory
        
        # Read the generated HTML file
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean up temporary files
        os.remove(filepath)
        os.remove(output_file)
        
        return html_content
        
    except Exception as e:
        # Clean up the temporary file in case of error
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists(output_file):
            os.remove(output_file)
        return f'Error processing file: {str(e)}', 500

if __name__ == '__main__':
    app.run(debug=True) 