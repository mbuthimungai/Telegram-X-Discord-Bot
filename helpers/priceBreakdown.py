# class PriceBreakDown:
#     def __init__(self) -> None:
#         pass
    
#     async def price_discounter(self, retail_price: float, discount_data: float,
#                                promo_discount: float, savings_percentage: float, 
#                                promo_code: str, is_price_dollars: bool, more_discount_data: str,
#                                more_discount_data_save: str):
        
#         print(f"Promo discount: {promo_discount}")
#         print(f"Promo code: {promo_code}")
#         if retail_price is None or not isinstance(retail_price, (int, float)):
#             retail_price = 0.0
        
#         price_breakdown_dict = {"Items": f'${retail_price:.2f}'}
#         initial_price = retail_price 
                
#         if savings_percentage is not None and isinstance(savings_percentage, (int, float)) and savings_percentage != 0:
#             discounted_price = (savings_percentage * initial_price) / 100
#             price_breakdown_dict[f'savings percentage -{savings_percentage}%'] = f'-${discounted_price:.2f}'
#             retail_price -= discounted_price
        
#         # Apply discount data based on whether it is a percent or fixed amount
#         if more_discount_data is not None and more_discount_data != 0:
            
#             if is_price_dollars:
#                 discounted_price = more_discount_data
#                 price_breakdown_dict[f'Discount 1 page: $-{more_discount_data} off'] = f'-${discounted_price:.2f}'
#             else:                
#                 discounted_price = (more_discount_data * initial_price) / 100
#                 price_breakdown_dict[f'Discount 1 page: {more_discount_data}% off'] = f'-${discounted_price:.2f}'
                
#             retail_price -= discounted_price
        
#         if more_discount_data_save is not None and more_discount_data_save != 0:
            
#             if is_price_dollars:
#                 discounted_price = more_discount_data_save
#                 price_breakdown_dict[f'Discount 2 page: $-{more_discount_data_save} off'] = f'-${discounted_price:.2f}'
#             else:                
#                 discounted_price = (more_discount_data_save * initial_price) / 100
#                 price_breakdown_dict[f'Discount 2 page: {more_discount_data_save}% off'] = f'-${discounted_price:.2f}'
                
#             retail_price -= discounted_price
        
#         if discount_data is not None and isinstance(discount_data, (int, float)) and discount_data != 0:
#             discounted_price = (discount_data * initial_price) / 100
#             price_breakdown_dict[f'Discount: {discount_data}% off'] = f'-${discounted_price:.2f}'
#             retail_price -= discounted_price

#         if promo_discount is not None and isinstance(promo_discount, (int, float)) and promo_discount != 0 and promo_code:
#             discounted_price = (promo_discount * initial_price) / 100
#             price_breakdown_dict[promo_code] = f'-${discounted_price:.2f}'
#             retail_price -= discounted_price
        
#         if retail_price != initial_price:
#             price_breakdown_dict["Total"] = f'${retail_price:.2f}'        
        
#         return price_breakdown_dict, retail_price
    
# from utils.extract_number import extract_number

# class PriceBreakDown:
#     def __init__(self) -> None:
#         pass
    
#     async def price_discounter(self, retail_price: float, discount_data: float,
#                                promo_discount: float,  
#                                promo_code: str, is_price_dollars: bool, more_discount_data: float,
#                                more_discount_data_save: float, deal_price: str):
        
#         print(f"Promo discount: {promo_discount}")
#         print(f"Promo code: {promo_code}")
#         if retail_price is None or not isinstance(retail_price, (int, float)):
#             retail_price = 0.0
        
#         price_breakdown_dict = {"Items": f'${retail_price:.2f}'}
#         initial_price = retail_price 
#         total_percentage_discount = 0.0
        
#         def apply_discount(price, discount, is_dollar, description):
#             nonlocal total_percentage_discount
#             if discount is not None and isinstance(discount, (int, float)) and discount != 0:
#                 if is_dollar:
#                     discounted_price = discount
#                     description = f'{description}: $-{discount:.2f} off'
#                 else:
#                     discounted_price = (discount * initial_price) / 100
#                     total_percentage_discount += discount
#                     description = f'{description}: {discount}% off'
#                 price -= discounted_price
#                 price_breakdown_dict[description] = f'-${discounted_price:.2f}'
#             return price

