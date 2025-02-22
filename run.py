from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/health')
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok"})


@app.route('/process-excel', methods=['POST'])
def process_excel():
    """
    Process Excel endpoint
    """
    if ("file" not in request.files) or ("instruction" not in request.form):
        # TODO: raise valid exception here.
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    instruction = request.form['instruction']
    
    if file.filename == '':
        # TODO: raise valid exception here.
        return jsonify({"error": "No file uploaded"}), 400
    
    # call the function to process the excel file

    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
