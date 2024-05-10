from processors.textProcessors.textCleaner import TextCleaner
from processors.textProcessors.priceFinder import PriceMatch
from processors.textProcessors.promoBuster import PromoBuster
from processors.textProcessors.discountDetector import DiscountDetective

class TextAnalysis:
    def __init__(self):
        # Initialize components if not provided
        self.text_cleaner = TextCleaner()
        self.price_match =  PriceMatch()
        self.promo_buster = PromoBuster()
        self.discount_detective = DiscountDetective()

    async def analyze_text(self, text):
        # Step 1: Clean text and get category
        category, cleaned_text = await self.text_cleaner.def_get_category_and_clean(text)

        # Step 2: Find prices in cleaned text
        prices = await self.price_match.find_price(cleaned_text)
        deal_price = prices.get('deal_price')
        retail_price = prices.get('retail_price')

        # Step 3: Detect promo codes and determine promo status
        is_promo_only = False
        is_no_promo_needed = False
        promo_codes_discounts = await self.promo_buster.find_promo_code(cleaned_text)
        
        # Check if original text contains any of the detected promo codes
        if text in [code for code, _ in promo_codes_discounts]:
            is_promo_only = True
        
        # Check for explicit no promo code needed in text
        if "no promo code needed" in text.lower():
            is_no_promo_needed = True

        # Step 4: Process text for any additional discounts
        discounts = await self.discount_detective.process_text(cleaned_text)

        # Output all relevant information
        return {
            "category": category,
            "cleaned_text": cleaned_text,
            "deal_price": deal_price,
            "retail_price": retail_price,
            "promo_codes_discounts": promo_codes_discounts,
            "is_promo_only": is_promo_only,
            "is_no_promo_needed": is_no_promo_needed,
            "discounts": discounts
        }
