import os


# # Replace with your actual API key
# API_KEY = os.getenv('KEEP_API_KEY')
# ASIN = 'B0CB5XMC1D'  # Example ASIN, replace with the product's ASIN you are interested in

# # Define the API endpoint
# endpoint = 'https://api.keepa.com/product'

# # Set up parameters
# params = {
#     'key': API_KEY,
#     'domain': 1,  # For Amazon.com, use the appropriate marketplace domain
#     'asin': ASIN
# }

# # Make the API call
# response = requests.get(endpoint, params=params)
# data = response.json()

# with open('file.json', 'w') as json_file:
#     json.dump(data, json_file, indent=4)

# if product_data := data.get('products'):
#     print(product_data[0]['csv'][1])
    
import keepa
from collections import Counter
from datetime import datetime, timedelta

accesskey = os.getenv('KEEP_API_KEY') # enter real access key here
api = keepa.Keepa(accesskey)

# Single ASIN query
products = api.query('B07HYZM6ZR') # returns list of product data


# Dump the JSON, using the default function to handle non-serializable objects
with open('file-prods.txt', 'w', encoding='utf-8') as file:
    file.write(str(products))
    
def get_price(product):
        # AMAZON = 0, NEW = 1 are the indices for Amazon and New prices in the csv array
        price_history = product['csv']
        
        # Check both Amazon and Marketplace New prices
        for price_type_index in [0, 1]:
            if price_history[price_type_index]:
                # Keepa stores the price history as [timestamp, price, timestamp, price, ...]
                # Iterate backwards to find the most recent price
                for i in range(len(price_history[price_type_index])-2, -1, -2):
                    price = price_history[price_type_index][i+1]
                    if price != -1:  # -1 indicates no price available
                        return f"${price / 100:.2f}"  # Convert to dollars

def get_historic_price( product):
    # Keepa's timestamp for one year ago from now
    one_year_ago_keepa = (datetime.now() - timedelta(days=365)).timestamp() / 60 + 21564000
    indices_to_check = [0, 1, 2, 10]  # Indices for Amazon, Marketplace New, Used, New FBA

    for index in indices_to_check:
        historic_prices = []
        if 'csv' in product and product['csv'][index]:
            price_history = product['csv'][index]
            for i in range(0, len(price_history), 2):
                keepa_timestamp = price_history[i] + 21564000  # Convert to Unix timestamp
                price = price_history[i + 1]
                # Check if the timestamp is within the last year and price is not -1
                if keepa_timestamp * 60 >= one_year_ago_keepa and price != -1:
                    converted_price = price / 100.0  # Convert price from cents to dollars
                    historic_prices.append(converted_price)

            if historic_prices:                
                mode_price = Counter(historic_prices).most_common(1)[0][0]
                print(f"{historic_prices[-2]:.2f}")
                print(historic_prices)
                return f"${mode_price:.2f}"

    return "Unknown"



def get_coupon( product):

        if not product:
            return "No coupon available"

        max_dollar_discount = 0
        max_percent_discount = 0

        # Check 'coupon' field
        coupon = product.get('coupon')
        if coupon:
            one_time_discount = coupon[0]
            subscribe_and_save_discount = coupon[1]

            if one_time_discount > 0:
                max_dollar_discount = max(max_dollar_discount, one_time_discount/100)
            elif one_time_discount < 0:
                max_percent_discount = max(max_percent_discount, -one_time_discount)

            if subscribe_and_save_discount > 0:
                max_dollar_discount = max(max_dollar_discount, subscribe_and_save_discount/100)
            elif subscribe_and_save_discount < 0:
                max_percent_discount = max(max_percent_discount, -subscribe_and_save_discount)

        # Check 'promotions' field
        promotions = product.get('promotions')
        if promotions:
            for promo in promotions:
                discount_amount = promo.get('discountAmount')
                discount_percent = promo.get('discountPercent')

                if discount_amount:
                    max_dollar_discount = max(max_dollar_discount, discount_amount/100)
                elif discount_percent:
                    max_percent_discount = max(max_percent_discount, discount_percent)
        
        discounts = []

        if max_dollar_discount > 0:
            discounts.append(f"${max_dollar_discount:.2f} off")
        if max_percent_discount > 0:
            discounts.append(f"{max_percent_discount}% off")

        if discounts:
            return ", ".join(discounts)

        return None

print(get_price(products[0]))
print(get_historic_price(products[0]))
# print(get_coupon(products[0]))