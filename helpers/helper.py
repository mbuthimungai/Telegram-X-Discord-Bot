from utils.logger import configure_logger
from senders.discordSender.sendMessages import DiscordSender
from helpers.amazonHelper import getDataByAsinSearch, get_product_data, skip_scrape
from processors.textProcessors.textCleaner import TextCleaner
from processors.textProcessors.priceFinder import PriceMatch
from processors.textProcessors.promoBuster import PromoBuster
from processors.textProcessors.discountDetector import DiscountDetective
from processors.linkProcessors.linkResolvers import LinkResolver
from processors.linkProcessors.linkDressers import LinkDresser



class Helper:
    def __init__(self, message_data: dict, discord_sender: DiscordSender) -> None:
        self.logger = configure_logger(__name__)        
        self.discord_sender = discord_sender
        self.link_resolver = LinkResolver()
        self.link_dresser = LinkDresser()
        self.text_cleaner = TextCleaner()
        self.price_match = PriceMatch()
        self.promo_buster = PromoBuster()
        self.discount_detective = DiscountDetective()

    async def process_links(self, message_data, discord_sender: DiscordSender):
        # self.logger.info(f'The queued message is: {message_data}')        
        self.discord_sender = discord_sender
        print("\n")
        print(f"Process Message: {message_data} \n")
        for url in message_data['urls']:
            if "facebook.com" in url:
                await self.process_facebook_url(url, message_data)
            else:
                await self.process_amazon_url(url, message_data)

    async def process_facebook_url(self, url, message_data):
        print(f"Processing message process_facebook_url: {message_data}\n")
        content, urls = await self.link_resolver.scrape_facebook_post_content(url)
        content = self.text_cleaner.truncate_text_at_keywords(content, ["Toa maoni", "Comment"])
        if urls:
            if "amazon.com" in urls[0]:
                message_data['text'] = content
                await self.process_amazon_url(urls[0], message_data)
            else:
                self.logger.info(f"URL does not contain 'amazon.com': {urls[0]}")

    async def process_amazon_url(self, url, message_data):
        print(f"Processing message process_amazon_url: {message_data}\n")
        link_data = await self.link_resolver.resolve_url(url)
        
        if link_data['resolved'] and "amazon.com" in link_data['url']:
            cleaned_link = await self.link_dresser.clean_amazon_link(link_data['url'])
            
            await self.amazon_helper(cleaned_link, message_data)

    async def amazon_helper(self, url: str, message_data):   
        text = message_data['text']
        is_promo_only = False        
        is_no_promo_needed = False
        self.text_cleaner = TextCleaner()
        self.price_match = PriceMatch()
        self.promo_buster = PromoBuster()
        self.discount_detective = DiscountDetective()
        
        try:
            category, cleaned_text = await self.text_cleaner.def_get_category_and_clean(text)
            
            
            prices = await self.price_match.find_price(cleaned_text)
            deal_price, retail_price = prices.get('deal_price'), prices.get('retail_price')
            
            promo_codes_discounts = await self.promo_buster.find_promo_code(cleaned_text)
            if text in [code for code, _ in promo_codes_discounts]:
                is_promo_only = True
            if "no promo code needed" in text.lower():
                is_no_promo_needed = True
                
            discounts = await self.discount_detective.process_text(cleaned_text)
            print(f"Message: Data : {message_data}\n")
            print(f"Text: {text}\n")            
            print(f"Deal Price: {deal_price}\n")
            print(f"Retail Price: {retail_price}\n")
            print(f"Promo discounts: {promo_codes_discounts}\n")
            print(f"Discount data: {discounts}\n")            
            
            if not is_promo_only:
                if url.startswith('https://www.amazon.com/promocode/') or url.startswith('https://www.amazon.com/s'):                    
                    embeds = await skip_scrape(url, [code for code, _ in promo_codes_discounts], text)
                    await self.discord_sender.send_to_discord(embed=embeds, links=[url], 
                                                               filepath=message_data['image'], 
                                                               is_promo_code_only=is_promo_only)
                    
                else:
                    
                    embed_data = await get_product_data(url, method='dataByLink', promo_codes=[code for code, _ in promo_codes_discounts], 
                                           promo_discounts={code: discount for code, discount in promo_codes_discounts if discount is not None}, 
                                           discount_data=discounts,
                                           deal_price=deal_price, retail_price=retail_price, text=text)
                    
                    # self.logger.info(f"embedded_data: {embed_data}")
                    
                    if embed_data:
                        await self.discord_sender.send_to_discord(embed=embed_data, links=[url],
                                                        filepath=message_data['image'],
                                                        is_promo_code_only=is_promo_only
                                                        )
        except Exception as e:
            self.logger.error(f"An error occurred in amazon_helper: {e}")