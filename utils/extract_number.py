import re

async def extract_number(input_string):
    """
    Extracts the first numerical value from a string that may contain non-numeric characters.

    Args:
    - input_string (str): The string from which to extract the number.

    Returns:
    - float: The first floating-point number found in the string. Returns None if no number is found.
    """
    # Use regular expression to find numbers, including decimals
    match = re.search(r"[-+]?\d*\.\d+|\d+", input_string)
    if match:
        return float(match.group())
    else:
        return float(0)