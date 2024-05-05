async def convert_to_ints(data):
    int_discounts = []
    for sublist in data:
        int_sublist = []
        for item in sublist:
            if isinstance(item, str):
                
                numeric_part = ''.join(filter(str.isdigit, item))
                if numeric_part:
                
                    int_sublist.append(int(numeric_part))
            elif isinstance(item, (int, float)):
                
                int_sublist.append(int(item))
            else:
                
                int_sublist.append(None)
        int_discounts.append(int_sublist)
    return int_discounts
