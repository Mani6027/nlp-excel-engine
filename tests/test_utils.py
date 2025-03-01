import io
import json
from io import BytesIO
from unittest.mock import patch

import pandas as pd

from tests import BaseTest
from tests.mocks.mock_utils import app
from utils import extract_excel_metadata


class TestValidateProcessExcelRequest(BaseTest):
    """Tests for validate_process_excel_request"""

    def setUp(self):
        """Set up Flask test client"""
        self.client = app.test_client()

    @patch("utils.extract_params_from_instructions")
    def test_valid_request(self, mock_parse_params_from_instructions):
        """ Test with valid file and valid instructions"""
        output = BytesIO()
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})  # Sample data
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
        output.seek(0)

        data = {
            "file": (output, "test.xlsx"),
            "instructions": "Sum column A and column B"
        }
        mock_parse_params_from_instructions.return_value ={"operation": "Summation", "columns": ["A", "B"], "sheets": ["Sheet1"]}
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "Success"})

    def test_missing_file(self):
        """ Test when file is missing"""
        data = {"instructions": "valid instruction"}
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        res = json.loads(response.text)
        self.assertEqual(res['error'], "Invalid parameters. Provide valid parameters.")
        self.assertEqual(res['error_code'], "INVALID_PARAMETERS")

    def test_invalid_file_data(self):
        """ Test when instructions are missing"""
        data = {"file": (BytesIO(b"dummy data"), "test.xlsx")}
        res = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 400)
        res = json.loads(res.text)
        self.assertEqual(res['error'], "Invalid parameters. Provide valid parameters.")
        self.assertEqual(res['error_code'], "INVALID_PARAMETERS")

    def test_empty_filename(self):
        """ Test when file is uploaded but has an empty filename"""
        data = {"file": (BytesIO(b"dummy data"), ""), "instructions": "valid instruction"}
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        res = json.loads(response.text)
        self.assertEqual(res['error'], "Invalid file. Upload a valid Excel file.")
        self.assertEqual(res['error_code'], "INVALID_FILE")

    @patch("utils.extract_params_from_instructions", return_value=None)
    def test_invalid_instructions(self, mock_parse):
        """ Test with invalid instructions (extract_params_from_instructions fails)"""

        output = BytesIO()
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})  # Sample data
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
        output.seek(0)

        data = {
            "file": (output, "test.xlsx"),
            "instructions": "invalid instruction"
        }
        mock_parse.return_value = {"operation": "Invalid", "columns": [], "sheets": [], "parameters": {}}

        res = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 400)
        res = res.text
        res = json.loads(res)
        self.assertEqual(res['error'], "Adjust your query to include at least one column.")
        self.assertEqual(res['error_code'], "INVALID_INSTRUCTION")


class TestExtractExcelMetadata(BaseTest):

    def setUp(self):
        # Create a sample Excel file in memory
        self.excel_data = io.BytesIO()
        with pd.ExcelWriter(self.excel_data, engine='openpyxl') as writer:
            # Sample data for multiple sheets
            df1 = pd.DataFrame({"A": [1, 2], "B": [3.5, 4.5], "C": ["x", "y"]})
            df2 = pd.DataFrame({"X": [True, False], "Y": ["foo", "bar"]})

            df1.to_excel(writer, sheet_name="Sheet1", index=False)
            df2.to_excel(writer, sheet_name="Sheet2", index=False)

        self.excel_data.seek(0)

    def test_extract_metadata(self):
        metadata = extract_excel_metadata(self.excel_data)
        expected_metadata = {
            "Sheet1":  ["A", "B", "C"],
            "Sheet2": ["X", "Y"]
        }
        self.assertEqual(metadata, expected_metadata)

    def tearDown(self):
        self.excel_data.close()
        self.excel_data = None
