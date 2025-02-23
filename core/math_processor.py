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

    def join(self, left_df: pd.DataFrame, right_df: pd.DataFrame,
             how: str, on: Union[str, List[str]]) -> pd.DataFrame:
        """
        Joins two DataFrames based on a key column or columns.

        :param left_df: The left DataFrame to join
        :param right_df: The right DataFrame to join
        :param how: Type of join to perform ('inner', 'left', 'right', 'outer')
        :param on: Column name(s) to join on
        :return: The resultant joined DataFrame
        """
        if not right_df:
            raise ValueError("Right DataFrame is required for join operation.")

        if isinstance(on, str):
            on = [on]

        for column in on:
            self.__check_column_exists(left_df, column)
            self.__check_column_exists(right_df, column)

        return pd.merge(left_df, right_df, how=how, on=on)

    def pivot(self, df: pd.DataFrame, index_col: str, value_col: str, aggfunc: str = 'sum') -> pd.DataFrame:
        """
        Creates a pivot table from the DataFrame

        :param df: DataFrame to perform the operation on
        :param index_col: Column(s) to use as rows in the pivot table
        :param value_col: Column to aggregate
        :param aggfunc: Aggregation function to use, default is 'sum'
        :return: A pivot table DataFrame
        """
        # Check if all columns exist
        for column in [index_col, value_col]:
            self.__check_column_exists(df, column)

        return pd.pivot_table(df, index=index_col, values=value_col, aggfunc=aggfunc)

    def unpivot(self, df: pd.DataFrame, id_vars: List[str],
                var_name: str = "Metric", value_name: str = "Value") -> pd.DataFrame:
        """
        Unpivots the DataFrame from wide to long format.

        :param df: DataFrame to perform the operation on
        :param id_vars: Column to use as identifier variables
        :param var_name: Column to unpivot
        :param value_name: Name of the new column to create
        :return: Unpivoted DataFrame
        """
        # Check if all columns exist
        for column in id_vars:
            self.__check_column_exists(df, column)

        return pd.melt(df, id_vars=id_vars, var_name=var_name, value_name=value_name)

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

        # Q: Need to handle the case where two columns are provided?
        if value is not None:
            df[new_column_name] = df[columns[0]] / value
            return df[new_column_name]

    def execute(self, df: pd.DataFrame, metadata: dict, right_df = None) -> Union[pd.DataFrame, pd.Series, float]:
        """
            Method to execute a math operation based on operation type and its arguments.

        :param df: DataFrame to perform the operation on
        :param metadata: Metadata containing operation type and its arguments
        :param right_df: Optional right DataFrame for join operations
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
            Operations.PIVOT_TABLE: self.pivot,
            Operations.UNPIVOT_TABLE: self.unpivot,
        }

        operation = metadata['operation']
        if operation not in operation_mapper:
            raise ValueError(f"Unknown operation: {operation}")

        columns = metadata.get('columns')
        method = operation_mapper[operation]

        if operation == Operations.PIVOT_TABLE:
            return self.pivot(df, metadata.get('index_column'),
                          metadata.get('values_column'), metadata.get('aggregation_function'))

        if operation == Operations.UNPIVOT_TABLE:
            return self.unpivot(df, metadata.get("id_vars"), metadata.get("var_name"), metadata.get("value_name"))

        if operation == Operations.OPERATION_JOIN:
            join_type = metadata.get("parameters", {}).get("join_type")
            on = metadata.get("parameters", {}).get("on")
            how = Operations.DF_JOIN_MAPPER.get(join_type)
            return self.join(df, right_df=right_df, how=how, on=on)
        return method(df, columns, metadata.get(value_mapper[operation]))
