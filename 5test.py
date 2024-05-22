# import requests
# import os


# # Define your access key and other parameters
# access_key = os.getenv('KEEP_API_KEY')
# domain_id = 1  # Example for Amazon UK
# asin = "B0B8G4QBSV"  # Replace with the ASIN of the product you are interested in

# # Define the base URL
# base_url = "https://api.keepa.com/lightningdeal"

# # Define the query parameters
# params = {
#     "key": access_key,
#     "domain": domain_id,
#     "asin": asin
# }

# # Make the request
# response = requests.get(base_url, params=params)

# # Check the response status
# if response.status_code == 200:
#     # Parse the JSON response
#     data = response.json()
#     print(data)
#     # Print the data
#     print(data['lightningDeals'][0]['currentPrice'] / 100)
# else:
#     print(f"Error: {response.status_code}")
#     print(response.text)


# # discount = 89

# # if 90 <= discount <= 100:
# #     print(f'discount 90 - 100: {discount}')
# # elif 80 <= discount <= 89:
# #     print(f'discount 80 - 89: {discount}')
# # elif 70 <= discount <= 79:
# #     print(f'discount 70 - 79: {discount}')
# # elif 60 <= discount <= 69:
# #     print(f'discount 60 - 69: {discount}')
# # elif 1 <= discount <= 59:
# #     print(f'discount 1 - 59: {discount}')

# def name():
#     return 3, None

# p, t = name()

# print(p)
# print(t)

from utils.extract_asin import extract_asin
import asyncio

import re
import asyncio

async def extract_asin(url: str) -> str:
    """
    Extracts and returns product asin from Amazon product URLs.
    """
    asin_regex = r'https?://www\.amazon\.com/(?:.*/)?(?:dp|gp/product)/([A-Z0-9]+)'
    match = re.search(asin_regex, url)
    if match:
        asin = match.group(1)
        return asin
    else:
        return None

async def main():
    url = 'https://www.amazon.com/dp/B07VRFC3Y7?ref_=as_li_ss_tl'
    asin = await extract_asin(url)
    print(f"ASIN: {asin}")

# Run the main function
asyncio.run(main())
