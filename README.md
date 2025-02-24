# NLP Excel Engine

The NLP Excel Engine is a Flask-based application designed to process Excel files using specified operations. It utilizes natural language processing to interpret user instructions and perform mathematical operations on data in Excel sheets.

## Features

- Upload Excel files and process them based on user instructions.
- Supports various mathematical operations, including addition, subtraction, multiplication, division, averages, and date differences.
- Provides a health check endpoint to verify the service status.
- Automatically generates documentation for API endpoints using Swagger.

## Requirements

- Python 3.8+
- Flask
- Flask-Cors
- Flasgger
- Pandas
- Openpyxl
- Python-dotenv
- Dateutil
- Pydantic

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd nlp-excel-engine
2. Create a virtual environment (optional but recommended):
    ```
    python -m venv venv
    source venv/bin/activate
    ```
3. Install the required packages
    ```
    pip install -r requirements.txt
    ```
4. Set up your environment variables by creating a .env file:
    ```
    GEMINI_FLASH_API_KEY=<your_api_key>
    ```

## Usage
Run the application:

    python app.py or docker-compose up --build
    Access the API documentation at http://localhost:5001/apidocs.

Use the following endpoints:
- Health Check
    Endpoint: /health
    Method: GET
    Response: Returns the status of the application.
- Process Excel
    Endpoint: /process-excel
    Method: POST
    Parameters:
    file: Excel file to be processed (form-data)
    instructions: Instructions for processing the Excel file (form-data)
    Response: Processed Excel file for download.

## Limitations
The engine still has a lot of improvements to do, including enhancing the NLP capabilities and optimizing performance. Additionally, the codebase requires further refactoring to improve readability and maintainability.

## Error Handling
The application raises custom exceptions for various error conditions, including:
- **Invalid Parameters**: Raised when required parameters are missing or invalid.
- **Invalid File**: Raised when the uploaded file is not valid.
- **Invalid Instruction**: Raised when instructions cannot be parsed or executed.

### Acknowledgements
- Flask for the web framework
- Pandas for data processing
- Gemini-Flash GPT model used in processing instructions

!!Feel free to make any further modifications as needed!!
