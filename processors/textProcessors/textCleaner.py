import re


class TextCleaner:
    def __init__(self):
        self.removal_keywords = ["ad", "[ad]", "Ad", "#ad", "ad#", "KICKASS", "REBELDEALZ", "MAMADEALS", "Buy on Amazon", "WALMART DEAL!", "WALMART DISCOUNT DEALS"]
        self.space_regex = r'\s{2,}'  # Remove excessive spacing
        # Regex pattern to match most emojis
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+", 
            flags=re.UNICODE)
        self.category_patterns = {
            "price_drop": [r"PRICE DROP", r"PR!CE DR0P", r"‼ P R ! C E D R 0 P ‼", r"‼PR!CE DROP‼", r'‼ P R ! C E D R 0 P ‼']
        }

    async def clean_text(self, text):
        for keyword in self.removal_keywords:
            # Use re.escape to safely escape any regex special characters in keywords/phrases
            pattern = re.escape(keyword)
            # Use re.sub() to replace the keyword/phrase with an empty string
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)  # Added IGNORECASE for case-insensitive matching
        # Remove brackets
        text = text.replace("[", '').replace("]", '')
        # Remove emojis
        text = self.emoji_pattern.sub(r'', text)
        # Remove excessive spacing
        text = re.sub(self.space_regex, ' ', text).strip()
        return text
    
    async def def_get_category_and_clean(self, text):
        category = None
        # Iterate over the category patterns to find and remove matches
        for cat, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    category = cat
                    # Remove the pattern from the text
                    text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                    break  # Stop searching if a match is found
            if category:  # Exit the loop early if a category has been assigned
                break
        # Further clean the text to remove any residual excessive spaces or symbols left after removal
        text = await self.clean_text(text)
        return category, text
        

    async def truncate_text_at_keywords(self, text, keywords):
        """
        Truncate the text at the first occurrence of any specified keywords.

        Args:
        text (str): The text to be truncated.
        keywords (list): A list of strings, each representing a keyword at which to truncate the text.

        Returns:
        str: The text truncated before the first keyword, if found. Full text if no keyword is found.
        """
        # Join the keywords into a single regex pattern with alternation
        pattern = re.compile('|'.join(re.escape(keyword) for keyword in keywords), re.IGNORECASE)

        # Search for the first occurrence of any keyword
        match = pattern.search(text)

        # If a match is found, truncate the text at the start of the matched word
        if match:
            return text[:match.start()].strip()
        else:
            # Return the full text if no keywords are found
            return text

