import unittest

import pandas as pd

from core.math_processor import MathOperationExecutor
from custom_exceptions import InvalidColumn, InvalidValue, InvalidOperation, InvalidInstruction
from tests import BaseTest


class TestDateDifferenceMethod(BaseTest):
    """
        Test cases for date difference calculation and validation
    """
    def setUp(self):
        # Prepare a sample DataFrame for testing
        self.df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8],
            'StartDate': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']),
            'EndDate': pd.to_datetime(['2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01'])
        })
        self.executor = MathOperationExecutor()

    def test_date_difference_days(self):
        result = self.executor.date_difference(self.df, 'StartDate', 'EndDate', 'days')
        expected = pd.Series([31, 28, 31, 30], name='Day_diff')
        pd.testing.assert_series_equal(result, expected)

    def test_date_difference_months(self):
        result = self.executor.date_difference(self.df, 'StartDate', 'EndDate', 'months')
        expected = pd.Series([1, 1, 1, 1], name='Month_diff')
        pd.testing.assert_series_equal(result, expected)

    def test_date_difference_years(self):
        result = self.executor.date_difference(self.df, 'StartDate', 'EndDate', 'years')
        expected = pd.Series([0, 0, 0, 0], name='Year_diff')
        pd.testing.assert_series_equal(result, expected)

    def test_date_difference_invalid_unit(self):
        with self.assertRaises(InvalidValue):
            self.executor.date_difference(self.df, 'StartDate', 'EndDate', 'invalid_unit')

    def test_date_difference_invalid_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.date_difference(self.df, 'NonExistent', 'EndDate', 'days')

    def test_date_difference_with_empty_values_in_column(self):
        self.df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8],
            'StartDate': pd.to_datetime(['', '2023-02-01', '2023-03-01', '2023-04-01']),
            'EndDate': pd.to_datetime(['2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01'])
        })
        result = self.executor.date_difference(self.df, 'StartDate', 'EndDate', 'days')
        expected = pd.Series([None, 28, 31, 30], name='Day_diff')
        pd.testing.assert_series_equal(result, expected)


class TestSumMethod(BaseTest):
    def setUp(self):
        # Prepare a sample DataFrame for testing
        self.df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8],
            'StartDate': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']),
            'EndDate': pd.to_datetime(['2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01'])
        })
        self.executor = MathOperationExecutor()

    def test_sum(self):
        """Test that it sums the numeric columns."""
        result = self.executor.sum(self.df, ['A', 'B'])
        expected = pd.Series([6.0, 8.0, 10.0, 12.0], name='AB_sum')
        pd.testing.assert_series_equal(result, expected)

    def test_sum_with_non_numeric_column(self):
        """Test that it ignores non-numeric columns."""
        self.df['C'] = ['a', 'b', 'c', 'd']
        result = self.executor.sum(self.df, ['A', 'B', 'C'])
        expected = pd.Series([6.0, 8.0, 10.0, 12.0], name='AB_sum')
        pd.testing.assert_series_equal(result, expected)

    def test_sum_with_non_existent_column(self):
        """Test that it raises an error if a non-existent column is provided."""
        with self.assertRaises(InvalidColumn):
            self.executor.sum(self.df, ['A', 'B', 'C'])

    def test_sum_with_empty_values_in_column(self):
        """Test that it ignores empty values in the column."""
        self.df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [None, None, None, None],
            'C': [None, None, None, None]
        })
        result = self.executor.sum(self.df, ['A', 'B', 'C'])
        expected = pd.Series([1.0, 2.0, 3.0, 4.0], name='A_sum')
        pd.testing.assert_series_equal(result, expected)

    def test_sum_with_column_and_constant(self):
        """Test that it sums the numeric columns with a constant."""
        result = self.executor.sum(self.df, ['A', 'B'], 2)
        expected = pd.Series([8.0, 10.0, 12.0, 14.0], name='AB_sum')
        pd.testing.assert_series_equal(result, expected)

    def test_sum_with_one_column_and_value(self):
        """Test that it sums the numeric column with a constant."""
        result = self.executor.sum(self.df, ['A'], 2)
        expected = pd.Series([3.0, 4.0, 5.0, 6.0], name='A_sum')
        pd.testing.assert_series_equal(result, expected)

    def test_sum_without_columns(self):
        """Test that it raises an error if no columns are provided."""
        with self.assertRaises(InvalidColumn):
            self.executor.sum(self.df, [], None)

