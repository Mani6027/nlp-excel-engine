"""
    Module to maintain mocks related to tests
"""
from flask import jsonify, Flask

from custom_exceptions import CustomBaseException
from utils import validate_process_excel_request

app = Flask(__name__)

@app.errorhandler(CustomBaseException)
def handle_custom_exception(error):
    """
    Handle custom exceptions.
    ---
    responses:
        400:
            description: Error message
    """
    return jsonify(error.to_dict()), error.status_code


@validate_process_excel_request
def mock_endpoint():
    return jsonify({"message": "Success"}), 200

app.add_url_rule('/process_excel', 'process_excel', mock_endpoint, methods=['POST'])
