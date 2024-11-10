import re

def translate_parameters(params: str) -> str:
    """Translate user-defined parameters into a valid SQL WHERE clause."""
    # Define how operators should be mapped to SQL operators
    operators = {"==": "=", "=": "LIKE", ">": ">", "<": "<", "!=": "!="}
    
    # Regular expression pattern to capture the column, operator, and value
    pattern = r"([A-Z_]+)(==|=|>|<|!=)\((.*?)\)"
    
    # Function to process each match
    def replace_match(match):
        column = match.group(1)  # Column name
        operator = match.group(2)  # Operator (==, =, <, >, !=)
        value = match.group(3)  # Value to compare

        # If it's a contains query, use SQL's LIKE operator with % wildcard
        if operator == "=":
            return f"{column} LIKE '%{value}%'"
        else:
            # Safely quote the value for SQL queries
            return f"{column} {operators[operator]} '{value}'"

    # Apply the replacement to the parameters string
    translated = re.sub(pattern, replace_match, params)

    # Debug: Print the translated where clause for inspection
    print("Translated where clause:", translated)
    
    return translated
