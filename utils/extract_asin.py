import re

async def extract_asin(url: str) -> str:
    """
    Extracts and returns product asin from Amazon product ulrs
    """
    asin_regex = r'https?://www\.amazon\.com/(?:dp|gp/product)/([A-Z0-9]+)'
    asin = re.search(asin_regex, url).group(1)
    return asin