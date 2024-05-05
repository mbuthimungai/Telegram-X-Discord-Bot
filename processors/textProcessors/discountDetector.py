import re


class DiscountDetective:
    def __init__(self):
        self.clip_keywords = ["clip", "clip the"] 
        self.sale_keywords = ["sale", "to", "extra", "Clearance hit"]
        self.discounts = []  # Stores tuples of (discount, preceding_word, following_word, tag)
        
    async def find_all_discounts(self, text):
        # Patterns to match regular, spaced, and worded discounts
        patterns = [
            r'(\b|^)(\d{1,3})\s*(\%|PERCENT)\s*(OFF)?(?=\s|$)',  # Regular
            r'(\b|^)(\d\s*\d*)\s*\%\s*(O\s*F\s*F)?',  # Spaced percentage, e.g., 5 0 %
            r'(\d\s*\d*)\s*P\s*E\s*R\s*C\s*E\s*N\s*T\s*(O\s*F\s*F)?'  # Worded with spaces
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                discount_raw = match.group(0)
                discount_normalized = re.sub(r'\s+', '', discount_raw).upper()

                if discount_normalized.endswith('%OFF'):
                    discount = discount_normalized.replace('%OFF', '% OFF')
                elif discount_normalized.endswith('%'):
                    discount = discount_normalized
                else:
                    discount = f"{discount_normalized} % OFF"

                # Call _add_discount for each found discount
                await self._add_discount(text, match, discount)

    async def _add_discount(self, text, match, discount):
        # Extract start and end positions of the discount number for context
        start, end = match.start(2), match.end(2)
        preceding_word = await self._get_preceding_word(start, text)
        following_word = await self._get_following_word(end, text)

        # Ensure the discount is not already recorded
        if not any(d[0] == discount for d in self.discounts):
            self.discounts.append([discount, preceding_word, following_word, None])

    async def _get_preceding_word(self, start, text):
        return text[:start].split()[-1] if text[:start].split() else ""

    async def _get_following_word(self, end, text):
        return text[end:].split()[0] if text[end:].split() else ""

    async def def_clip_discount(self):
        for d in self.discounts:
            if any(keyword in d[1] for keyword in self.clip_keywords):
                d[3] = 'clip_discount'
    
    async def def_total_discount(self):
        for d in self.discounts:
            if d[1] == '' and d[2] != '':  # No preceding word but has following word
                d[3] = 'total_discount'

    async def def_sale_discount(self):
        for d in self.discounts:
            # Check if the preceding word is one of the sale keywords
            if d[1].lower() in self.sale_keywords:
                d[3] = 'sale_discount'
                # print(f"Sale discount found and tagged: {d}")
    
    async def handle_unassigned_discounts(self):
        unhandled_discounts = [d for d in self.discounts if d[3] is None]
        # for d in unhandled_discounts:
        #     print(f"Unhandled discount: {d[0]}")
        # Optionally, assign a default tag or perform other actions
    
    async def process_text(self, text):
        await self.find_all_discounts(text)
        await self.def_clip_discount()
        await self.def_sale_discount()
        await self.def_total_discount()
        await self.handle_unassigned_discounts()
        return self.discounts
