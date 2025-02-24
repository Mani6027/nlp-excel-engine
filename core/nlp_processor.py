import asyncio
import json
import os
from typing import Any

import aiohttp
import pandas as pd

from constants import Operations, ErrorCodes
from errors import LLMRaisedException, EmptyColumnException


class Summarizer:

    def __init__(self, gemini_model_name: str = "gemini-2.0-flash", chunk_size: int = 100):
        self._api_key = os.environ.get('GEMINI_FLASH_API_KEY')
        self._model_name = gemini_model_name
        self.chunk_size = chunk_size
        self._api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self._api_key}"

    def __chunk_data(self, data_list):
        """Splits the data list into smaller chunks."""
        return [data_list[i:i + self.chunk_size] for i in range(0, len(data_list), self.chunk_size)]

    @staticmethod
    def __format_payload(chunk: list[str]) -> dict:
        """Formats the payload for the LLM API call."""
        system_content = {"text": "Summarize following content"}
        content_parts = [{"text": text} for text in chunk]
        return {
            "contents": [{
                "parts": [system_content] + content_parts
            }],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 1000,
            }
        }

    async def __call_llm_api(self, chunk):
        """Calls the LLM API with a chunk of text data."""
        headers = {
            'Content-Type': 'application/json',
        }
        payload = self.__format_payload(chunk)
        async with aiohttp.ClientSession() as session:
            async with session.post(self._api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    raise LLMRaisedException(message=f"Request failed: {response.status} - {await response.text()}",
                                             error_code=ErrorCodes.LLM_RAISED_EXCEPTION)
                result = await response.json()
                for candidate in result.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        return part["text"]

    async def __process_chunks(self, chunks):
        """Processes each chunk of data and gathers responses."""
        tasks = [asyncio.create_task(self.__call_llm_api(chunk)) for chunk in chunks]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses

    async def __summarize_chunks(self, data_list: list[str]) -> list[str]:
        """Summarizes the text from a list of strings in chunks."""
        chunks = self.__chunk_data(data_list)
        summaries = await self.__process_chunks(chunks)
        return summaries

    async def __summarize(self, data_list: list[str]) -> str:
        """Summarizes the text from a list of strings."""
        initial_summaries = await self.__summarize_chunks(data_list)
        final_summary = await self.__summarize_chunks(initial_summaries)
        return final_summary[0]

    def summarize(self, data_list: list[str]) -> str:
        """Summarizes the text from a list of strings."""
        return asyncio.run(self.__summarize(data_list))

class TextClassifier:

    def __init__(self, gemini_model_name: str = "gemini-2.0-flash", chunk_size: int = 100):
        self._api_key = os.environ.get('GEMINI_FLASH_API_KEY')
        self._model_name = gemini_model_name
        self.chunk_size = chunk_size
        self._api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self._api_key}"

    def __chunk_data(self, data_list):
        """Splits the data list into smaller chunks."""
        return [data_list[i:i + self.chunk_size] for i in range(0, len(data_list), self.chunk_size)]

    @staticmethod
    def __format_payload(chunk: list[str]) -> dict:
        """Formats the payload for the LLM API call."""
        system_content = {"text": "Perform sentiment analysis on each sentence separately and return JSON in this format: {\"index\": <number>, \"text\": \"<input>\", \"sentiment\": \"Positive|Negative|Neutral\"}. Respond with a JSON array containing results for each input."}
        return {
            "contents": [
                {
                    "role": "user",
                    "parts": [system_content] + [{"text": json.dumps(text)} for text in chunk]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 1000,
            }
        }

    @staticmethod
    def __format_response(response: dict) -> list[str]:
        """Formats the response from the API call."""
        sentiments = []
        for candidate in response.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                raw_text = part["text"]
                # Remove markdown formatting
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                try:
                    sentiments.append(json.loads(raw_text))  # Convert to dictionary
                except json.JSONDecodeError:
                    print("Error decoding JSON:", raw_text)
        return sentiments

    async def __fetch_sentiments(self, chunks: list[str]) -> list[str]:
        """Summarizes the text from a list of strings in chunks."""
        payload = self.__format_payload(chunks)
        async with aiohttp.ClientSession() as session:
            async with session.post(self._api_url, json=payload, headers={"Content-Type": "application/json"}) as response:
                response = await response.json()
                return self.__format_response(response)

    async def __process_chunks(self, chunks):
        """Processes each chunk of data and gathers responses."""
        tasks = [asyncio.create_task(self.__fetch_sentiments(chunk)) for chunk in chunks]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses

    async def __classify(self, data_list: list[str]) -> list[list[dict[str, Any]]]:
        """Summarizes the text from a list of strings in chunks."""
        chunks = self.__chunk_data(data_list)
        summaries = await self.__process_chunks(chunks)
        return summaries

    def classify(self, data_list: list[str]) -> list[list[dict[str, Any]]]:
        """Summarizes the text from a list of strings."""
        responses = asyncio.run(self.__classify(data_list))
        return responses


class NLPTaskExecutor:

    def __init__(self):
        self._summarizer = Summarizer()
        self._text_classifier = TextClassifier()

    def sentiment_analysis(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
            Sentiment analysis on column.
        """
        data_list = df[column].tolist()
        if not data_list:
            raise EmptyColumnException(column_name=column)
        responses = self._text_classifier.classify(data_list)

        sentiment_dict = {}
        for response in responses:
            if isinstance(response, list):
                for item in response:
                    _index = item.get('index')
                    text = item.get('text')
                    sentiment = item.get('sentiment')
                    if text and sentiment and _index is not None:
                        # Concatenate the text and index to create a unique key
                        sentiment_dict[(text, _index)] = sentiment

        def select_value(index_value: int, row_val):
            key = (row_val, index_value)
            return sentiment_dict.get(key, "Unclassified")

        df[f'Classified_{column}'] = df[column].apply(lambda row: select_value(row.name, row[column]), axis=1)
        return df

    def summarization(self, df: pd.DataFrame, column: str, on: str = None) -> pd.DataFrame:
        """
            Summarize the sentence from the given column. Add result in a separate column.
        """
        data_list = df[column].tolist()

        if not data_list:
            raise EmptyColumnException(column_name=column)

        summary = self._summarizer.summarize(data_list)
        df[f'Summarized_{column}'] = summary
        return df

    def execute(self, df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
            Method to execute the NLP operations
        """
        operations = metadata.get('operation')
        if operations == Operations.SUMMARIZATION:
            return self.summarization(df, metadata.get('columns')[0])
        elif operations == Operations.TEXT_CLASSIFICATION:
            return self.sentiment_analysis(df, metadata.get('columns')[0])
