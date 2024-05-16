from APICalls.amazon.scrapers.scraper import Amazon
from APICalls.amazon.keepa.keepaAPI import KeepaAPI

from datetime import datetime
import discord
from utils.logger import configure_logger
from utils.extract_number import extract_number
from utils.extract_asin import extract_asin
from helpers.priceBreakdown import PriceBreakDown
from helpers.text_analyzer import TextAnalysis
from utils.unwanted import filter_unwanted


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
                 

# async def get_product_data(userInput, method, promo_codes, promo_discounts, discount_data, deal_price, retail_price, text):
#     """
#     Fetches data from Amazon using either an ASIN or a link, creates a Discord embed with product data.
#     """
#     print(f"User Input: {userInput}")
    
#     price_breakdown = PriceBreakDown()
    
#     try:
               
#         datas = await getattr(Amazon(userInput), method)()
#         if not datas:
#             logger.info("Failed to retrieve data from Amazon.")
#             return
#         keepa_api = KeepaAPI()
        
#         product_asin = await extract_asin(userInput)
#         product_price_info = await keepa_api.make_request(product_asin)
        
#         print('passes 0')
#         print('\n')
#         logger.info(f"Data {datas}\n")
        
#         name = datas.get('Name', 'No Name Available')
#         hyperlink = f"https://www.amazon.com/dp/{datas.get('ASIN', 'Unavailable')}"
#         embed = discord.Embed(title=name, url=hyperlink, color=0xff9900)
        
#         embed.set_thumbnail(url=datas.get('Image', 'https://example.com/default_thumbnail.jpg'))
#         embed.timestamp = datetime.now()
#         embed.set_footer(text='Powered by DiamondAIO', icon_url='https://static.timesofisrael.com/www/uploads/2017/12/iStock-639204700.jpg')
#         embed.add_field(name="Content", value=f"```{text}```", inline=False)                
        
#         form_tracker = {
#             'List Price': 'Missing',
#             'Deal Price': 'Missing',
#             'Clip coupon text': 'Missing',
#             'Clip coupon page': 'Missing',
#             'Promo Code': 'Missing',
#             'Promo Discount': 'Missing',
#             # 'Checkout Price': 'Missing',
#             'Text Deal Price': 'Missing'
#         }
        
#         form_tracker['Text Deal Price'] = deal_price
        
#         saving_percentage = await extract_number(datas.get('Savings percentage'))
        
#         product_price = float(product_price_info['price'].replace('$', '').strip())
        
#         block_message = datas.get('Promo block message')
#         is_lightning_deal = datas.get('lightningDeal')
#         deal_price = 0
#         if deal_price:
#             deal_price = await extract_number(deal_price.replace('xx', '99'))
#         is_limited_deal = datas.get('Limited deal')
              
#         print('passed 1')
        
#         total_discount = 0
#         promo_disc = 0
#         disc = 0
#         more_discount_data = 0
#         promo_code = ""
#         print('passed 1_1')
#         # Extract discount from promo code if available
#         if promo_codes and promo_codes[0][:2]:
#             promo_code = promo_codes[0]
            
#             if promo_code in name:
#                 promo_code = ""
#             else:
#                 form_tracker['Promo Code'] = promo_code                
#                 promo_disc = await extract_number(promo_codes[0][:2]) or 0
#                 if len(str(promo_disc)) == 2:
#                     form_tracker['Promo Discount'] = f"{promo_disc}%"
#                 else:
#                     promo_disc = 0
#         print('passed 1_2')
#         # Calculate total discount based on available data
#         if discount_data and discount_data[0]:
#             disc = await extract_number(discount_data[0][0])
#             form_tracker['Clip coupon text'] = f"{disc}%"
#             if promo_codes:
#                 total_discount = promo_disc + disc
#             else:
#                 total_discount = disc
#         elif promo_codes:  # Fallback to promo code discount if only promo codes are provided
#             total_discount = promo_disc
#         print('passed 1_3') 
#         # No promo codes, no deal price, no discount data or Limited deal
#         if (not promo_codes and not discount_data) or is_limited_deal == 'Limited time deal':
#             if saving_percentage:
#                 # prod_price = await extract_number(datas.get('Price', '1'))                
#                 # deal_price = prod_price
#                 # product_price = (prod_price * 100) / (100 - saving_percentage)
#                 total_discount = saving_percentage              
                                    
