from utils.logger import configure_logger
from senders.discordSender.sendMessages import DiscordSender
from helpers.amazonHelper import get_product_data, skip_scrape
from processors.linkProcessors.linkResolvers import LinkResolver
from processors.linkProcessors.linkDressers import LinkDresser
from helpers.text_analyzer import TextAnalysis
from processors.textProcessors.textCleaner import TextCleaner

class Helper:
    def __init__(self, message_data: dict, discord_sender: DiscordSender) -> None:
        self.logger = configure_logger(__name__)        
        self.discord_sender = discord_sender
        self.link_resolver = LinkResolver()
        self.link_dresser = LinkDresser()        

    async def process_links(self, message_data, discord_sender: DiscordSender):
        # self.logger.info(f'The queued message is: {message_data}')        
        self.discord_sender = discord_sender
        print("\n")
        print(f"Process Message: {message_data} \n")
        try:
            for url in message_data['urls']:
                if "facebook.com" in url:
                    await self.process_facebook_url(url, message_data)
                else:
                    await self.process_amazon_url(url, message_data)
        except Exception as e:
            pass
    async def process_facebook_url(self, url, message_data):
        print(f"Processing message process_facebook_url: {message_data}\n")
        content, urls = await self.link_resolver.scrape_facebook_post_content(url)
        text_cleaner = TextCleaner()
        content = await text_cleaner.truncate_text_at_keywords(content, ["Toa maoni", "Comment"])
        if urls:
            resolved_url_fb = await self.link_resolver.resolve_url(url=urls[0])            
            
            if "amazon.com" in resolved_url_fb['url']:
                cleaned_url_link_fb = await self.link_dresser.clean_amazon_link(resolved_url_fb['url'])
                message_data['text'] = content
                await self.process_amazon_url(cleaned_url_link_fb, message_data)
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
        try:
            
            text_analyzer = TextAnalysis()
            result_analyzed = await text_analyzer.analyze_text(text)                                    
            
            if not result_analyzed['is_promo_only']:
                if url.startswith('https://www.amazon.com/promocode/') or url.startswith('https://www.amazon.com/s'):                    
                    embeds = await skip_scrape(url, [code for code, _ in result_analyzed['promo_codes_discounts']], text)
                    await self.discord_sender.send_to_discord(embed=embeds, links=[url], 
                                                               filepath=message_data['image'], 
                                                               is_promo_code_only=result_analyzed['is_promo_only'])
                    
                else:
                    
                    embed_data = await get_product_data(url, method='dataByLink', promo_codes=[code for code, _ in result_analyzed['promo_codes_discounts']], 
                                           promo_discounts={code: discount for code, discount in result_analyzed['promo_codes_discounts'] if discount is not None}, 
                                           discount_data=result_analyzed['discounts'],
                                           deal_price=result_analyzed['deal_price'], retail_price=result_analyzed['retail_price'], text=text)
                    
                    # self.logger.info(f"embedded_data: {embed_data}")
                    
                    if embed_data:
                        await self.discord_sender.send_to_discord(embed=embed_data, links=[url],
                                                        filepath=message_data['image'],
                                                        is_promo_code_only=result_analyzed['is_promo_only']
                                                        )
        except Exception as e:
            self.logger.error(f"An error occurred in amazon_helper: {e}")