from typing import Union, List

import pandas as pd
from dateutil.relativedelta import relativedelta

from config import logger
from constants import Operations, ErrorCodes
from custom_exceptions import InvalidColumn, InvalidValue, InvalidOperation, InvalidInstruction


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
            raise InvalidColumn(
                message=f"Column '{column}' does not exist in DataFrame.",
                error_code=ErrorCodes.INVALID_COLUMN
            )

    @staticmethod
    def __calculate_dt_difference_in_months(df, column_start, column_end):
        df['Month_diff'] = df.apply(lambda row: relativedelta(row[column_end], row[column_start]).months, axis=1)
        return df['Month_diff']

    @staticmethod
    def __calculate_dt_difference_in_years(df, column_start, column_end):
        df['Year_diff'] = df.apply(lambda row: relativedelta(row[column_end], row[column_start]).years, axis=1)
        return df['Year_diff']

    def date_difference(self, df: pd.DataFrame, column_start: str, column_end: str, unit: str = 'days') -> pd.Series:
        """
        Calculate the difference between two date columns.

        :param df: DataFrame to perform the operation on
        :param column_start: Name of the start date column
        :param column_end: Name of the end date column
        :param unit: Time unit for the difference ('days', 'hours', 'minutes', etc.)
        :return: Series with the difference in the specified unit
        """
        # Ensure the date columns exist
        self.__check_column_exists(df, column_start)
        self.__check_column_exists(df, column_end)

        # Convert columns to datetime if not already
        start_dates = pd.to_datetime(df[column_start])
        end_dates = pd.to_datetime(df[column_end])

        if unit == 'days':
            df['Day_diff'] = (end_dates - start_dates).dt.days
            return df['Day_diff']
        elif unit == 'months':
            return self.__calculate_dt_difference_in_months(df, column_start, column_end)
        elif unit == 'years':
            return self.__calculate_dt_difference_in_years(df, column_start, column_end)
        raise InvalidValue(message=f"Invalid time unit: {unit}", error_code=ErrorCodes.INVALID_VALUE)

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
        if right_df is None:
            raise InvalidInstruction("Specify right sheet for join operation.", ErrorCodes.INVALID_INSTRUCTION)

        if isinstance(on, str):
            on = [on]

        missing_columns = [column for column in on if column not in left_df.columns or column not in right_df.columns]
        if missing_columns:
            raise InvalidColumn(
                f"Column(s) {', '.join(missing_columns)} do not exist in provided DataFrames.",
                error_code=ErrorCodes.INVALID_COLUMN
            )

        if how not in {'inner', 'left', 'right', 'outer'}:
            raise InvalidOperation(
                f"Please provide one of 'inner', 'left', 'right', or 'outer'.",
                error_code=ErrorCodes.INVALID_OPERATION
            )

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
        for column in [index_col, value_col]:
            self.__check_column_exists(df, column)

        valid_aggfuncs = {'sum', 'mean', 'max', 'min', 'count', 'prod'}
        if aggfunc not in valid_aggfuncs:
            raise InvalidOperation(f"Choose aggregation operations from: {', '.join(valid_aggfuncs)}.",
                                   error_code=ErrorCodes.INVALID_OPERATION)

        pivot_table = pd.pivot_table(df, index=index_col, values=value_col, aggfunc=aggfunc)
        return pivot_table.reset_index()

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
        num_columns = []
        for column in columns:
            self.__check_column_exists(df, column)
            if pd.api.types.is_numeric_dtype(df[column]):
                num_columns.append(column)
            else:
                logger.warning(f"Non-numeric column '{column}' included in sum operation. Ignoring it.")

        if len(num_columns) == 0:
            raise InvalidColumn(message="Provide at least one numeric column.", error_code=ErrorCodes.INVALID_COLUMN)

        new_column_name = ''.join(num_columns) + '_sum'
        df[new_column_name] = (df[num_columns].sum(axis=1)
                               if len(num_columns) > 1 else df[num_columns[0]]).astype(float)

        if value is not None:
            df[new_column_name] += value

        return df[new_column_name]

    def subtraction(self, df: pd.DataFrame, columns: List[str], value: Union[int, float] = None) -> pd.Series:
        """
            Subtraction between two columns

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param value: Value to subtract with
        :return: Subtraction of the specified columns
        """
        if not columns:
            raise InvalidInstruction(message="Please specify column name to subtract.",
                                     error_code=ErrorCodes.INVALID_INSTRUCTION)

        if len(columns) > 2:
            raise InvalidInstruction(message="Too many columns provided for subtraction. Max 2 allowed.",
                                     error_code=ErrorCodes.OPERATION_NOT_SUPPORTED)

        for column in columns:
            self.__check_column_exists(df, column)
            if not pd.api.types.is_numeric_dtype(df[column]):
                # Can we handle this case like sum operation?
                raise InvalidColumn(message=f"Non-numeric column '{column}' cannot be used for subtraction.",
                                    error_code=ErrorCodes.INVALID_COLUMN)

        if len(columns) == 1 and value is not None:
            new_column_name = f"{columns[0]}_subtracted_by_{value}"
            df[new_column_name] = df[columns[0]] - value
        elif len(columns) == 2 and value is None:
            new_column_name = f"{columns[0]}_minus_{columns[1]}"
            df[new_column_name] = df[columns[0]] - df[columns[1]]
        else:
            raise InvalidValue(
                error_code=ErrorCodes.INVALID_INSTRUCTION,
                message="Invalid parameters for subtraction. Provide either one column and a value, or two columns."
            )

        return df[new_column_name]

    def multiplication(self, df: pd.DataFrame, columns: List[str], value: Union[int, float] = None):
        """
            Multiplication on number/numeric column with the given value

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param value: Value to multiply with
        :return: Multiplication of the specified column with the given value
        """
        if not columns:
            raise InvalidInstruction(message="Please specify column name to multiply.",
                                     error_code=ErrorCodes.INVALID_INSTRUCTION)

        for column in columns:
            self.__check_column_exists(df, column)
            if not pd.api.types.is_numeric_dtype(df[column]):
                raise InvalidColumn(message=f"Column '{column}' is not numeric and cannot be used for multiplication.",
                                    error_code=ErrorCodes.OPERATION_NOT_SUPPORTED)

        if value is not None:
            new_column_name = '_and_'.join(columns) + f'_multiplied_by_{value}'
            df[new_column_name] = df[columns].prod(axis=1) * value if len(columns) > 1 else df[columns[0]] * value
        else:
            if len(columns) < 2:
                raise InvalidInstruction(
                    message="At least two columns must be specified for element-wise multiplication.",
                    error_code=ErrorCodes.INVALID_INSTRUCTION)
            new_column_name = '_and_'.join(columns)
            df[new_column_name] = df[columns].prod(axis=1)

        return df[new_column_name]

    def division(self, df: pd.DataFrame, columns: List[str], value: Union[int, float] = None) -> pd.Series:
        """
            Division on number/numeric column with the given value

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param value: Value to divide with
        :return: Division of the specified column with the given value
        """
        if not columns:
            raise InvalidInstruction("No columns specified for division.", ErrorCodes.INVALID_INSTRUCTION)

        if len(columns) > 2:
            raise InvalidInstruction("Too many columns specified for division. Maximum two allowed.",
                                     ErrorCodes.INVALID_INSTRUCTION)
        for column in columns:
            self.__check_column_exists(df, column)
            if not pd.api.types.is_numeric_dtype(df[column]):
                raise InvalidColumn(f"Column '{column}' is not numeric and cannot be used for division.",
                                    ErrorCodes.OPERATION_NOT_SUPPORTED)
        new_column_name = None
        if len(columns) == 1:
            if value is None:
                raise InvalidValue("A numeric value must be provided for division when only one column specified.",
                                   ErrorCodes.INVALID_OPERATION)
            if value == 0:
                raise InvalidValue("Cannot divide by zero.", ErrorCodes.INVALID_OPERATION)
            new_column_name = f"{columns[0]}_divided_by_{value}"
            df[new_column_name] = df[columns[0]] / value
        elif len(columns) == 2:
            if value is not None:
                raise InvalidInstruction(
                    "Only columns should be specified for element-wise division, not a third value.",
                    ErrorCodes.INVALID_OPERATION)
            new_column_name = f"{columns[0]}_divided_by_{columns[1]}"
            df[new_column_name] = df[columns[0]] / df[columns[1]]

        return df[new_column_name]

    def avg(self, df: pd.DataFrame, columns: List[str], group_by: str = None):
        """
            Average operation on specified column

        :param df: DataFrame to perform the operation on
        :param columns: List of column names to perform the operation on
        :param group_by: Column to group by
        :return: Average of the specified column
        """
        if not columns or len(columns) > 1:
            raise InvalidInstruction("Exactly one column must be specified for the average calculation.",
                                     ErrorCodes.INVALID_INSTRUCTION)
        column = columns[0]
        self.__check_column_exists(df, column)
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise InvalidColumn(f"Column '{column}' is not numeric and cannot be used for averaging.",
                                ErrorCodes.OPERATION_NOT_SUPPORTED)
        if group_by:
            self.__check_column_exists(df, group_by)
            result = df.groupby(group_by)[column].mean().reset_index(name=f'avg_of_{column}')
        else:
            avg_value = df[column].mean()
            result = pd.DataFrame({f'avg_of_{column}': [avg_value]})
        return result

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
            Operations.SUMMATION: 'sum_value',
            Operations.SUBTRACTION: 'subtract_value',
            Operations.MULTIPLICATION: 'multiply_value',
            Operations.DIVISION: 'divide_value'
        }

        operation_mapper = {
            Operations.ADDITION: self.sum, # alias for summation
            Operations.SUMMATION: self.sum,
            Operations.SUBTRACTION: self.subtraction,
            Operations.MULTIPLICATION: self.multiplication,
            Operations.DIVISION: self.division,
            Operations.PIVOT_TABLE: self.pivot,
            Operations.UNPIVOT_TABLE: self.unpivot,
            Operations.AVG: self.avg
        }

        operation = metadata['operation']
        if operation not in operation_mapper:
            raise InvalidOperation(message=f"Unknown operation: {operation}", error_code=ErrorCodes.INVALID_OPERATION)

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
        if operation == Operations.DATE_DIFFERENCE:
            self.date_difference(df, metadata.get('columns')[0], metadata.get('columns')[1], metadata.get('parameters').get('unit'))
        if operation == Operations.AVG:
            return self.avg(df, metadata.get('columns'), metadata.get('parameters', {}).get('group_by'))
        if operation == Operations.SUMMATION:
            return self.sum(df, metadata.get('columns'), metadata.get('parameters', {}).get('sum_value'))
        return method(df, columns, metadata.get(value_mapper.get(operation)))
