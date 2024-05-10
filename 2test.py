import requests
import os
import json

# Replace with your actual API key
API_KEY = os.getenv('KEEP_API_KEY')
ASIN = 'B09TZP2B2D'  # Example ASIN, replace with the product's ASIN you are interested in

# Define the API endpoint
endpoint = 'https://api.keepa.com/product'

# Set up parameters
params = {
    'key': API_KEY,
    'domain': 1,  # For Amazon.com, use the appropriate marketplace domain
    'asin': ASIN
}

# Make the API call
response = requests.get(endpoint, params=params)
data = response.json()

with open('file.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

if product_data := data.get('products'):
    print(product_data[0]['csv'][1])