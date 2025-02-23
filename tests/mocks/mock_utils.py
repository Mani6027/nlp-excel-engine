"""
    Module to maintain mocks related to tests
"""
from flask import jsonify, Flask

from utils import validate_process_excel_request

app = Flask(__name__)


@validate_process_excel_request
def mock_endpoint(file, instructions):
    return jsonify({"message": "Success"}), 200

app.add_url_rule('/process_excel', 'process_excel', mock_endpoint, methods=['POST'])