class TestSubtractionMethod(BaseTest):
    def setUp(self):
        self.executor = MathOperationExecutor()
        self.df = pd.DataFrame({
            'Num1': [10, 20, 30],
            'Num2': [1, 2, 3],
            'NonNumeric': ['a', 'b', 'c']
        })

    def test_subtract_two_numeric_columns(self):
        result = self.executor.subtraction(self.df, ['Num1', 'Num2'])
        expected = pd.Series([9, 18, 27], name='Num1_minus_Num2')
        pd.testing.assert_series_equal(result, expected)

    def test_subtract_value_from_column(self):
        result = self.executor.subtraction(self.df, ['Num1'], value=5)
        expected = pd.Series([5, 15, 25], name='Num1_subtracted_by_5')
        pd.testing.assert_series_equal(result, expected)

    def test_subtract_with_non_numeric_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.subtraction(self.df, ['Num1', 'NonNumeric'])

    def test_subtract_with_too_many_columns(self):
        with self.assertRaises(InvalidInstruction):
            self.executor.subtraction(self.df, ['Num1', 'Num2', 'NonNumeric'])

    def test_subtraction_with_no_columns(self):
        with self.assertRaises(InvalidInstruction):
            self.executor.subtraction(self.df, [])

    def test_subtract_two_columns_and_value(self):
        # Checking misuse by passing two columns and a value
        with self.assertRaises(InvalidValue):
            self.executor.subtraction(self.df, ['Num1', 'Num2'], value=2)

    def test_subtract_nonexistent_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.subtraction(self.df, ['Num1', 'Unknown'])


class TestMultiplicationMethod(BaseTest):
    def setUp(self):
        self.executor = MathOperationExecutor()
        self.df = pd.DataFrame({
            'A': [2, 4, 8],
            'B': [1, 3, 5],
            'C': [10, 20, 30],
            'NonNumeric': ['x', 'y', 'z']
        })

    def test_multiplication_single_column_by_constant(self):
        result = self.executor.multiplication(self.df, ['A'], 5)
        expected = pd.Series([10, 20, 40], name='A_multiplied_by_5')
        pd.testing.assert_series_equal(result, expected)

    def test_multiplication_multiple_columns_by_constant(self):
        result = self.executor.multiplication(self.df, ['A', 'B'], 2)
        expected = pd.Series([4, 24, 80], name='A_and_B_multiplied_by_2')  # Calculated as (A*B)*2
        pd.testing.assert_series_equal(result, expected)

    def test_element_wise_multiplication(self):
        # Multiplying values across columns element-wise
        result = self.executor.multiplication(self.df, ['A', 'C'])
        expected = pd.Series([20, 80, 240], name='A_and_C')  # Calculated as A*C
        pd.testing.assert_series_equal(result, expected)

    def test_error_on_non_numeric_multiplication(self):
        with self.assertRaises(InvalidColumn):
            self.executor.multiplication(self.df, ['A', 'NonNumeric'], 3)

    def test_error_on_nonexistent_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.multiplication(self.df, ['A', 'D'], 3)

    def test_error_no_columns_provided(self):
        with self.assertRaises(InvalidInstruction):
            self.executor.multiplication(self.df, [])

    def test_error_single_column_no_value(self):
        with self.assertRaises(InvalidInstruction):
            self.executor.multiplication(self.df, ['A'])