#         # print("passed 2")
#         # if total_discount:
#         #     if not product_price:
#         #         product_price = deal_price / (1 - total_discount / 100)
#         #     else:
#         #         deal_price = product_price * (1 - total_discount / 100)
#         print('passed 1_4')
#         is_price_dollars = False
#         if "apply" in block_message.lower():
#             text_analyzer = TextAnalysis()
#             result_analyzed = await text_analyzer.analyze_text(block_message)
#             print(f"result_analyzed: {result_analyzed}")
#             if result_analyzed['deal_price']:
#                 more_discount_data = await extract_number(result_analyzed['deal_price'])
#                 is_price_dollars = True
#                 form_tracker['Clip coupon page'] = f"${more_discount_data}"
#             elif result_analyzed['discounts'] and result_analyzed['discounts'][0]:
#                 more_discount_data = await extract_number(result_analyzed['discounts'][0])
#                 form_tracker['Clip coupon page'] = f"{more_discount_data}%"
#             # discount_data = result_analyzed['deal_price'] or result_analyzed['discounts']
#         print('passed 1_5')
#         if saving_percentage and is_lightning_deal.lower() != 'lightning deal':
#            product_price  = ((product_price * 100) / (100 - saving_percentage))
#         form_tracker['List Price'] = product_price
#         print('passed 1_6')
#         breakdown, total = await price_breakdown.price_discounter(retail_price=product_price, discount_data=disc, 
#                                          promo_discount=promo_disc, savings_percentage=saving_percentage,
#                                          promo_code=promo_code, is_price_dollars=is_price_dollars,
#                                           more_discount_data=more_discount_data)
#         form_tracker['Deal Price'] = total
#         print('passed 1_7')
#         breakdown_details = "```\n"  
#         for key, value in breakdown.items():
#             breakdown_details += f"{key}: {value}\n"
#         breakdown_details += "```"  
#         print('passed 1_8')
#         form_tracker_details = "```\n"
#         for key, value in form_tracker.items():
#             form_tracker_details += f"{key}: {value}\n"
#         form_tracker_details += "```"
        
#         embed.add_field(name='Tracker details', value=form_tracker_details, inline=False)
#         embed.add_field(name="Order Summary", value=breakdown_details, inline=False)
        
#         # if total_discount and deal_price and not product_price:
#         #     product_price = float((deal_price * 100)  / (100 - float(total_discount)))                                                    
              
#         # print("passed 3")
#         # if product_price and not deal_price:
            
#         #     if total_discount:
#         #         deal_price = product_price * (1 - total_discount / 100)                                
#         #     else:                
#         #         deal_price = float(product_price)
                
#         #         if saving_percentage:
#         #             product_price = float((deal_price * 100) / (100 - saving_percentage))
#         #             total_discount = saving_percentage
#         # if deal_price == product_price or product_price < deal_price:
#         #     total_discount = await extract_number(saving_percentage)
#         #     if total_discount:
#         #         deal_price = product_price
#         # product_price = float((deal_price * 100) / (100 - saving_percentage))
#         print("passed 4")
#         if total and not total == product_price:
#             embed.add_field(name='Deal Price', value=f"```${total:.2f}```", inline=True)
#         elif deal_price:
#             embed.add_field(name='Deal Price', value=f"```${deal_price:.2f}```", inline=True)
        
#         print("passed 5")        
#         if product_price:
#             retail = await extract_number(product_price)
#             embed.add_field(name='Retail Price', value=f"```${retail:.2f}```", inline=True)
        
#         print("passed 6")
#         if promo_codes:
#             embed.add_field(name='Promo Codes', value='```, ```'.join(promo_codes), inline=False)
#         else:
#             embed.add_field(name='Promo Codes', value="```No promo code needed```", inline=False)
        
