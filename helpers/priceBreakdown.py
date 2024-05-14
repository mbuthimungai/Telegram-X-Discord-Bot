class PriceBreakDown:
    def __init__(self) -> None:
        pass
    
    async def price_discounter(self, retail_price: float, discount_data: float,
                               promo_discount: float, savings_percentage: float, 
                               promo_code: str, is_price_dollars: bool, more_discount_data: str):
#         List Price: 29.99
# Clip coupon: $10
# Deal Price: $19.99
# Promo Code: 7GWUYJ9K 
# Promo Discount: Missing
# Checkout Price: Missing
        print(f"Promo discount: {promo_discount}")
        print(f"Promo code: {promo_code}")
        if retail_price is None or not isinstance(retail_price, (int, float)):
            retail_price = 0.0
        
        price_breakdown_dict = {"Items": f'${retail_price:.2f}'}
        initial_price = retail_price 
                
        if savings_percentage is not None and isinstance(savings_percentage, (int, float)) and savings_percentage != 0:
            discounted_price = (savings_percentage * retail_price) / 100
            price_breakdown_dict[f'savings percentage -{savings_percentage}%'] = f'-${discounted_price:.2f}'
            retail_price -= discounted_price
        
        # Apply discount data based on whether it is a percent or fixed amount
        if more_discount_data is not None and isinstance(discount_data, (int, float)) and more_discount_data != 0:
            
            if is_price_dollars:
                discounted_price = more_discount_data
                price_breakdown_dict[f'$-{more_discount_data} off'] = f'-${discounted_price:.2f}'
            else:                
                discounted_price = (more_discount_data * retail_price) / 100
                price_breakdown_dict[f'{more_discount_data}% off'] = f'-${discounted_price:.2f}'
                
            retail_price -= discounted_price
        
        if discount_data is not None and isinstance(discount_data, (int, float)) and discount_data != 0:
            discounted_price = (discount_data * retail_price) / 100
            price_breakdown_dict[f'{discount_data}% off'] = f'-${discounted_price:.2f}'
            retail_price -= discounted_price

        if promo_discount is not None and isinstance(promo_discount, (int, float)) and promo_discount != 0 and promo_code:
            discounted_price = (promo_discount * retail_price) / 100
            price_breakdown_dict[promo_code] = f'-${discounted_price:.2f}'
            retail_price -= discounted_price
        
        if retail_price != initial_price:
            price_breakdown_dict["Total"] = f'${retail_price:.2f}'        
        
        return price_breakdown_dict, retail_price
        