#         # Apply savings percentage discount
#         # retail_price = apply_discount(retail_price, savings_percentage, False, f'Savings percentage -{savings_percentage}%')
#         # if abs(retail_price - initial_price) <= 1:
#         #     return price_breakdown_dict, retail_price, total_percentage_discount

#         # Apply more discount data
#         retail_price = apply_discount(retail_price, more_discount_data, is_price_dollars, 'Discount 1 page')
#         if abs(retail_price - deal_price) <= 1:
#             return price_breakdown_dict, retail_price, total_percentage_discount

#         # Apply more discount data save
#         retail_price = apply_discount(retail_price, more_discount_data_save, is_price_dollars, 'Discount 2 page')
#         if abs(retail_price - deal_price) <= 1:
#             return price_breakdown_dict, retail_price, total_percentage_discount

#         # Apply discount data
#         retail_price = apply_discount(retail_price, discount_data, False, f'Discount: {discount_data}% off')
#         if abs(retail_price - deal_price) <= 1:
#             return price_breakdown_dict, retail_price, total_percentage_discount

#         # Apply promo discount
#         if promo_code:
#             retail_price = apply_discount(retail_price, promo_discount, False, promo_code)
#             if abs(retail_price - deal_price) <= 1:
#                 return price_breakdown_dict, retail_price, total_percentage_discount
        
#         deal_price = await extract_number(str(deal_price))
        
#         if deal_price:
#             deal_price = float(deal_price)
#             if not abs(deal_price - retail_price) <= 1:
#                 if not promo_discount:
#                     percentage_change = ((deal_price - retail_price) / retail_price) * 100
#                     if promo_code:
#                         price_breakdown_dict[f"{promo_code} Percentage Change"] = f'{percentage_change:.2f}%'
#                     else:
#                         price_breakdown_dict["Additional Percentage Change"] = f'{percentage_change:.2f}%'
#                     retail_price = deal_price

#         if retail_price != initial_price:
#             price_breakdown_dict["Total"] = f'${retail_price:.2f}'
        
#         return price_breakdown_dict, retail_price, total_percentage_discount

# from utils.extract_number import extract_number

# class PriceBreakDown:
#     def __init__(self) -> None:
#         pass
    
#     async def price_discounter(self, retail_price: float, discount_data: float,
#                                promo_discount: float,  
#                                promo_code: str, is_price_dollars: bool, more_discount_data: float,
#                                more_discount_data_save: float, deal_price: str):
        
#         print(f"Promo discount: {promo_discount}")
#         print(f"Promo code: {promo_code}")
#         if retail_price is None or not isinstance(retail_price, (int, float)):
#             retail_price = 0.0
        
#         price_breakdown_dict = {"Items": f'${retail_price:.2f}'}
#         initial_price = retail_price 
#         total_percentage_discount = 0.0
#         price_before_zero = initial_price
        
#         def apply_discount(price, discount, is_dollar, description):
#             nonlocal total_percentage_discount, price_before_zero
#             if discount is not None and isinstance(discount, (int, float)) and discount != 0:
#                 price_before_zero = price  # Store price before applying discount
#                 if is_dollar:
#                     discounted_price = discount
#                     description = f'{description}: $-{discount:.2f} off'
#                 else:
#                     discounted_price = (discount * initial_price) / 100
#                     total_percentage_discount += discount
#                     description = f'{description}: {discount}% off'
#                 price -= discounted_price
#                 if price <= 0:
#                     return 0, price_before_zero
#                 price_breakdown_dict[description] = f'-${discounted_price:.2f}'
#             return price, price_before_zero

#         # Apply more discount data
#         retail_price, price_before_zero = apply_discount(retail_price, more_discount_data, is_price_dollars, 'Discount 1 page')
#         if abs(retail_price - deal_price) <= 1 or retail_price == 0:
#             return price_breakdown_dict, price_before_zero, total_percentage_discount

