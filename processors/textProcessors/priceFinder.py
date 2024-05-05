import time, re
from word2number import w2n

class PriceMatch:
    def __init__(self):
        self.blacklist_file = "blacklist.txt"
        self.price_regex = r"\$\s*?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?(?!\%)"
        self.numeric_price_regex = r"\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?!\%)\b"
        self.reg_price_regex = r"\(REG\.\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\)"
        self.textual_price_regex = r"\b(\w+)\s(dollars|cents)\b"
        self.debounce_time = 0.5  # Time to wait before processing in seconds
        self.last_call_time = None

    async def find_price(self, text):
        current_time = time.time()

        # Debouncing: Check if we should delay processing
        if self.last_call_time and (current_time - self.last_call_time < self.debounce_time):
            #print("Waiting due to debouncing...")
            time.sleep(self.debounce_time - (current_time - self.last_call_time))
        
        self.last_call_time = time.time()  # Update last call time after processing

        #print("Initializing Price Match")
        # Initialize blacklists and valid prices list
        preceding_blacklist = ["when you spend at least", "Save", "clip"]
        following_blacklist = ["promotional credit", "in promotional item(s)", "in promotional items"]
        valid_prices = []

        # Load blacklist words and phrases from a file
        with open(self.blacklist_file, 'r') as file:
            current_list = None
            for line in file:
                line = line.strip()
                if line == "# Preceding Blacklist Keywords":
                    current_list = preceding_blacklist
                elif line == "# Following Blacklist Words":
                    current_list = following_blacklist
                elif line and current_list is not None:
                    current_list.append(line)

        # Find and process textual prices (e.g., "ten dollars", "five cents")
        found_textual_prices = re.findall(self.textual_price_regex, text, re.IGNORECASE)
        for number_word, currency in found_textual_prices:
            try:
                number = w2n.word_to_num(number_word)
                if currency.lower() == "dollars":
                    price = f"${number:.2f}"
                elif currency.lower() == "cents":
                    price = f"${number / 100:.2f}"
                valid_prices.append(price)
            except ValueError:
                # Skip if conversion fails (e.g., unrecognized number word)
                continue

        found_prices_with_sign = re.findall(self.price_regex, text)

        # Use prices with $ if found
        if found_prices_with_sign:
            for price in found_prices_with_sign:
                index = text.find(price)
                preceding_context = text[:index]
                following_context = text[index+len(price):]

                # Check against preceding blacklist
                preceding_invalid = any(phrase in preceding_context for phrase in preceding_blacklist)

                # Check against following blacklist
                following_invalid = any(phrase in following_context for phrase in following_blacklist)

                if not preceding_invalid and not following_invalid:
                    valid_prices.append(price)

        # Sort and determine deal and retail prices
        valid_prices.sort(key=lambda x: float(x.replace('$', '').replace(',', '').replace(' ', '')))
        deal_price = valid_prices[0] if valid_prices else None
        retail_price = valid_prices[-1] if len(valid_prices) > 1 else None

        if not valid_prices:
            print("No valid prices found in the text")

        return {
            'deal_price': deal_price,
            'retail_price': retail_price
        }
