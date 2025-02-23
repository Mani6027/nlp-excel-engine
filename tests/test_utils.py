from io import BytesIO
from unittest.mock import patch

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
