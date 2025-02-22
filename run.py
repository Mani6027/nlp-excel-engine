from flask import Flask, jsonify, request, send_file
from app.utils import validate_process_excel_request

app = Flask(__name__)

@app.route('/health')
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok"})


@app.route('/process-excel', methods=['POST'])
@validate_process_excel_request
def process_excel():
    """
    Process Excel endpoint
    """
    # call the function to process the excel file

    return send_file(output, attachment_filename="placeholder_name.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
