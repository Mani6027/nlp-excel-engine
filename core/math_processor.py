from typing import Union, List

import pandas as pd

from constants import Operations


class MathOperationExecutor:
    """
        Executor to handle mathematical operation on columns
    """
    @staticmethod
    def __check_column_exists(df: pd.DataFrame, column: str):
        """
            Checks if the specified column exists in the DataFrame.

        :param df: DataFrame to check
        :param column: Column name to check
        """
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in DataFrame.")

    def sum(self, df: pd.DataFrame, columns: List[str], value: Union[int, float] = None):
        """
            Sum operation on specified column

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param value: Value to add with
        :return: Sum of the specified column
        """
        for column in columns:
            self.__check_column_exists(df, column)

        new_column_name = ''.join(columns) + '_sum'
        if value is not None:
            df[new_column_name] = df[columns].sum() + value
        else:
            df[new_column_name] = df[columns].sum(axis=1)

        return df[new_column_name]

    def subtraction(self, df: pd.DataFrame, columns: List[str], value: Union[int, float] = None) -> pd.Series:
        """
            Subtraction between two columns

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param value: Value to subtract with
        :return: Subtraction of the specified columns
        """
        for column in columns:
            self.__check_column_exists(df, column)

        if value is not None:
            return df[columns].sum() - value

        df['subtracted result'] = df[columns[0]] - df[columns[1]]
        return df['subtracted result']

    def multiplication(self, df: pd.DataFrame, columns: List[str], value: Union[int, float]):
        """
            Multiplication on number/numeric column with the given value

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param value: Value to multiply with
        :return: Multiplication of the specified column with the given value
        """
        for column in columns:
            self.__check_column_exists(df, column)

        new_column_name = ''.join(columns) + '_multiplied'
        if value is not None:
            df[new_column_name] = df[columns] * value
        else:
            df[new_column_name] = df[columns].prod(axis=1)

        return df[new_column_name]

    def division(self, df: pd.DataFrame, columns: List[str], value: Union[int, float]) -> pd.Series:
        """
            Division on number/numeric column with the given value

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param value: Value to divide with
        :return: Division of the specified column with the given value
        """
        for column in columns:
            self.__check_column_exists(df, column)

        if value == 0:
            raise ValueError("Division by zero is not allowed.")

        new_column_name = ''.join(columns) + '_divided'
        if value is not None:
            df[new_column_name] = df[columns[0]] / value
        return df[new_column_name]

    def execute(self, df: pd.DataFrame, metadata: dict) -> Union[pd.Series, float]:
        """
            Method to execute a math operation based on operation type and its arguments.

        :param df: DataFrame to perform the operation on
        :param metadata: Metadata containing operation type and its arguments
        :return: Result of the operation
        """
        value_mapper = {
            Operations.ADDITION: 'add_value',
            Operations.SUBTRACTION: 'subtract_value',
            Operations.MULTIPLICATION: 'multiply_value',
            Operations.DIVISION: 'divide_value'
        }

        operation_mapper = {
            Operations.ADDITION: self.sum,
            Operations.SUBTRACTION: self.subtraction,
            Operations.MULTIPLICATION: self.multiplication,
            Operations.DIVISION: self.division,
        }

        operation = metadata['operation']
        if operation not in operation_mapper:
            raise ValueError(f"Unknown operation: {operation}")

        columns = metadata.get('columns')
        method = operation_mapper[operation]
        return method(df, columns, metadata.get(value_mapper[operation]))
