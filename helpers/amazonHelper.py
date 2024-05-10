from APICalls.amazon.scrapers.scraper import Amazon

from datetime import datetime
import discord
from utils.logger import configure_logger
from utils.extract_number import extract_number
from helpers.priceBreakdown import PriceBreakDown
from helpers.text_analyzer import TextAnalysis



logger = configure_logger(__name__)

async def getDataByAsinSearch(userInput, promo_codes, promo_discounts, discount_data, deal_price, retail_price, text):
    results = []
    links_to_pages = await Amazon(userInput).find_links_with_aria_label()
    links_to_pages.insert(0, userInput)        
    
    for link_to_page in links_to_pages:
        try:        
            data_asins = await Amazon(link_to_page).product_links()            
            for asin in data_asins:                                  
                data = await get_product_data(asin, method='dataByAsin', promo_codes=promo_codes, promo_discounts=promo_discounts, discount_data=discount_data,
                                              deal_price=deal_price, retail_price=retail_price, text=text) 
                if data:
                    results.append(data)
        except Exception as e:
            print(f"Error {e}")        
    return results
                 

async def get_product_data(userInput, method, promo_codes, promo_discounts, discount_data, deal_price, retail_price, text):
    """
    Fetches data from Amazon using either an ASIN or a link, creates a Discord embed with product data.
    """
    print(f"User Input: {userInput}")
    
    price_breakdown = PriceBreakDown()
    
    try:
               
        datas = await getattr(Amazon(userInput), method)()
        if not datas:
            logger.info("Failed to retrieve data from Amazon.")
            return
        print('passes 0')
        print('\n')
        logger.info(f"Data {datas}\n")
        
        name = datas.get('Name', 'No Name Available')
        hyperlink = f"https://www.amazon.com/dp/{datas.get('ASIN', 'Unavailable')}"
        embed = discord.Embed(title=name, url=hyperlink, color=0xff9900)
        
        embed.set_thumbnail(url=datas.get('Image', 'https://example.com/default_thumbnail.jpg'))
        embed.timestamp = datetime.now()
        embed.set_footer(text='Powered by DiamondAIO', icon_url='https://static.timesofisrael.com/www/uploads/2017/12/iStock-639204700.jpg')
        embed.add_field(name="Content", value=f"```{text}```", inline=False)                
        
        saving_percentage = await extract_number(datas.get('Savings percentage'))
        product_price = await extract_number(datas.get('Price', '0'))
        block_message = datas.get('Promo block message')
        deal_price = 0
        if deal_price:
            deal_price = await extract_number(deal_price.replace('xx', '99'))
        is_limited_deal = datas.get('Limited deal')
        print('passed 1')
        
        total_discount = 0
        promo_disc = 0
        disc = 0
        promo_code = ""
        # Extract discount from promo code if available
        if promo_codes and promo_codes[0][:2]:
            promo_code = promo_codes[0]
            if promo_code in name:
                promo_code = ""
            else:
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
            
        # No promo codes, no deal price, no discount data or Limited deal
        if (not promo_codes and not discount_data) or is_limited_deal == 'Limited time deal':
            if saving_percentage:
                prod_price = await extract_number(datas.get('Price', '1'))                
                deal_price = prod_price
                product_price = (prod_price * 100) / (100 - saving_percentage)
                total_discount = saving_percentage              
                                        
        print("passed 2")
        if total_discount:
            if not product_price:
                product_price = deal_price / (1 - total_discount / 100)
            else:
                deal_price = product_price * (1 - total_discount / 100)
        
        is_price_dollars = False
        if "apply" in block_message.lower():
            text_analyzer = TextAnalysis()
            result_analyzed = text_analyzer.analyze_text(text)
            if result_analyzed['deal_price']:
                discount_data = await extract_number(result_analyzed['deal_price'])
                is_price_dollars = True
            elif result_analyzed['discounts'] and result_analyzed['discounts'][0]:
                discount_data = await extract_number(result_analyzed['discounts'][0])
                
            # discount_data = result_analyzed['deal_price'] or result_analyzed['discounts']
                            
        breakdown, total = await price_breakdown.price_discounter(retail_price=product_price, discount_data=disc, 
                                         promo_discount=promo_disc, savings_percentage=saving_percentage,
                                         promo_code=promo_code, is_price_dollars=is_price_dollars)        
                
        breakdown_details = "```\n"  
        for key, value in breakdown.items():
            breakdown_details += f"{key}: {value}\n"
        breakdown_details += "```"  
        
        embed.add_field(name="Order Summary", value=breakdown_details, inline=False)
        # if total_discount and deal_price and not product_price:
        #     product_price = float((deal_price * 100)  / (100 - float(total_discount)))                                                    
              
        # print("passed 3")
        # if product_price and not deal_price:
            
        #     if total_discount:
        #         deal_price = product_price * (1 - total_discount / 100)                                
        #     else:                
        #         deal_price = float(product_price)
                
        #         if saving_percentage:
        #             product_price = float((deal_price * 100) / (100 - saving_percentage))
        #             total_discount = saving_percentage
        # if deal_price == product_price or product_price < deal_price:
        #     total_discount = await extract_number(saving_percentage)
        #     if total_discount:
        #         deal_price = product_price
        # product_price = float((deal_price * 100) / (100 - saving_percentage))
        print("passed 4")
        if total and not total == product_price:
            embed.add_field(name='Deal Price', value=f"```${total:.2f}```", inline=True)
        elif deal_price:
            embed.add_field(name='Deal Price', value=f"```${deal_price:.2f}```", inline=True)
        
        print("passed 5")        
        if product_price or retail_price:
            retail = float(retail_price if retail_price else product_price)
            embed.add_field(name='Retail Price', value=f"```${retail:.2f}```", inline=True)
        
        print("passed 6")
        if promo_codes:
            embed.add_field(name='Promo Codes', value='```, ```'.join(promo_codes), inline=False)
        else:
            embed.add_field(name='Promo Codes', value="```No promo code needed```", inline=False)
        
        print("passed 7")
        if total_discount:
            embed.add_field(name='Discount', value=f'```{float(total_discount):.2f}% Off```', inline=False)
        
        print("passed 8")
        # if deal_price and product_price and not discount_data and not total_discount:
        #     discount = (1 - (deal_price / retail_price)) * 100
        #     print(f"discount: {discount}")
        #     embed.add_field(name='Discount', value=f"```{float(discount):.2f}% Off```")

            
        print("passed 9")
        embed.add_field(name='Availability', value=datas.get('Availability', 'Unavailable'), inline=False)
        store_link = datas['Store link']
        if not 'amazon.com' in store_link:
            store_link = store_link.replace('amazon.', 'amazon.com')
            
        embed.add_field(name = "Store", value = f"[{datas['Store']}]({store_link})", inline = False)
        logger.info(f"Embed: {embed.to_dict()}\n")
        return embed
    except Exception as e:
        logger.error(f"Error getdata {e}")

        
async def skip_scrape(userInput, promo_codes, text):
    # Filtering and converting to integers if the first two characters are digits.
    promo_discount = [int(promo_code[:2]) for promo_code in promo_codes if is_int(promo_code[:2])]
    
    embed = discord.Embed(title=f"Save {'%'.join(map(str, promo_discount))}% on the eligible item(s) below", url=userInput, color=0xff9900)
    embed.set_thumbnail(url='https://example.com/default_thumbnail.jpg')
    embed.timestamp = datetime.now()    
    embed.set_footer(text='Powered by DiamondAIO', icon_url='https://static.timesofisrael.com/www/uploads/2017/12/iStock-639204700.jpg')
    embed.add_field(name='Content', value=f'```{text}```', inline=False)
    if promo_codes:
        embed.add_field(name='Promo Codes', value=f'```, ```'.join(promo_codes), inline=False)
    
    if promo_discount:
        embed.add_field(name='Promo Discount', value='```, ```'.join(f"{discount}% Off" for discount in promo_discount), inline=False)
    return embed

async def product_types(userInput) ->list:
    
    return await Amazon(userInput).product_types()    


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
