from dotenv import load_dotenv
from flask import Flask, jsonify, send_file, g, request

from core import Engine
from errors import CustomBaseException
from utils import validate_process_excel_request
from config import logger

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.errorhandler(CustomBaseException)
def handle_custom_exception(error):
    """
        Handle custom exceptions
    """
    return jsonify(error.to_dict()), error.status_code


@app.route('/health')
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok"}), 200


@app.route('/process-excel', methods=['POST'])
@validate_process_excel_request
def process_excel():
    """
    Process Excel endpoint
    """
    core = Engine(g.params, request.files['file'])
    core.execute()

    return send_file("./output.xlsx", download_name="output.xlsx", as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    logger.info("Starting the server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
