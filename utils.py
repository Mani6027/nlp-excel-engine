"""
Utility functions for the application
"""
import json
import os
from functools import wraps

import google.generativeai as genai
import pandas as pd
from flask import request, g
from pydantic import BaseModel, Field, model_validator

from config import logger
from constants import ErrorCodes, Operations
from custom_exceptions import InvalidParameters, InvalidInstruction, InvalidFile
from system_prompt import EXCEL_PARAM_EXTRACTION_PROMPT


# create a schema for parameters checking from instructions
class Parameters(BaseModel):
    """
    Schema for parameters extracted from the instructions
    """
    operation: str = Field(..., description="The identified operation from the query.")
    columns: list[str] = Field(default_factory=list, description="List of column names extracted from the query.")
    sheets: list[str] = Field(default_factory=list, description="List of sheet names extracted from the query.")
    parameters: dict = Field(default_factory=dict, description="Parameters extracted from the query.")

    @model_validator(mode="after")
    def validate_non_empty(self):
        is_pivot_table = self.operation in {Operations.PIVOT_TABLE, Operations.UNPIVOT_TABLE}
        if (not self.columns) and (not is_pivot_table):
            raise InvalidInstruction("Adjust your query to include at least one column.", error_code=ErrorCodes.INVALID_INSTRUCTION)
        elif not self.sheets:
            raise InvalidInstruction("Adjust your query to include at least one sheet.", error_code=ErrorCodes.INVALID_INSTRUCTION)
        if not self.parameters and (self.operation in {Operations.PIVOT_TABLE, Operations.UNPIVOT_TABLE, Operations.INNER_JOIN,
                              Operations.LEFT_JOIN, Operations.RIGHT_JOIN, Operations.FULL_OUTER_JOIN}):
            raise InvalidInstruction(message=f"Could not understand by the system. Describe the operation in more detail.",
                                     error_code=ErrorCodes.OPERATION_NOT_SUPPORTED)
        return self

    def to_dict(self):
        return self.model_dump()


def validate_process_excel_request(func: callable) -> callable:
    """
    Validates the request parameters for the process excel endpoint
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'file' not in request.files or 'instructions' not in request.form:
            raise InvalidParameters(error_code=ErrorCodes.INVALID_PARAMETERS)

        file = request.files.get('file')
        instructions = request.form['instructions']

        if file.filename == '':
            raise InvalidFile(error_code=ErrorCodes.INVALID_FILE)

        if instructions:
            excel_metadata = extract_excel_metadata(file)
            params = extract_params_from_instructions(excel_metadata, instructions)
            if not params:
                raise InvalidInstruction(error_code=ErrorCodes.INVALID_INSTRUCTION)
            validated_params = validate_params_from_instructions(params)
            g.params = validated_params
        return func(*args, **kwargs)
    return decorated_function


def extract_params_from_instructions(excel_metadata, instructions: str) -> dict:
    """
    Parse the parameters from the instructions
    """
    genai.configure(api_key=os.environ.get('GEMINI_FLASH_API_KEY'))
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",
    }
    system_prompt = EXCEL_PARAM_EXTRACTION_PROMPT.format(excel_metadata=excel_metadata, user_query=instructions)
    logger.info(f"system_prompt: {system_prompt}")
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction=system_prompt
    )
    chat_session = model.start_chat(history=[])
    _response = chat_session.send_message(instructions)
    _response = _response.text
    logger.info(f"response from gemini: {_response}")
    return json.loads(_response)


def validate_params_from_instructions(params: dict) -> dict:
    """
    Validate the parameters extracted from the instructions
    """
    output = Parameters(**params)
    logger.debug(f"output: {output.to_dict()}")
    return output.to_dict()


def extract_excel_metadata(file_stream):
    """Extract sheet names, column names, and data types from an uploaded Excel file."""
    metadata = {}
    xls = pd.ExcelFile(file_stream, engine='openpyxl')
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, nrows=2)
        metadata[sheet] = list(df.columns)
    logger.debug(f"metadata of uploaded excel file:: {metadata}")
    return metadata
