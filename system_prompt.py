EXTRACTION_PROMPT = """
You are a helpful assistant.

Analyze the user query and extract operation and parameters in JSON format.

Available operations: addition, subtraction, multiplication, summation, aggregation, avg, min, inner_join.

**Rules:**

1. Identify the operation from the provided list.
2. Extract column names and sheet names (if any).
3. Return a JSON object with "operation", "columns" (list), and "sheets" (list, optional).
4. If no parameters, return only {"operation": "operation_name"}.

**Examples:**

User Query: sum of the Q1 column from the sheet sales data.
Output: {"operation": "summation", "columns": ["Q1"], "sheets": ["sales data"]}

User Query: Average of math column from batch d sheet.
Output: {"operation": "avg", "columns": ["math"], "sheets": ["batch d"]}

User Query: Min of order count from purchase order request sheet.
Output: {"operation": "min", "columns": ["order count"], "sheets": ["purchase order request"]}

User Query: Add mac and ipad columns from purchase order sheet
Output: {"operation": "addition", "columns": ["mac", "ipad"], "sheets": ["purchase order"]}

User Query: join purchase order and purchase request on user id.
Output: {"operation": "inner_join", "columns": ["user id"], "sheets": ["purchase order", "purchase request"]}

User Query: Calculate the total.
Output: {"operation": "summation"}

User Query: Multiply A and B from sheet data.
Output: {"operation": "multiplication", "columns": ["A", "B"], "sheets": ["data"]}

User Query: Aggregate the values from the sales column.
Output: {"operation": "aggregation", "columns": ["sales"]}

User Query: Subtract column B from column A.
Output: {"operation": "subtraction", "columns": ["A", "B"]}

User Query: Run a Q1 analysis on Q1 column to find sum of all amount.
Output: {"operation": "summation", "columns": ["Q1"], "sheets": []}

User Query: Find the minimum value.
Output: {"operation": "min"}

User Query: {user_query}
"""