#         # Apply more discount data save
#         retail_price, price_before_zero = apply_discount(retail_price, more_discount_data_save, is_price_dollars, 'Discount 2 page')
#         if abs(retail_price - deal_price) <= 1 or retail_price == 0:
#             return price_breakdown_dict, price_before_zero, total_percentage_discount

#         # Apply discount data
#         retail_price, price_before_zero = apply_discount(retail_price, discount_data, False, f'Discount: {discount_data}% off')
#         if abs(retail_price - deal_price) <= 1 or retail_price == 0:
#             return price_breakdown_dict, price_before_zero, total_percentage_discount

#         # Apply promo discount
#         if promo_code:
#             retail_price, price_before_zero = apply_discount(retail_price, promo_discount, False, promo_code)
#             if abs(retail_price - deal_price) <= 1 or retail_price == 0:
#                 return price_breakdown_dict, price_before_zero, total_percentage_discount
        
#         deal_price = await extract_number(str(deal_price))
        
#         if deal_price:
#             deal_price = float(deal_price)
#             if not abs(deal_price - retail_price) <= 1:
#                 if not promo_discount:
#                     percentage_change = ((deal_price - retail_price) / retail_price) * 100
#                     if promo_code:
#                         price_breakdown_dict[f"{promo_code} Percentage Change"] = f'{percentage_change:.2f}%'
#                     else:
#                         price_breakdown_dict["Additional Percentage Change"] = f'{percentage_change:.2f}%'
#                     retail_price = deal_price

#         if retail_price != initial_price:
#             price_breakdown_dict["Total"] = f'${retail_price:.2f}'
        
#         return price_breakdown_dict, retail_price, total_percentage_discount


from utils.extract_number import extract_number

class PriceBreakDown:
    def __init__(self) -> None:
        pass
    
    async def price_discounter(self, retail_price: float, discount_data: float,
                               promo_discount: float,  
                               promo_code: str, is_price_dollars: bool, more_discount_data: float,
                               more_discount_data_save: float, deal_price: str,
                               savings_percentage: str=0):
        
        print(f"Promo discount: {promo_discount}")
        print(f"Promo code: {promo_code}")
        if retail_price is None or not isinstance(retail_price, (int, float)):
            retail_price = 0.0
        
        price_breakdown_dict = {"Items": f'${retail_price:.2f}'}
        initial_price = retail_price 
        total_percentage_discount = 0.0
        price_before_zero = initial_price
        
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

        # Apply price drop (savings percentage)
        retail_price = apply_discount(retail_price, savings_percentage, is_price_dollars, 'Price drop')
        if retail_price <= 0:
            return price_breakdown_dict, price_before_zero, total_percentage_discount
        if abs(retail_price - deal_price) <= 1:
            return price_breakdown_dict, retail_price, total_percentage_discount
        
        # Apply more discount data
        retail_price = apply_discount(retail_price, more_discount_data, is_price_dollars, 'Discount 1 page')
        if retail_price <= 0:
            return price_breakdown_dict, price_before_zero, total_percentage_discount
        if abs(retail_price - deal_price) <= 1:
            return price_breakdown_dict, retail_price, total_percentage_discount

        # Apply more discount data save
        retail_price = apply_discount(retail_price, more_discount_data_save, is_price_dollars, 'Discount 2 page')
        if retail_price <= 0:
            return price_breakdown_dict, price_before_zero, total_percentage_discount
        if abs(retail_price - deal_price) <= 1:
            return price_breakdown_dict, retail_price, total_percentage_discount

        # Apply discount data
        retail_price = apply_discount(retail_price, discount_data, False, f'Discount: {discount_data}% off')
        if retail_price <= 0:
            return price_breakdown_dict, price_before_zero, total_percentage_discount
        if abs(retail_price - deal_price) <= 1:
            return price_breakdown_dict, retail_price, total_percentage_discount

        # Apply promo discount
        if promo_code:
            retail_price = apply_discount(retail_price, promo_discount, False, promo_code)
            if retail_price <= 0:
                return price_breakdown_dict, price_before_zero, total_percentage_discount
            if abs(retail_price - deal_price) <= 1:
                return price_breakdown_dict, retail_price, total_percentage_discount
        
        deal_price = await extract_number(str(deal_price))
        
        if deal_price:
            deal_price = float(deal_price)
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
