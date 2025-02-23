"""
Utility functions for the application
"""
import json
import os
from functools import wraps

from flask import request, jsonify
from google import genai
from pydantic import BaseModel, Field

from config import logger
from system_prompt import EXTRACTION_PROMPT


# create a schema for parameters checking from instructions
class Parameters(BaseModel):
    """
    Schema for parameters extracted from the instructions
    """
    operation: str = Field(..., description="The identified operation from the query.")
    columns: list[str] = Field(default_factory=list, description="List of column names extracted from the query.")
    sheets: list[str] = Field(default_factory=list, description="List of sheet names extracted from the query.")

    def to_dict(self):
        return self.model_dump()


def validate_process_excel_request(func: callable) -> callable:
    """
    Validates the request parameters for the process excel endpoint
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'file' not in request.files or 'instructions' not in request.form:
            return jsonify({"error": "File and instructions are required"}), 400

        file = request.files.get('file')
        instructions = request.form['instructions']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if instructions:
            params = parse_params_from_instructions(instructions)
            if not params:
                return jsonify({"error": "Invalid instructions"}), 400
            validate_params_from_instructions(params)
        
        return func(file, instructions, *args, **kwargs)
    return decorated_function


def parse_params_from_instructions(instructions: str):
    """
    Parse the parameters from the instructions
    """
    client = genai.Client(api_key=os.environ.get('GEMINI_FLASH_API_KEY'))
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=EXTRACTION_PROMPT,
        config={
            "response_mime_type": "application/json"
            }
        )
    response = response.text
    logger.debug(f"response from gemini: {response}")
    return json.loads(response)


def validate_params_from_instructions(params: dict) -> dict:
    """
    Validate the parameters extracted from the instructions
    """
    output = Parameters(**params)
    logger.debug(f"output: {output.to_dict()}")
    return output.to_dict()
