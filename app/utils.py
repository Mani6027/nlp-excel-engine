"""
Utility functions for the application
"""
from flask import request, jsonify
from functools import wraps
from google import genai

def validate_process_excel_request(func: callable) -> callable:
    """
    Validates the request parameters for the process excel endpoint
    """
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


def parse_params_from_instructions(instructions: str):
    """
        Parses the parameters from the instructions
    """
    pass
