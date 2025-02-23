import os

import pandas as pd
import google.generativeai as genai


class NLPTaskExecutor:

    def __init__(self):
        self._llm_client = None

    def __get_llm_client(self):
        """
            Private method to load llm client. Using lazy loading to avoid creating multiple instance.
        """
        genai.configure(api_key=os.environ.get('GEMINI_FLASH_API_KEY'))
        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }
        system_prompt = ""
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction=system_prompt
        )
        chat_session = model.start_chat(history=[])

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
