import re

class PromoBuster:
    def __init__(self):
        self.whitelist_promo_F = ["promo code", "use code", "Use code: ", "coupon code", "with code", "with code:", "use code:", "use promo code:", "use promo code", "use Sales-aholic code:", "Use promo code "]  # Add phrases as needed
        self.whitelist_promo_A = []  
        self.blacklist_promo_F = ["no promo code"]  
        self.blacklist_promo_A = ["off", "gc", "coupon", "gift card", "MFC -"]
        self.promo_blacklist = ["NEEDED", "COUPON"]
        self.promo_regex = r"\b(?=[A-Z0-9]*[0-9])[A-Z0-9]{6,10}\b"

    async def find_promo_code(self, text):
        found_codes = set()  # Use a set to automatically handle duplicates

        # First, attempt to find codes that directly follow a whitelist phrase
        for phrase in self.whitelist_promo_F:
            pattern = re.compile(f'{phrase}\\s+([A-Za-z\\d]{{5,10}})', re.IGNORECASE)
            matches = pattern.findall(text)
            for code in matches:
                if await self.is_code_valid(code, text):
                    found_codes.add(code.upper())  # Convert to upper case for consistency and uniqueness

        # If no codes found directly after whitelist phrases, use the general regex
        if not found_codes:
            all_matches = re.findall(self.promo_regex, text)
            for code in all_matches:
                if await self.is_code_valid(code, text):
                    found_codes.add(code.upper())

        # Convert to list and add discount information if applicable
        codes_with_discounts = []
        for code in found_codes:
            discount = await self.extract_discount_from_code(code)
            if discount:
                codes_with_discounts.append((code, discount))
            else:
                codes_with_discounts.append((code, None))

        return codes_with_discounts if codes_with_discounts else []

    async def is_code_valid(self, code, text):
        """Checks if the found code is valid based on blacklist and surrounding context."""
        index = text.find(code)
        preceding_text = text[:index].split()[-1] if text[:index].split() else ""
        following_text = text[index+len(code):].split()[0] if text[index+len(code):].split() else ""
        
        # Validate against blacklists
        if any(phrase.lower() in preceding_text.lower() for phrase in self.blacklist_promo_F) or any(phrase.lower() in following_text.lower() for phrase in self.blacklist_promo_A):
            return False  # Code is blacklisted
        
        # Check against the promo_blacklist to ensure the code isn't a blacklisted word
        if code.upper() in (blacklisted.upper() for blacklisted in self.promo_blacklist):
            return False

        return True
    
    async def extract_discount_from_code(self, code):
        """
        Extracts the discount percentage from a promo code if it starts with two numbers followed by letters.
        Returns the discount percentage as an integer or None if the pattern doesn't match.
        """
        match = re.match(r'^(\d{2})[A-Za-z]', code)
        if match:
            return int(match.group(1))
        return None
