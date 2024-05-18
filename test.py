import asyncio
import logging
import re
import sys
from playwright.async_api import async_playwright
from processors.textProcessors.textCleaner import TextCleaner
from processors.textProcessors.discountDetector import DiscountDetective
from processors.textProcessors.priceFinder import PriceMatch
from processors.textProcessors.promoBuster import PromoBuster
from utils.extract_number import extract_number

text_cleaner = TextCleaner()
price_match = PriceMatch()
promo_buster = PromoBuster()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

sys.dont_write_bytecode = True
class LinkResolver:
    def __init__(self):
        self.ignore_list = [
            'www.amazon.com', 'www.instagram.com', 'http://glitchndealz.com',
            'https://freebieflow.com/', 'https://www.woot.com/?ref=',
            'https://www.edealinfo.com', "http://thefreebieguy.com/"
        ]
        self.endpoint_list = [
            'https://www.amazon.com/dp/', 'https://www.amazon.com/gp/',
            'https://www.walmart.com/ip/', 'https://www.amazon.com/promocode/',
            'https://tools.woot.com', 'https://www.bestbuy.com',
            'https://www.woot.com/', 'https://www.kohls.com/product/',
            'https://www.macys.com/shop/'
        ]
        self.retry_attempts = 3 

    async def scrape_facebook_post_content(self, facebook_url):
        content = ""
        extracted_links = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    await page.goto(facebook_url, timeout=60000)
                    await page.wait_for_load_state('networkidle', timeout=60000)
                    content = await page.evaluate('() => document.body.innerText')                    
                    # Extract URLs from the content using regex
                    urls = re.findall(r'https?://[^\s]+', content)
                    extracted_links.extend(urls)
                    
                except asyncio.TimeoutError:
                    print("Page load timed out. Attempting to extract available content...")
                except Exception as e:
                    print(f"Error navigating to page: {e}")
                finally:
                    await context.close()
                    await browser.close()

                # Save the content and extracted URLs to a text file
                with open("facebook_post_content.txt", "w", encoding="utf-8") as file:
                    file.write(content + "\n\nExtracted URLs:\n" + "\n".join(extracted_links))

        except Exception as e:
            print(f"Error scraping Facebook post content: {e}")

        return content, extracted_links


link_res = LinkResolver()

async def main():
    # content, urls = await link_res.scrape_facebook_post_content("https://www.facebook.com/share/p/7Yre1N7J7znSEAxd/?mibextid=oFDknk")
    # print(urls)
            
    discount_detective = DiscountDetective()
    content = '''🔥$13.99 for Nightstand with Charging Station and Dimmable LED Lights
Clip the Extra $10 off Coupon & use Sales-aholic code: X9MQKMP5 #ad'''
    category, cleaned_text = await text_cleaner.def_get_category_and_clean(content)
    cleaned_text = await text_cleaner.truncate_text_at_keywords(content, ["Toa maoni", "Comment"])
    

    discount_data = await discount_detective.process_text(cleaned_text)
    
    prices_extracted = await price_match.find_price(cleaned_text)
    deal_price, retail_price = prices_extracted.get('deal_price'), prices_extracted.get('retail_price')
        
    promo_codes_discounts_extracted = await promo_buster.find_promo_code(cleaned_text)        
    promo_codes = [code for code, _ in promo_codes_discounts_extracted]        
    promo_discounts = {code: discount for code, discount in promo_codes_discounts_extracted if discount is not None}
    total_discount = 0
    promo_disc = 0

    # Extract discount from promo code if available
    if promo_codes and promo_codes[0][:2]:
        promo_disc = await extract_number(promo_codes[0][:2]) or 0

    # Calculate total discount based on available data
    if discount_data and discount_data[0]:
        disc = await extract_number(discount_data[0][0])
        if promo_codes:
            total_discount = promo_disc + disc
        else:
            total_discount = disc
    elif promo_codes:  # Fallback to promo code discount if only promo codes are provided
        total_discount = promo_disc
    print(f"Deal Price: {deal_price}")
    print(f"Retail Price: {retail_price}")
    print(f"Promo discounts: {promo_codes_discounts_extracted}")
    print(f"Discount data: {discount_data}")
    print(f"Promo discounts {promo_discounts}")
    print(f"Promo codes {promo_codes}")
    print(f"Total discount: {total_discount}")
    print("Content and URLs have been saved to facebook_post_content.txt")

if __name__ == "__main__":
    asyncio.run(main())