class TestDivisionMethod(BaseTest):
    def setUp(self):
        self.df = pd.DataFrame({
            'A': [10, 20, 30],
            'B': [2, 5, 10],
            'C': [0, 1, 0],  # To test division by zero scenario
            'NonNumeric': ['a', 'b', 'c']
        })
        self.executor = MathOperationExecutor()

    def test_divide_column_by_constant(self):
        result = self.executor.division(self.df, ['A'], 2)
        expected = pd.Series([5.0, 10.0, 15.0], name='A_divided_by_2')
        pd.testing.assert_series_equal(result, expected)

    def test_element_wise_division(self):
        result = self.executor.division(self.df, ['A', 'B'])
        expected = pd.Series([5.0, 4.0, 3.0], name='A_divided_by_B')
        pd.testing.assert_series_equal(result, expected)

    def test_division_by_zero(self):
        with self.assertRaises(InvalidValue):
            self.executor.division(self.df, ['A'], 0)

    def test_invalid_column_type_division(self):
        with self.assertRaises(InvalidColumn):
            self.executor.division(self.df, ['NonNumeric'], 3)

    def test_invalid_numbers_of_columns(self):
        with self.assertRaises(InvalidInstruction):
            self.executor.division(self.df, ['A', 'B', 'C'])

    def test_missing_value_with_single_column(self):
        with self.assertRaises(InvalidValue):
            self.executor.division(self.df, ['A'])

    def test_provide_value_with_two_columns(self):
        with self.assertRaises(InvalidInstruction):
            self.executor.division(self.df, ['A', 'B'], 3)


class TestAvgMethod(BaseTest):
    def setUp(self):
        self.executor = MathOperationExecutor()
        self.data = {
            'Region': ['East', 'West', 'East', 'West'],
            'Sales': [100, 200, 300, 400],
            'Month': ['Jan', 'Jan', 'Feb', 'Feb']
        }
        self.df = pd.DataFrame(self.data)

    def test_avg_on_numeric_column(self):
        result = self.executor.avg(self.df, columns=['Sales'], group_by='Region')
        expected_data = {
            'Region': ['East', 'West'],
            'avg_of_Sales': [200.0, 300.0]
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result, expected_df)

    def test_avg_with_missing_values(self):
        self.df.loc[2, 'Sales'] = pd.NA
        result = self.executor.avg(self.df, columns=['Sales'], group_by='Month')
        expected_data = {
            'Month': ['Feb', 'Jan'],
            'avg_of_Sales': [400.0, 150.0]
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result, expected_df)

    def test_avg_with_non_numeric_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.avg(self.df, columns=['Region'], group_by='Month')

    def test_avg_nonexistent_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.avg(self.df, columns=['Nonexistent'], group_by='Region')

    def test_avg_without_group_by(self):
        result = self.executor.avg(self.df, columns=['Sales'])
        expected_data = {'avg_of_Sales': [250.0]}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result, expected_df)


class TestPivotMethod(BaseTest):
    def setUp(self):
        self.executor = MathOperationExecutor()
        self.data = {
            'Category': ['A', 'A', 'B', 'B', 'C'],
            'Values': [100, 200, 150, 250, 300],
            'Count': [1, 1, 1, 2, 1]
        }
        self.df = pd.DataFrame(self.data)

    def test_pivot_sum(self):
        result = self.executor.pivot(self.df, index_col='Category', value_col='Values', aggfunc='sum')
        expected_data = {
            'Category': ['A', 'B', 'C'],
            'Values': [300, 400, 300]
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result, expected_df.reset_index(drop=True))

    def test_pivot_mean(self):
        result = self.executor.pivot(self.df, index_col='Category', value_col='Values', aggfunc='mean')
        expected_data = {
            'Category': ['A', 'B', 'C'],
            'Values': [150.0, 200.0, 300.0]
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result, expected_df.reset_index(drop=True))

    def test_pivot_with_nonexistent_index_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.pivot(self.df, index_col='Nonexistent', value_col='Values')

    def test_pivot_with_nonexistent_value_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.pivot(self.df, index_col='Category', value_col='Nonexistent')

    def test_pivot_with_invalid_aggfunc(self):
        with self.assertRaises(InvalidOperation):
            self.executor.pivot(self.df, index_col='Category', value_col='Values', aggfunc='invalid_func')

    def test_pivot_with_empty_dataframe(self):
        empty_df = pd.DataFrame(columns=['Category', 'Values'])
        result = self.executor.pivot(empty_df, index_col='Category', value_col='Values', aggfunc='sum')
        expected_df = pd.DataFrame(columns=['Category'])
        pd.testing.assert_frame_equal(result, expected_df)

