from unittest.mock import patch, AsyncMock

import pandas as pd

from core import NLPTaskExecutor
from custom_exceptions import EmptyColumnException
from tests import BaseTest


class TestNLPTaskExecutor(BaseTest):
    def setUp(self):
        self.executor = NLPTaskExecutor()
        self.sample_data = {
            'Text': [
                'I love programming!',
                'Python is great for data science.',
                'I dislike bugs in my code.',
                'The weather is nice today.'
            ]
        }
        self.df = pd.DataFrame(self.sample_data)

    @patch('core.nlp_processor.TextClassifier.classify', new_callable=AsyncMock)
    async def test_sentiment_analysis(self, mock_classify):
        mock_classify.return_value = [
            [{'index': 0, 'text': 'I love programming!', 'sentiment': 'Positive'}],
            [{'index': 1, 'text': 'Python is great for data science.', 'sentiment': 'Positive'}],
            [{'index': 2, 'text': 'I dislike bugs in my code.', 'sentiment': 'Negative'}],
            [{'index': 3, 'text': 'The weather is nice today.', 'sentiment': 'Positive'}]
        ]

        result_df = await self.executor.sentiment_analysis(self.df, 'Text')
        expected_sentiments = ['Positive', 'Positive', 'Negative', 'Positive']

        self.assertListEqual(result_df[f'Classified_Text'].tolist(), expected_sentiments)

    @patch('core.nlp_processor.Summarizer.summarize', new_callable=AsyncMock)
    async def test_summarization(self, mock_summarize):
        mock_summarize.return_value.set_result(["Mixed of programming and weather. Mike loves to code in python and he thinks"
             "python is greate for datascience. And weather is nice today."])

        result_df = await self.executor.summarization(self.df, 'Text')

        expected_summaries = ["Mixed of programming and weather. Mike loves to code in python and he thinks"
                              "python is greate for datascience. And weather is nice today."]

        pd.testing.assert_series_equal(result_df['Summarized_Text'], pd.Series(expected_summaries))

    def test_sentiment_analysis_empty_column(self):
        empty_df = pd.DataFrame(columns=['Text'])
        with self.assertRaises(EmptyColumnException):
            self.executor.sentiment_analysis(empty_df, 'Text')

    def test_summarization_empty_column(self):
        empty_df = pd.DataFrame(columns=['Text'])
        with self.assertRaises(EmptyColumnException):
            self.executor.summarization(empty_df, 'Text')
