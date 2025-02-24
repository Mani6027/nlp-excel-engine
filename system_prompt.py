INITIAL_PROMPT= """
You are a helpful assistant. Here is metadata about the Excel file:

{excel_metadata}

Analyze the user query and extract the operation and parameters in a consistent JSON format.
"""

EXCEL_PARAM_EXTRACTION_PROMPT = """

## Available Operations (with concise examples)

**Math Operations**

- `addition` (e.g., `{"operation": "addition", "columns": ["Quantity", "Profit"], "sheets": ["Sales"], "parameters": {"add_value": 10}}`)
- `subtraction` (e.g., `{"operation": "subtraction", "columns": ["Revenue", "Customer Acquisition"], "sheets": ["Sales"], "parameters": {"subtract_value": 50}}`)
- `multiplication` (e.g., `{"operation": "multiplication", "columns": ["Quantity", "Revenue"], "sheets": ["Sales"], "parameters": {}}`)
- `division` (e.g., `{"operation": "division", "columns": ["Revenue", "Quantity"], "sheets": ["Sales"], "parameters": {}}`)
- `summation` (e.g., `{"operation": "summation", "columns": ["Revenue"], "sheets": ["Sales"], "parameters": {}}`)
- `aggregation` (e.g., `{"operation": "aggregation", "columns": ["Revenue"], "sheets": ["Sales"], "parameters": {"group_by": "Product"}}`)
- `avg` (e.g., `{"operation": "avg", "columns": ["Rating"], "sheets": ["Customer Reviews"], "parameters": {}}`)
- `min` (e.g., `{"operation": "min", "columns": ["Stock"], "sheets": ["Inventory"], "parameters": {}}`)
- `max` (e.g., `{"operation": "max", "columns": ["Revenue"], "sheets": ["Sales"], "parameters": {}}`)

**Join Operations**

- `inner_join` (e.g., `{"operation": "join", "columns": ["Item Code"], "sheets": ["Sales", "Inventory"], "parameters": {"join_type": "inner_join", "on": "Item Code"}}`)
- `left_join` (e.g., `{"operation": "join", "columns": ["Item Code"], "sheets": ["Sales", "Inventory"], "parameters": {"join_type": "left_join", "on": "Item Code"}}`)
- `right_join` (e.g., `{"operation": "join", "columns": ["Item Code"], "sheets": ["Sales", "Inventory"], "parameters": {"join_type": "right_join", "on": "Item Code"}}`)
- `full_outer_join` (e.g., `{"operation": "join", "columns": ["Item Code"], "sheets": ["Sales", "Inventory"], "parameters": {"join_type": "full_outer_join", "on": "Item Code"}}`)

**Pivot and Unpivot Operations**

- `pivot_table` (e.g., `{"operation": "pivot_table", "columns": ["Product", "Revenue"], "sheets": ["Sales"], "parameters": {"index_column": "Product", "values_column": "Revenue", "aggregation_function": "sum"}}`)
- `unpivot_table` (e.g., `{"operation": "unpivot_table", "columns": ["Product", "Revenue", "Quantity", "Date"], "sheets": ["Sales"], "parameters": {}}`)

**Date Operations**

- `extract_date_parts` (unit: `year`, `month`, `day`) (e.g., `{"operation": "extract_date_parts", "columns": ["Date"], "sheets": ["Sales"], "parameters": {"unit": "year"}}`)
- `date_difference` (unit: `days`, `months`, `years`) (e.g., `{"operation": "date_difference", "columns": ["Date", "Ship Date"], "sheets": ["Sales"], "parameters": {"unit": "days"}}`)

**NLP Operations (Unstructured Data Processing)**

- `sentiment_analysis` (e.g., `{"operation": "sentiment_analysis", "columns": ["Feedback"], "sheets": ["Customer Reviews"], "parameters": {"task": "sentiment_analysis", "language": "en", "output_column": "Sentiment"}}`)
- `summarization` (e.g., `{"operation": "summarization", "columns": ["Feedback"], "sheets": ["Customer Reviews"], "parameters": {"task": "summarization", "language": "en", "output_column": "Summary"}}`)
- `text_classification` (e.g., `{"operation": "text_classification", "columns": ["Feedback"], "sheets": ["Customer Reviews"], "parameters": {"task": "text_classification", "language": "en", "output_column": "Category"}}`)

## Rules for Extraction

1. **Identify the operation** from the available list.
2. **Extract column names and sheet names from the User Query**
    - **Column Extraction:**
        - Extract only **exactly matching column names** from the provided metadata.
        - Prioritize names mentioned inside **quoted text** (e.g., `"feedback"`).
    - **Sheet Extraction:**
        - Extract **explicitly mentioned sheet names** as stated.
        - Infer sheet names **only if contextually clear** (e.g., "Pivot sales data" → "Sales").
        - If no sheet name is mentioned or inferable, set `"sheets": []`.
3. **Ensure a structured and concise JSON output.**
"""

