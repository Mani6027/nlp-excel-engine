class Operations:
    """Available operations for the engine."""
    # available math operations
    ADDITION = 'addition'
    SUMMATION = 'summation'
    SUBTRACTION = 'subtraction'
    MULTIPLICATION = 'multiplication'
    DIVISION = 'division'
    AVG = 'avg'
    MIN = 'min'
    MAX = 'max'

    ALL_MATH_OPERATIONS = [ADDITION, SUMMATION, SUBTRACTION, MULTIPLICATION, DIVISION, AVG, MIN, MAX]

    # NLP operations
    SENTIMENT_ANALYSIS = 'sentiment_analysis'
    SUMMARIZATION = 'summarization'

    # Pivot and unpivot operations
    PIVOT_TABLE = 'pivot_table'
    UNPIVOT_TABLE = 'unpivot_table'

    # join operations
    OPERATION_JOIN = 'join'
    INNER_JOIN = 'inner_join'
    LEFT_JOIN = 'left_join'
    RIGHT_JOIN = 'right_join'
    FULL_OUTER_JOIN = 'outer_join'

    # date operations
    DATE_DIFFERENCE = 'date_difference'

    ######### Misc ########
    DF_JOIN_MAPPER = {
        INNER_JOIN: 'inner',
        LEFT_JOIN: 'left',
        RIGHT_JOIN: 'right',
        FULL_OUTER_JOIN: 'outer'
    }


class ErrorCodes:
    """Error codes for custom exceptions."""
    INVALID_FILE = "INVALID_FILE"
    INVALID_INSTRUCTION = "INVALID_INSTRUCTION"
    INVALID_OPERATION = "INVALID_OPERATION"
    INVALID_COLUMN = "INVALID_COLUMN"
    INVALID_SHEET = "INVALID_SHEET"
    INVALID_PARAMETERS = "INVALID_PARAMETERS"
    INVALID_VALUE = "INVALID_VALUE"
    LLM_RAISED_EXCEPTION = "LLM_RAISED_EXCEPTION"
    INVALID_REQUEST = "INVALID_REQUEST"
    OPERATION_NOT_SUPPORTED = "OPERATION_NOT_SUPPORTED"


class ErrorMessages:
    """Error messages for custom exceptions."""
    INVALID_FILE = "Invalid file. Upload a valid Excel file."
    INVALID_INSTRUCTION = "Invalid instruction. Provide a valid instruction."
    INVALID_OPERATION = "Invalid operation. Provide a valid operation."
    INVALID_COLUMN = "Invalid column. Provide a valid column."
    INVALID_SHEET = "Invalid sheet. Provide a valid sheet."
    INVALID_PARAMETERS = "Invalid parameters. Provide valid parameters."


class StatusCodes:
    """Status codes for custom exceptions."""
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500
    NOT_FOUND = 404
