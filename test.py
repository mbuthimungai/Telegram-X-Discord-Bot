import asyncio
import logging
import re
import sys
from playwright.async_api import async_playwright
from processors.textProcessors.textCleaner import TextCleaner
from processors.textProcessors.discountDetector import DiscountDetective
from processors.textProcessors.priceFinder import PriceMatch
from processors.textProcessors.promoBuster import PromoBuster

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
    content, urls = await link_res.scrape_facebook_post_content("https://www.facebook.com/groups/addictivedealsreloaded/permalink/1912513835845902/?mibextid=oFDknk&rdid=52wS8ajP60nyVjLh&share_url=https%3A%2F%2Fwww.facebook.com%2Fshare%2Fp%2F74umpr9cTBx7aiX2%2F%3Fmibextid%3DoFDknk")
    print(urls)
            
    discount_detective = DiscountDetective()
    content = '🚨🚨WAY DAY IS N0W L!VE🚨🚨 28" Griddle with Front Shelf and Cover $199.99 (REG. $299.99) https://go.sylikes.com/eMItnDFH3xzH Free Shipping On All Orders! [AD] MAY042024'
    category, cleaned_text = await text_cleaner.def_get_category_and_clean(content)
    cleaned_text = await text_cleaner.truncate_text_at_keywords(content, ["Toa maoni", "Comment"])
    

    discounts_data = await discount_detective.process_text(cleaned_text)
    
    prices_extracted = await price_match.find_price(cleaned_text)
    deal_price, retail_price = prices_extracted.get('deal_price'), prices_extracted.get('retail_price')
        
    promo_codes_discounts_extracted = await promo_buster.find_promo_code(cleaned_text)        
    promo_codes = [code for code, _ in promo_codes_discounts_extracted]        
    promo_discounts = {code: discount for code, discount in promo_codes_discounts_extracted if discount is not None}
    print(f"Deal Price: {deal_price}")
    print(f"Retail Price: {retail_price}")
    print(f"Promo discounts: {promo_codes_discounts_extracted}")
    print(f"Discount data: {discounts_data}")
    print(f"Promo discounts {promo_discounts}")
    print(f"Promo codes {promo_codes}")
    print("Content and URLs have been saved to facebook_post_content.txt")

if __name__ == "__main__":
    asyncio.run(main())
