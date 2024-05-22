import aiohttp
import asyncio
import os

async def fetch_lightning_deal():
    # Define your access key and other parameters
    access_key = os.getenv('KEEP_API_KEY')
    domain_id = 1  # Example for Amazon UK
    asin = "B0C89L3RYG"  # Replace with the ASIN of the product you are interested in

    # Define the base URL
    base_url = "https://api.keepa.com/lightningdeal"

    # Define the query parameters
    params = {
        "key": access_key,
        "domain": domain_id,
        "asin": asin
    }

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(base_url, params=params) as response:
                    if response.status == 200:
                        # Parse the JSON response
                        data = await response.json()
                        # Check if 'lightningDeals' key is in the response
                        if 'lightningDeals' in data:
                            return data['lightningDeals'][0]['currentPrice']
                        else:
                            print("No lightning deals found in the response.")
                            return None
                    else:
                        print(f"Error: {response.status}")
                        # Optional: print response text for debugging
                        error_text = await response.text()
                        print(error_text)
            except Exception as e:
                print(f"An error occurred: {e}")

            # Wait for a short period before retrying
            await asyncio.sleep(5)

# Run the function
async def main():
    price = await fetch_lightning_deal()
    if price:
        print(f"Current price: {price}")

# Execute the main function
if __name__ == "__main__":
    asyncio.run(main())
