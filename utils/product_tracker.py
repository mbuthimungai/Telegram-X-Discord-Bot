import time
import asyncio


class ProductTracker:
    def __init__(self):
        self.product_dict = {}
        self.lock = asyncio.Lock()

    async def add_product(self, product):
        async with self.lock:
            self.product_dict[product] = time.time()
            print(f"Added product: {product} at {self.product_dict[product]}")

    async def remove_expired_asins(self):
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = time.time()
            async with self.lock:
                expired_products = [product for product, timestamp in self.product_dict.items() if current_time - timestamp > 180]
                for product in expired_products:
                    del self.product_dict[product]
                    print(f"Removed Product: {product}")

    async def is_product_tracked(self, product):
        async with self.lock:
            return product in self.product_dict

    async def start_tracking(self):
        asyncio.create_task(self.remove_expired_asins())

# async def scrape_product(asin):
#     # Simulate scraping delay
#     await asyncio.sleep(1)
#     print(f"Scraping product: {asin}")

# async def scrape_products(asins, tracker):
#     for asin in asins:
#         if await tracker.is_asin_tracked(asin):
#             print(f"Skipping ASIN: {asin} (already tracked)")
#             continue
#         await tracker.add_product(asin)
#         await scrape_product(asin)

# async def main():
#     tracker = ProductTracker()
#     await tracker.start_tracking()

#     asins_to_scrape = ['B000123', 'B000456', 'B000123', 'B000789', 'B000456']  # Example ASINs

#     await scrape_products(asins_to_scrape, tracker)

# # Run the main function
# asyncio.run(main())
