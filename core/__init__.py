import pandas as pd

from config import logger
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

    def update_df(self, df: pd.DataFrame, sheet_name: str):
        """Updates the dataframe for the specified sheet."""
        self.__load_df[sheet_name] = df
        logger.info(f"Updated dataframe for sheet '{sheet_name}'")

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
        logger.info(f"File saved to {save_path}")


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
                {Operations.SENTIMENT_ANALYSIS, Operations.SUMMARIZATION}):
            result = self._nlp_operation_executor.execute(df, self._metadata)
        elif self._metadata.get('operation') == Operations.OPERATION_JOIN:
            right_df = self._file_handler.df_dict.get(self._metadata.get('sheets')[1])
            result = self._math_operation_executor.execute(df, self._metadata, right_df)
        else:
            result = self._math_operation_executor.execute(df, self._metadata)

        if result is not None and isinstance(result, pd.DataFrame):
            self._file_handler.update_df(result, "result_sheet")

        self._file_handler.save_file()
