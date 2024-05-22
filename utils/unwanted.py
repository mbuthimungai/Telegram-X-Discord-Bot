import re

async def filter_unwanted(words):
    # List of unwanted words
    unwanteds = ['C0UP0N', 'COUPON', 'C0UPON']
    
    # Regex pattern for dates in the format MAY012024
    date_pattern = re.compile(r'^[A-Z]{3}\d{2}\d{4}$')
    
    # Filter the list to remove unwanted words and dates
    filtered_words = [word for word in words if word not in unwanteds and not date_pattern.match(word)]
    
    return filtered_words

