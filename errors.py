"""
    To handle custom exceptions
"""
from constants import StatusCodes, ErrorMessages


class CustomBaseException(Exception):
    """Custom exception for specific error conditions."""

    def __init__(self, message, error_code=None, status_code=StatusCodes.BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

    def __str__(self):
        if self.error_code is not None:
            return f"[Error {self.error_code}] {self.message}"
        return self.message

    def to_dict(self):
        """Convert exception details to a dictionary."""
        return {
            "error": self.message,
            "error_code": self.error_code
        }


class InvalidFileException(CustomBaseException):
    """Exception for invalid file."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_FILE, error_code, StatusCodes.BAD_REQUEST)


class InvalidInstructionException(CustomBaseException):
    """Exception for invalid instruction."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_INSTRUCTION, error_code, StatusCodes.BAD_REQUEST)


class InvalidOperationException(CustomBaseException):
    """Exception for invalid operation."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_OPERATION, error_code, StatusCodes.BAD_REQUEST)


class InvalidColumnException(CustomBaseException):
    """Exception for invalid column."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_COLUMN, error_code, StatusCodes.BAD_REQUEST)


class InvalidSheetException(CustomBaseException):
    """Exception for invalid sheet."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_SHEET, error_code, StatusCodes.BAD_REQUEST)

class InvalidParametersException(CustomBaseException):
    """Exception for invalid parameters."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_PARAMETERS, error_code, StatusCodes.BAD_REQUEST)
