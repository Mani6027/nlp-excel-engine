from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
