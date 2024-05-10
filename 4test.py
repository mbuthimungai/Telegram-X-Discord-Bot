import requests

def get_lightning_deals(api_key, domain_id, asin):
    url = f"https://api.keepa.com/lightningdeal?key={api_key}&domain={domain_id}&asin={asin}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # This will contain the array of lightning deal objects
    else:
        
        return None

# Usage example
api_key = '9drsddrncr408fb9ke607gdjsnlvph5nnph1ae7ge99u78aso447hoj3r9ne3p9r'
domain_id = 1  # Example: '1' for Amazon.com
asin = 'B0C1C87MCN'

lightning_deals = get_lightning_deals(api_key, domain_id, asin)
print(lightning_deals)
if lightning_deals:
    print(lightning_deals)
else:
    print("Failed to retrieve lightning deals.")
