import asyncio


class PriceBreakDown:
    def __init__(self) -> None:
        pass
    
    async def price_discounter(self, retail_price: float, discount_data: float,
                               promo_discount: float, savings_percentage: float, 
                               promo_code: str, is_price_dollars: bool, more_discount_data: float,
                               more_discount_data_save: float):
        
        print(f"Promo discount: {promo_discount}")
        print(f"Promo code: {promo_code}")
        if retail_price is None or not isinstance(retail_price, (int, float)):
            retail_price = 0.0
        
        price_breakdown_dict = {"Items": f'${retail_price:.2f}'}
        initial_price = retail_price 
        price_to_discount = retail_price
        
        
        def apply_discount(price, discount, is_dollar, description):
            if discount is not None and isinstance(discount, (int, float)) and discount != 0:
                print(discount)
                if is_dollar:
                    discounted_price = discount
                    description = f'{description}: $-{discount:.2f} off'
                else:
                    discounted_price = (discount * price_to_discount) / 100
                    description = f'{description}: {discount}% off'
                price -= discounted_price
                
                price_breakdown_dict[description] = f'-${discounted_price:.2f}'
            return price

        # Apply savings percentage discount
        retail_price = apply_discount(retail_price, savings_percentage, False, f'Savings percentage -{savings_percentage}%')
        
        # Apply more discount data
        retail_price = apply_discount(retail_price, more_discount_data, is_price_dollars, 'Discount 1 page')
        
        # Apply more discount data save
        retail_price = apply_discount(retail_price, more_discount_data_save, is_price_dollars, 'Discount 2 page')
        
        # Apply discount data
        retail_price = apply_discount(retail_price, discount_data, False, f'Discount: {discount_data}% off')
        
        # Apply promo discount
        if promo_code:
            retail_price = apply_discount(retail_price, promo_discount, False, promo_code)
        
        if retail_price != initial_price:
            price_breakdown_dict["Total"] = f'${retail_price:.2f}'        
        
        return price_breakdown_dict, retail_price


async def main():    
    # Example usage
    price_breakdown = PriceBreakDown()
    r = await price_breakdown.price_discounter(100, 10, 0, 20, "PROMO2024", False, 15, 5)
    print(r)
if __name__ == "__main__":
    asyncio.run(main())