OBJ_PROMPT_V2 = """
<OBJECTIVE_AND_PERSONA>
You are a helpful assistant. Here is metadata about the Excel file:

{excel_metadata}

Analyze the user query and extract the operation and parameters in a JSON format.
</OBJECTIVE_AND_PERSONA>
"""

EXCEL_PARAM_EXTRACTION_PROMPT_V2 = """

<INSTRUCTIONS>
## Available Operations

**Math Operations**
- `summation`
- `subtraction` 
- `multiplication`
- `division`
- `aggregation`
- `avg`
- `min`
- `max`

**Join Operations**
- `inner_join`
- `left_join`
- `right_join`
- `full_outer_join`

**Pivot and Unpivot Operations**
- `pivot_table`
- `unpivot_table`

**Date Operations**
- `date_difference`

**NLP Operations (Unstructured Data Processing)**
- `sentiment_analysis`
- `summarization`
</INSTRUCTIONS>

<CONSTRAINTS>
## Rules for Extraction
1. **Identify the operation** from the available list.
2. **Extract column names and sheet names from the User Query**
    - **Column Extraction:**
        - Extract only **exactly matching column names** from the provided metadata.
        - Prioritize names mentioned inside **quoted text** (e.g., `"feedback"`).
    - **Sheet Extraction:**
        - Extract **explicitly mentioned sheet names** as stated.
        - Infer sheet names **only if contextually clear** (e.g., "Pivot sales data" → "Sales").
        - If no sheet name is mentioned or inferable, set `"sheets": []`.
3. **Ensure a structured and concise JSON output.**
</CONSTRAINTS>

<OUTPUT_FORMAT>
{
  "operation": "operation_name",
  "columns": ["column1", "column2", ...],
  "sheets": ["sheet1", "sheet2", ...],
  "parameters": {
    "parameter1": "value1",
    "parameter2": "value2",
    ...
  }
}
</OUTPUT_FORMAT>

<FEW_SHOT_EXAMPLES>
1. Example #1
Sample Excel Metadata:
Sheet Names: ["Sales", "Customer Reviews", "Inventory"]
Columns in "Sales": ["Product", "Revenue", "Quantity", "Date", "Customer Acquisition", "Profit"]

User Query: Find highest revenue

Output: {
      "operation": "max",
      "columns": ["Revenue"],
      "sheets": ["Sales"],
      "parameters": {}
    }

2. Example #2
Sample Excel Metadata:
Sheet Names: ["Project Timeline", "Resource Allocation", "Risk Assessment"]
Columns in "Project Timeline": ["Task ID", "Task Name", "Start Date", "End Date", "Assigned To", "Status"]

User Query: compute date difference between start and end date of each task

Output: {
      "operation": "date_difference",
      "columns": ["End Date", "Start Date"],
      "sheets": ["Project Timeline"],
      "parameters": {
        "unit": "days"
      }
    }

3. Example #3
Sheet Names: ["Employee Data", "Department Data"]
Columns in "Employee Data": ["Employee ID", "Employee Name", "Department ID", "Salary"]
Columns in "Department Data": ["Department ID", "Department Name", "Manager ID"]

User Query: join employee and department data
Output: {
      "operation": "join",
      "columns": ["Deparment ID"],
      "sheets": ["Employee Data", "Department Data"],
      "parameters": {
        "join_type": "inner_join"
        "on": "Department ID"
      }
    }


4. Example #4
Sheet Names: ["Employee List", "Payroll Data"]
Columns in "Payroll Data": ["Employee ID", "Salary", "Bonus"]

User Query: Unpivot the Payroll Data sheet while keeping Employee ID fixed, and convert salary and bonus columns into two new columns: Earnings Type and Amount
Output: {
    "operation": "unpivot_table",
    "columns": ["Salary", "Bonus"],
    "sheets": ["Payroll Data"],
    "parameters": {
        "id_vars": ["Employee ID"],
        "var_name": "Earnings Type",
        "value_name": "Amount"
    }
}

5. Example #5
Sheet Names: ["Employee List", "Payroll Data"]
Columns in "Payroll Data": ["Employee ID", "Salary", "Bonus"]

User Query: Pivot the Payroll Data sheet using Employee ID as the index and Salary as values, aggregating by sum.
Output: {
    "operation": "pivot_table",
    "columns": ["Salary"],  # Values to pivot
    "sheets": ["Payroll Data"],
    "parameters": {
        "index_column": "Employee ID",
        "value_column": "Salary",
        "aggfunc": "sum"
    }
}

6. Example #6
Sheet Names: ["Sales", "Customer Reviews", "Inventory"]
Columns in "Customer Reviews": ["Customer Name", "Feedback", "Rating"]

User Query: Analyze sentiment in the Feedback column of Customer Reviews, grouped by Rating
Output: {
    "operation": "sentiment_analysis",
    "columns": ["Feedback"],
    "sheets": ["Customer Reviews"],
    "parameters": {
        "task": "sentiment_analysis",
        "language": "en",
        "group_by": "Rating",
        "output_column": "Sentiment Score"
    }
}

</FEW_SHOT_EXAMPLES>
"""