#         print("passed 7")
#         if total_discount:
#             embed.add_field(name='Discount', value=f'```{float(total_discount):.2f}% Off```', inline=False)
        
#         print("passed 8")
#         # if deal_price and product_price and not discount_data and not total_discount:
#         #     discount = (1 - (deal_price / retail_price)) * 100
#         #     print(f"discount: {discount}")
#         #     embed.add_field(name='Discount', value=f"```{float(discount):.2f}% Off```")

            
#         print("passed 9")
#         embed.add_field(name='Availability', value=datas.get('Availability', 'Unavailable'), inline=False)
#         store_link = datas['Store link']
#         if not 'amazon.com' in store_link:
#             store_link = store_link.replace('amazon.', 'amazon.com')
            
#         embed.add_field(name = "Store", value = f"[{datas['Store']}]({store_link})", inline = False)
#         logger.info(f"Embed: {embed.to_dict()}\n")
#         return embed
#     except Exception as e:
#         logger.error(f"Error getdata {e}")

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
        print('passed 1')
        keepa_api = KeepaAPI()
        product_asin = await extract_asin(userInput)
        product_price_info = await keepa_api.make_request(product_asin)

        logger.info(f"Data {datas}\n")

        name = datas.get('Name', 'No Name Available')
        hyperlink = f"https://www.amazon.com/dp/{datas.get('ASIN', 'Unavailable')}"
        embed = discord.Embed(title=name, url=hyperlink, color=0xff9900)
        embed.set_thumbnail(url=datas.get('Image', 'https://example.com/default_thumbnail.jpg'))
        embed.timestamp = datetime.now()
        embed.set_footer(text='Powered by DiamondAIO', icon_url='https://static.timesofisrael.com/www/uploads/2017/12/iStock-639204700.jpg')
        embed.add_field(name="Content", value=f"```{text}```", inline=False)
        
        form_tracker = {
            'List Price': 'Missing',
            'Deal Price': 'Missing',
            'Clip coupon text': 'Missing',
            'Clip coupon page': 'Missing',
            'Promo Code': 'Missing',
            'Promo Discount': 'Missing',
            'Text Deal Price': 'Missing'
        }
        print('passed 2')
        form_tracker['Text Deal Price'] = deal_price
        main_deal_price = 0
        main_deal_price = deal_price
        saving_percentage = await extract_number(datas.get('Savings percentage'))
        product_price = float(product_price_info['price'].replace('$', '').strip())

        block_message = datas.get('Promo block message')
        block_message_2 = datas.get('Promo block message 2')
        is_lightning_deal = datas.get('lightningDeal')
        deal_price = 0
        if deal_price:
            deal_price = await extract_number(deal_price.replace('xx', '99'))
        is_limited_deal = datas.get('Limited deal')
        
        print('passed 3')
        
        total_discount = 0
        promo_disc = 0
        disc = 0
        more_discount_data = 0
        more_discount_data_save = 0
        promo_code = None
        promo_codes = await filter_unwanted(promo_codes)
        print('passed 4')
        if promo_codes and promo_codes[0][:2]:
            promo_code = promo_codes[0]
            if promo_code not in name:
                form_tracker['Promo Code'] = promo_code                
                promo_disc = await extract_number(promo_codes[0][:2]) or 0                
                if len(str(int(promo_disc))) >= 2:
                    form_tracker['Promo Discount'] = f"{promo_disc}%"
                else:
                    promo_disc = 0
                print(f"form_tracker: {form_tracker}")

        print('passed 5')
        if discount_data and discount_data[0]:
            disc = await extract_number(discount_data[0][0])
            form_tracker['Clip coupon text'] = f"{disc}%"
            total_discount = promo_disc + disc if promo_codes else disc
        elif promo_codes:
            total_discount = promo_disc

        if (not promo_codes and not discount_data) or is_limited_deal == 'Limited time deal':
            if saving_percentage:
                total_discount = saving_percentage

        print('passed 6')
        is_price_dollars = False
        
        if "coupon:" in block_message.lower() or ("save" in block_message.lower() and promo_code in block_message):
            text_analyzer = TextAnalysis()
            result_analyzed = await text_analyzer.analyze_text(block_message)
            print(f'result analyzed: {result_analyzed}')
            
            if result_analyzed['deal_price'] is not None:
                print('passed_result_analyzed_1')
                more_discount_data = await extract_number(result_analyzed['deal_price'])
                is_price_dollars = True
                form_tracker['Clip coupon page 1'] = f"${more_discount_data}"
                
            elif result_analyzed['discounts'] and result_analyzed['discounts'][0]:
                print(f'passed_result_analyzed_2: {result_analyzed["discounts"][0]}')
                more_discount_data = await extract_number(result_analyzed['discounts'][0][0])
                print(f"More discount: {more_discount_data}")
                form_tracker['Clip coupon page 1'] = f"{more_discount_data}%"
        elif "save" in block_message_2.lower() and promo_code in block_message_2:
            text_analyzer = TextAnalysis()
            result_analyzed = await text_analyzer.analyze_text(block_message_2)
            print(f'result analyzed: {result_analyzed}')
            
            if result_analyzed['deal_price'] is not None:
                print('passed_result_analyzed_3')
                more_discount_data_save = await extract_number(result_analyzed['deal_price'])
                is_price_dollars = True
                form_tracker['Clip coupon page 2'] = f"${more_discount_data_save}"
                
            elif result_analyzed['discounts'] and result_analyzed['discounts'][0]:
                print(f'passed_result_analyzed_4: {result_analyzed["discounts"][0]}')
                more_discount_data_save = await extract_number(result_analyzed['discounts'][0][0])
                print(f"More discount: {more_discount_data}")
                form_tracker['Clip coupon page 2'] = f"{more_discount_data_save}%"
        if 'clip the extra' in text.lower() and more_discount_data and disc:
            more_discount_data = 0

        print('Passed 7')
        if saving_percentage and is_lightning_deal.lower() != 'lightning deal':
            
           product_price = ((product_price * 100) / (100 - saving_percentage))

        form_tracker['List Price'] = product_price
        print('passed 8')
        breakdown, total = await price_breakdown.price_discounter(
            retail_price=product_price, 
            discount_data=disc, 
            promo_discount=promo_disc, 
            savings_percentage=saving_percentage,
            promo_code=promo_code, 
            is_price_dollars=is_price_dollars,
            more_discount_data=more_discount_data,
            more_discount_data_save=more_discount_data_save,
            deal_price=main_deal_price
        )
        print('passed 9')
        form_tracker['Deal Price'] = total

        breakdown_details = "```\n"
        for key, value in breakdown.items():
            breakdown_details += f"{key}: {value}\n"
        breakdown_details += "```"

        form_tracker_details = "```\n"
        for key, value in form_tracker.items():
            form_tracker_details += f"{key}: {value}\n"
        form_tracker_details += "```"
        
        embed.add_field(name='Tracker details', value=form_tracker_details, inline=False)
        embed.add_field(name="Order Summary", value=breakdown_details, inline=False)
        print('passed 10')
        if total and total != product_price:
            embed.add_field(name='Deal Price', value=f"```${total:.2f}```", inline=True)
        elif deal_price:
            embed.add_field(name='Deal Price', value=f"```${deal_price:.2f}```", inline=True)
        print('passed 11')
        if product_price:
            retail = product_price
            embed.add_field(name='Retail Price', value=f"```${retail:.2f}```", inline=True)
        print('passed 12')
        if promo_codes:
            embed.add_field(name='Promo Codes', value='```, ```'.join(promo_codes), inline=False)
        else:
            embed.add_field(name='Promo Codes', value="```No promo code needed```", inline=False)
        print('passed 13')
        if total_discount:
            embed.add_field(name='Discount', value=f'```{float(total_discount):.2f}% Off```', inline=False)
        print('passed 14')
        embed.add_field(name='Availability', value=datas.get('Availability', 'Unavailable'), inline=False)
        
        store_link = datas['Store link']
        if 'amazon.com' not in store_link:
            store_link = store_link.replace('amazon.', 'amazon.com')
            
        embed.add_field(name="Store", value=f"[{datas['Store']}]({store_link})", inline=False)
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
    
