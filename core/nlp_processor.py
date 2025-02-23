import pandas as pd


class NLPTaskExecutor:

    def __init__(self):
        self._llm_client = None

    def __get_llm_client(self):
        """
            Private method to load llm client. Using lazy loading to avoid creating multiple instance.
        """
        pass

    def sentiment_analysis(self, df: pd.DataFrame, column: str):
        """
            Sentiment analysis on column.
        """
        pass

    def text_classification(self, df: pd.DataFrame, column: str):
        """
            Classify the sentence from the given column. Add result in a separate column.
        """
        pass

    def summarization(self, df: pd.DataFrame, column: str):
        """
            Summarize the sentence from the given column. Add result in a separate column.
        """
        pass

    def execute(self, df: pd.DataFrame, metadata: dict):
        """
            Method to execute the NLP operations
        """
        pass
