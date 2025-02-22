"""
Utility functions for the application
"""
from functools import wraps

def validate_process_excel_request(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'file' not in request.files or 'instructions' not in request.form:
            return jsonify({"error": "File and instructions are required"}), 400

        file = request.files['file']
        instructions = request.form['instructions']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        return f(file, instructions, *args, **kwargs)
    return decorated_function
