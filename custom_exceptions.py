"""
    To handle custom exceptions
"""
from constants import StatusCodes, ErrorMessages, ErrorCodes


class CustomBaseException(Exception):
    """Custom exception for specific error conditions."""

    def __init__(self, message, error_code=None, status_code=StatusCodes.BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ErrorCodes.INVALID_REQUEST
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


class InvalidFile(CustomBaseException):
    """Exception for invalid file."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_FILE, error_code, StatusCodes.BAD_REQUEST)


class InvalidInstruction(CustomBaseException):
    """Exception for invalid instruction."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_INSTRUCTION, error_code, StatusCodes.BAD_REQUEST)


class InvalidOperation(CustomBaseException):
    """Exception for invalid operation."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_OPERATION, error_code, StatusCodes.BAD_REQUEST)


class InvalidColumn(CustomBaseException):
    """Exception for invalid column."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_COLUMN, error_code, StatusCodes.BAD_REQUEST)


class InvalidSheet(CustomBaseException):
    """Exception for invalid sheet."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_SHEET, error_code, StatusCodes.BAD_REQUEST)


class InvalidParameters(CustomBaseException):
    """Exception for invalid parameters."""

    def __init__(self, message=None, error_code=None):
        super().__init__(message or ErrorMessages.INVALID_PARAMETERS, error_code, StatusCodes.BAD_REQUEST)


class InvalidValue(CustomBaseException):
    """Exception for invalid value."""

    def __init__(self, message, error_code=None):
        super().__init__(message, error_code, StatusCodes.BAD_REQUEST)


class LLMRaisedException(CustomBaseException):
    """Exception for LLM raised exception."""

    def __init__(self, message, error_code=None):
        super().__init__(message, error_code, StatusCodes.BAD_REQUEST)


class EmptyColumnException(CustomBaseException):
    """Exception raised when a DataFrame column is empty."""

    def __init__(self, column_name, error_code=None):
        message = f"The column '{column_name}' is empty."
        super().__init__(message, error_code, StatusCodes.BAD_REQUEST)
