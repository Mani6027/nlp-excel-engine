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
