import io
from io import BytesIO
from unittest.mock import patch

import pandas as pd

from app.utils import extract_excel_metadata
from tests import BaseTest
from tests.mocks.mock_utils import app


class TestValidateProcessExcelRequest(BaseTest):
    """Tests for validate_process_excel_request"""

    def setUp(self):
        """Set up Flask test client"""
        self.client = app.test_client()

    @patch("app.utils.parse_params_from_instructions")
    def test_valid_request(self, mock_parse_params_from_instructions):
        """ Test with valid file and valid instructions"""
        data = {
            "file": (BytesIO(b"dummy data"), "test.xlsx"),
            "instructions": "Sum column A and column B"
        }
        mock_parse_params_from_instructions.return_value ={"operation": "Summation", "columns": ["A", "B"]}
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "Success"})

    def test_missing_file(self):
        """ Test when file is missing"""
        data = {"instructions": "valid instruction"}
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "File and instructions are required"})

    def test_missing_instructions(self):
        """ Test when instructions are missing"""
        data = {"file": (BytesIO(b"dummy data"), "test.xlsx")}
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "File and instructions are required"})

    def test_empty_filename(self):
        """ Test when file is uploaded but has an empty filename"""
        data = {"file": (BytesIO(b"dummy data"), ""), "instructions": "valid instruction"}
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "No selected file"})

    @patch("app.utils.parse_params_from_instructions", return_value=None)
    def test_invalid_instructions(self, mock_parse):
        """ Test with invalid instructions (parse_params_from_instructions fails)"""
        data = {
            "file": (BytesIO(b"dummy data"), "test.xlsx"),
            "instructions": "invalid instruction"
        }
        response = self.client.post("/process_excel", data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Invalid instructions"})


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
            "Sheet1": {
                "columns": ["A", "B", "C"],
                "data_types": {"A": "int64", "B": "float64", "C": "object"}
            },
            "Sheet2": {
                "columns": ["X", "Y"],
                "data_types": {"X": "bool", "Y": "object"}
            }
        }
        self.assertEqual(metadata, expected_metadata)

    def tearDown(self):
        self.excel_data.close()
        self.excel_data = None
