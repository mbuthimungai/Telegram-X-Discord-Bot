import re

async def extract_number(input_string):
    """
    Extracts the first numerical value from a string that may contain non-numeric characters.

    Args:
    - input_string (str): The string from which to extract the number.

    Returns:
    - float: The first floating-point number found in the string. Returns None if no number is found.
    """
    # Use regular expression to find numbers, including decimals
    match = re.search(r"[-+]?\d*\.\d+|\d+", input_string)
    if match:
        return float(match.group())
    else:
        return None
    
# print(extract_number('5%'))

import asyncio

# Assuming the utils.extract_number function is properly defined and imported

class PriceBreakDown:
    def __init__(self) -> None:
        pass
    
    async def price_discounter(self, retail_price: float, discount_data: float,
                               promo_discount: float,  
                               promo_code: str, is_price_dollars: bool, more_discount_data: float,
                               more_discount_data_save: float, deal_price: str):
        
        print(f"Promo discount: {promo_discount}")
        print(f"Promo code: {promo_code}")
        if retail_price is None or not isinstance(retail_price, (int, float)):
            retail_price = 0.0
        
        price_breakdown_dict = {"Items": f'${retail_price:.2f}'}
        initial_price = retail_price 
        total_percentage_discount = 0.0
        price_before_zero = initial_price
        deal_price = await extract_number(str(deal_price))
        def apply_discount(price, discount, is_dollar, description):
            nonlocal total_percentage_discount, price_before_zero
            if discount is not None and isinstance(discount, (int, float)) and discount != 0:
                price_before_zero = price  # Store price before applying discount
                if is_dollar:
                    discounted_price = discount
                    description = f'{description}: $-{discount:.2f} off'
                else:
                    discounted_price = (discount * initial_price) / 100
                    total_percentage_discount += discount
                    description = f'{description}: {discount}% off'
                price -= discounted_price
                price_breakdown_dict[description] = f'-${discounted_price:.2f}'
            return price
        print(abs(retail_price - deal_price))
        # Apply more discount data
        retail_price = apply_discount(retail_price, more_discount_data, is_price_dollars, 'Discount 1 page')
        if retail_price == 0:
            return price_breakdown_dict, price_before_zero, total_percentage_discount
        if abs(retail_price - deal_price) <= 1:
            return price_breakdown_dict, retail_price, total_percentage_discount
        print(abs(retail_price - deal_price))
        print(price_breakdown_dict)
        # Apply more discount data save
        retail_price = apply_discount(retail_price, more_discount_data_save, is_price_dollars, 'Discount 2 page')
        if retail_price == 0:
            return price_breakdown_dict, price_before_zero, total_percentage_discount
        if abs(retail_price - deal_price) <= 1:
            return price_breakdown_dict, retail_price, total_percentage_discount
        print(abs(retail_price - deal_price))
        print(price_breakdown_dict)
        # Apply discount data
        retail_price = apply_discount(retail_price, discount_data, False, f'Discount: {discount_data}% off')
        if retail_price == 0:
            return price_breakdown_dict, price_before_zero, total_percentage_discount
        if abs(retail_price - deal_price) <= 1:
            return price_breakdown_dict, retail_price, total_percentage_discount
        print(abs(retail_price - deal_price))
        print(price_breakdown_dict)
        print('passed')
        # Apply promo discount
        if promo_code:
            retail_price = apply_discount(retail_price, promo_discount, False, promo_code)
            print(retail_price)
            print(abs(retail_price - deal_price))
            if retail_price == 0:
                return price_breakdown_dict, price_before_zero, total_percentage_discount
            if abs(retail_price - deal_price) <= 1:
                return price_breakdown_dict, retail_price, total_percentage_discount
        
        print('passed_1')
        
        if deal_price:
            if not abs(deal_price - retail_price) <= 1:
                if not promo_discount:
                    percentage_change = ((deal_price - retail_price) / retail_price) * 100
                    if promo_code:
                        price_breakdown_dict[f"{promo_code} Percentage Change"] = f'{percentage_change:.2f}%'
                    else:
                        price_breakdown_dict["Additional Percentage Change"] = f'{percentage_change:.2f}%'
                    retail_price = deal_price

        if retail_price != initial_price:
            price_breakdown_dict["Total"] = f'${retail_price:.2f}'
        
        return price_breakdown_dict, retail_price, total_percentage_discount

# Create an instance of PriceBreakDown
price_breakdown_instance = PriceBreakDown()

# Define the parameters
params = {
    "retail_price": 39.97,
    "discount_data": 0.0,  # No discount data provided
    "promo_discount": 10.0,
    "promo_code": "10CTUYT7",
    "is_price_dollars": True,
    "more_discount_data": 13.0,
    "more_discount_data_save": 0.0,  # No more discount data save provided
    "deal_price": "22.973"
}

# Run the function with the provided parameters
async def run():
    result = await price_breakdown_instance.price_discounter(**params)
    print(result)

# Execute the async function
asyncio.run(run())


