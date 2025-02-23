import pandas as pd

from constants import Operations
from core.math_processor import MathOperationExecutor
from core.nlp_processor import NLPTaskExecutor


class FileHandler:
    """Handles reading and writing Excel files."""

    def __init__(self, file_stream, sheet_names):
        self.file_stream = file_stream
        self.sheet_names = sheet_names
        self.__load_df = {}

    @property
    def df_dict(self) -> dict[str, pd.DataFrame]:
        return self.__load_df

    def load_file(self) -> None:
        """Loads Excel file from a file stream into a Pandas DataFrame."""
        xls = pd.ExcelFile(self.file_stream, engine='openpyxl')

        # Check if all sheets exist
        for sheet in self.sheet_names:
            if sheet not in xls.sheet_names:
                raise ValueError(f"Sheet '{sheet}' does not exist in the Excel file.")

        for sheet in self.sheet_names:
            self.__load_df[sheet] = pd.read_excel(xls, sheet_name=sheet)

    def save_file(self, save_path: str = './output.xlsx') -> None:
        """Saves modifications back to a specified path for the Excel file."""
        with pd.ExcelWriter(save_path, engine='openpyxl', mode='w') as writer:
            for sheet_name, df in self.__load_df.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)


class Engine:

    def __init__(self, metadata: dict, file_stream):
        self._metadata = metadata
        self._math_operation_executor = MathOperationExecutor()
        self._nlp_operation_executor = NLPTaskExecutor()
        self._file_handler = FileHandler(file_stream, metadata.get('sheets'))

    def execute(self):
        """
            Driver method to execute the user instructed task.
        """
        self._file_handler.load_file()
        df = self._file_handler.df_dict.get(self._metadata.get('sheets')[0])

        if (self._metadata.get('operation') in
                {Operations.SENTIMENT_ANALYSIS, Operations.SUMMARIZATION, Operations.TEXT_CLASSIFICATION}):
            self._nlp_operation_executor.execute(df, self._metadata)
        elif self._metadata.get('operation') == Operations.OPERATION_JOIN:
            right_df = self._file_handler.df_dict.get(self._metadata.get('sheets')[1])
            self._math_operation_executor.execute(df, self._metadata, right_df)
        else:
            self._math_operation_executor.execute(df, self._metadata)

        self._file_handler.save_file()
