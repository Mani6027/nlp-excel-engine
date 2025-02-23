class Operations:

    # available math operations
    ADDITION = 'addition'
    SUBTRACTION = 'subtraction'
    MULTIPLICATION = 'multiplication'
    DIVISION = 'division'

    # NLP operations
    SENTIMENT_ANALYSIS = 'sentiment_analysis'
    SUMMARIZATION = 'summarization'
    TEXT_CLASSIFICATION = 'text_classification'

    # Pivot and unpivot operations
    PIVOT_TABLE = 'pivot_table'
    UNPIVOT_TABLE = 'unpivot_table'

    # join operations
    OPERATION_JOIN = 'join'
    INNER_JOIN = 'inner_join'
    LEFT_JOIN = 'left_join'
    RIGHT_JOIN = 'right_join'
    FULL_OUTER_JOIN = 'full_outer_join'

    # date operations
    DATE_DIFFERENCE = 'date_difference'

    DF_JOIN_MAPPER = {
        INNER_JOIN: 'inner',
        LEFT_JOIN: 'left',
        RIGHT_JOIN: 'right',
        FULL_OUTER_JOIN: 'outer'
    }