class TestJoinMethod(BaseTest):
    def setUp(self):
        self.executor = MathOperationExecutor()
        self.left_df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30]
        })
        self.right_df = pd.DataFrame({
            'id': [2, 3, 4],
            'description': ['twenty', 'thirty', 'forty']
        })

    def test_join_inner(self):
        result_df = self.executor.join(self.left_df, self.right_df, 'inner', 'id')
        expected_df = pd.DataFrame({
            'id': [2, 3],
            'value': [20, 30],
            'description': ['twenty', 'thirty']
        })
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_join_left(self):
        result_df = self.executor.join(self.left_df, self.right_df, 'left', 'id')
        expected_df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30],
            'description': [None, 'twenty', 'thirty']
        })
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_join_with_nonexistent_columns(self):
        with self.assertRaises(InvalidColumn):
            self.executor.join(self.left_df, self.right_df, 'inner', 'nonexistent_column')

    def test_join_with_none_dataframe(self):
        with self.assertRaises(InvalidInstruction):
            self.executor.join(self.left_df, None, 'inner', 'id')

    def test_join_with_invalid_join_type(self):
        with self.assertRaises(InvalidOperation):
            self.executor.join(self.left_df, self.right_df, 'invalid_join_type', 'id')

    def test_join_multiple_columns(self):
        extended_left_df = self.left_df.copy()
        extended_left_df['extra'] = ['a', 'b', 'c']
        extended_right_df = self.right_df.copy()
        extended_right_df['extra'] = ['b', 'c', 'd']
        result_df = self.executor.join(extended_left_df, extended_right_df, 'inner', ['id', 'extra'])
        expected_df = pd.DataFrame({
            'id': [2, 3],
            'value': [20, 30],
            'extra': ['b', 'c'],
            'description': ['twenty','thirty']
        })
        pd.testing.assert_frame_equal(result_df, expected_df)


class TestMathOperationExecutor(unittest.TestCase):
    def setUp(self):
        # Prepare a sample DataFrame for testing
        self.df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8],
            'StartDate': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']),
            'EndDate': pd.to_datetime(['2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01'])
        })
        self.executor = MathOperationExecutor()

    def test_division(self):
        result = self.executor.division(self.df, ['B'], 2)
        expected = pd.Series([2.5, 3.0, 3.5, 4.0], name='B_divided')
        pd.testing.assert_series_equal(result, expected)

    def test_avg(self):
        result = self.executor.avg(self.df, ['A'])
        expected = pd.Series([2.5, 2.5, 2.5, 2.5], name='avg_of_A')
        pd.testing.assert_series_equal(result, expected)

    def test_invalid_column(self):
        with self.assertRaises(InvalidColumn):
            self.executor.sum(self.df, ['NonExistent'])

    def test_division_by_zero(self):
        with self.assertRaises(InvalidValue):
            self.executor.division(self.df, ['A'], 0)

    def test_invalid_operation(self):
        with self.assertRaises(InvalidOperation):
            self.executor.execute(self.df, {'operation': 'INVALID_OPERATION'})
