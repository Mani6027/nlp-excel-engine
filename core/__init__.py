import pandas as pd

from core.math_processor import MathOperationExecutor
from core.nlp_processor import NLPTaskExecutor


class FileHandler:
    """Handles reading and writing Excel files."""

    def __init__(self, file_stream, sheet_name):
        self.file_stream = file_stream
        self.sheet_name = sheet_name
        self.df = None

    def load_file(self) -> pd.DataFrame:
        """Loads Excel file from a file stream into a Pandas DataFrame."""
        xls = pd.ExcelFile(self.file_stream, engine='openpyxl')
        if self.sheet_name and self.sheet_name not in xls.sheet_names:
            raise ValueError(f"Sheet '{self.sheet_name}' does not exist in the Excel file.")

        self.df = pd.read_excel(xls, sheet_name=self.sheet_name)
        return self.df

    def save_file(self, save_path: str = './output.xlsx'):
        """Saves modifications back to a specified path for the Excel file."""
        with pd.ExcelWriter(save_path, engine='openpyxl', mode='w') as writer:
            self.df.to_excel(writer, index=False)


class Engine:

    def __init__(self, metadata: dict, file_stream):
        self._metadata = metadata
        self._math_operation_executor = MathOperationExecutor()
        self._nlp_operation_executor = NLPTaskExecutor()
        self._file_handler = FileHandler(file_stream, metadata.get('sheets')[0])

    def execute(self):
        """
            Driver method to execute the user instructed task.
        """
        self._file_handler.load_file()
        if self._metadata.get('operation') in {'sentiment_analysis', 'summarization', 'text_classification'}:
            self._nlp_operation_executor.execute(self._file_handler.df, self._metadata)
        else:
            self._math_operation_executor.execute(self._file_handler.df, self._metadata)

        self._file_handler.save_file()
