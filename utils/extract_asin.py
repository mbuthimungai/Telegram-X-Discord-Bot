import re

async def extract_asin(url: str) -> str:
    """
    Extracts and returns product asin from Amazon product URLs.
    """
    asin_regex = r'https?://www\.amazon\.com/(?:.*/)?(?:dp|gp/product)/([A-Z0-9]+)'
    match = re.search(asin_regex, url)
    if match:
        asin = match.group(1)
        return asin
    else:
        return None