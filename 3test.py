# import re

# def extract_number(input_string):
#     """
#     Extracts the first numerical value from a string that may contain non-numeric characters.

#     Args:
#     - input_string (str): The string from which to extract the number.

#     Returns:
#     - float: The first floating-point number found in the string. Returns None if no number is found.
#     """
#     # Use regular expression to find numbers, including decimals
#     match = re.search(r"[-+]?\d*\.\d+|\d+", input_string)
#     if match:
#         return float(match.group())
#     else:
#         return None
    
# print(extract_number('-30%'))



x = 10 % 3

if (x > 10):
    print(1)
elif (x > 5):
    print(2)
elif (x < 2):
    print(3)
else:
    print(4) 