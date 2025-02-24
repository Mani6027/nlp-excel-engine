from dotenv import load_dotenv
from flask import Flask, jsonify, send_file, g, request

from core import Engine
from custom_exceptions import CustomBaseException
from utils import validate_process_excel_request
from config import logger
from flasgger import Swagger

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)

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


@app.route('/health')
def health_check():
    """
    Health check endpoint.
    ---
    responses:
        200:
            description: OK response
            schema:
                id: HealthCheck
                properties:
                    status:
                        type: string
                        example: ok
    """
    return jsonify({"status": "ok"}), 200


@app.route('/process-excel', methods=['POST'])
@validate_process_excel_request
def process_excel():
    """
    Process an Excel file and return the processed output.
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Input Excel file to be processed.
      - name: instructions
        in: formData
        type: string
        required: true
        description: Instructions for the processing of the Excel file (e.g., "Sum column A and column B").
    responses:
        200:
            description: Successfully processed Excel file and returned as a downloadable file.
            schema:
                type: file
        400:
            description: Bad request if the input file is invalid.
        500:
            description: Internal server error.
    """
    core = Engine(g.params, request.files['file'])
    core.execute()

    return send_file("./output.xlsx", download_name="output.xlsx", as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    logger.info("Starting the server...")
    app.run(host="0.0.0.0", port=5001, debug=True)
    # to enable CORS for the swagger UI
    from flask_cors import CORS
    CORS(app)
