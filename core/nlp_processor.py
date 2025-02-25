import asyncio
import json
import os
from typing import Any

import aiohttp
import pandas as pd

from config import logger
from constants import Operations
from custom_exceptions import EmptyColumnException


class BaseNLModel:
    def __init__(self, gemini_model_name: str = "gemini-2.0-flash", chunk_size: int = 20):
        self._api_key = os.environ.get('GEMINI_FLASH_API_KEY')
        self._model_name = gemini_model_name
        self.chunk_size = chunk_size
        self._api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self._api_key}"

    def chunk_data(self, data_list):
        """Splits the data list into smaller chunks."""
        return [data_list[i:i + self.chunk_size] for i in range(0, len(data_list), self.chunk_size)]


class Summarizer(BaseNLModel):
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
                "maxOutputTokens": 7192, # Optimize this later.
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
                result = await response.json()
                for candidate in result.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        return part["text"]

    async def __process_chunks(self, chunks):
        """Processes each chunk of data and gathers responses."""
        tasks = [asyncio.create_task(self.__call_llm_api(chunk)) for chunk in chunks]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return [response for response in responses if response]

    async def __summarize_chunks(self, data_list: list[str]) -> list[str]:
        """Summarizes the text from a list of strings in chunks."""
        chunks = self.chunk_data(data_list)
        summaries = await self.__process_chunks(chunks)
        return summaries

    async def __summarize(self, data_list: list[str]) -> list[str]:
        """Summarizes the text from a list of strings."""
        initial_summaries = await self.__summarize_chunks(data_list)
        # can comment this out if you want to see the full summaries
        final_summary = await self.__summarize_chunks(initial_summaries)
        return final_summary

    def summarize(self, data_list: list[str]) -> list[str]:
        """Summarizes the text from a list of strings."""
        return asyncio.run(self.__summarize(data_list))


class TextClassifier(BaseNLModel):
    def __chunk_data(self, data_list):
        """Splits the data list into smaller chunks."""
        return [data_list[i:i + self.chunk_size] for i in range(0, len(data_list), self.chunk_size)]

    @staticmethod
    def __format_payload(chunk: list[str]) -> dict:
        """Formats the payload for the LLM API call."""
        system_content = {"text": "Perform sentiment analysis on each provided text separately and return the result in JSON format. Each input will be structured as \"<index>: <number> <text>: <input>\". Extract the index and text, then respond with a JSON array where each object includes the original index, text, and a 'sentiment' field with values 'Positive', 'Negative', or 'Neutral'."}
        return {
            "contents": [
                {
                    "role": "user",
                    "parts": [system_content] + [{"text": json.dumps(f"<index>: {index} <text>: {text}")} for index, text in chunk]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 7192, # Optimize this later.
            }
        }

    @staticmethod
    def __format_response(response: dict) -> list[str]:
        """Formats the response from the API call."""
        data_list = []
        json_text = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
        if json_text:
            json_text = json_text.replace("```json\n", "").replace("\n```", "")
        else:
            return data_list
        try:
            data_list = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.info(f"Error decoding JSON: {e}")
        return data_list

    async def __fetch_sentiments(self, chunks: list[str]) -> list[str]:
        """Summarizes the text from a list of strings in chunks."""
        payload = self.__format_payload(chunks)
        async with aiohttp.ClientSession() as session:
            async with session.post(self._api_url, json=payload, headers={"Content-Type": "application/json"}) as response:
                response = await response.json()
                return self.__format_response(response)

    async def __process_chunks(self, chunks):
        """Processes each chunk of data and gathers responses."""
        results = []
        tasks = [asyncio.create_task(self.__fetch_sentiments(chunk)) for chunk in chunks]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if response:
                results.extend(response)
        return results

    async def __classify(self, data_list: list[tuple[int, str]]) -> list[dict[str, Any]]:
        """Classifies the text from a list of strings in chunks."""
        chunks = self.chunk_data(data_list)
        result = await self.__process_chunks(chunks)
        return result

    def classify(self, data_list: list[tuple[int, str]]) -> list[dict[str, Any]]:
        """Classifies the text from a list of strings."""
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
        data_list = list(df[column].items())
        if not data_list:
            raise EmptyColumnException(column_name=column)
        responses = self._text_classifier.classify(data_list)

        sentiment_dict = {}
        logger.debug(f"Responses: {responses}")
        for response in responses:
            _index = response.get('index')
            text = response.get('text')
            sentiment = response.get('sentiment')
            if text and sentiment and _index is not None:
                sentiment_dict[(text, _index)] = sentiment

        def select_value(index_value: int, row_val):
            key = (row_val, str(index_value))
            return sentiment_dict.get(key, "Unclassified")

        df[f'Classified_{column}'] = df.apply(lambda row: select_value(row.name, row[column]), axis=1)
        return df

    def summarization(self, df: pd.DataFrame, column: str, on: str = None) -> pd.DataFrame:
        """
            Summarize the sentence from the given column. Add result in a separate column.
        """
        if column not in df.columns:
            raise EmptyColumnException(column_name=column)

        data_list = df[column].dropna().tolist()

        if not data_list:
            raise EmptyColumnException(column_name=column)

        summary = self._summarizer.summarize(data_list)
        df[f'Summarized_{column}'] = pd.Series(summary[:len(data_list)]).reindex(df.index)
        return df

    def execute(self, df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
            Method to execute the NLP operations
        """
        operations = metadata.get('operation')
        if operations == Operations.SUMMARIZATION:
            return self.summarization(df, metadata.get('columns')[0])
        elif operations == Operations.SENTIMENT_ANALYSIS:
            return self.sentiment_analysis(df, metadata.get('columns')[0])
