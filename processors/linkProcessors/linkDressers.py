import re, aiohttp, ssl, certifi
from urllib.parse import urlparse, parse_qs, urlencode

class LinkDresser:
    # async def clean_link(self, url):
    #     if 'amazon.com' in url:
    #         return await self.clean_amazon_link(url)
    #     elif 'walmart.com' in url:
    #         return await self.clean_walmart_link(url)
    #     elif 'bestbuy.com' in url:
    #         return await self.clean_bestbuy_link(url)
    #     elif 'lowes.com' in url:
    #         return await self.clean_lowes_link(url)
    #     elif 'ulta.com' in url:
    #         return await self.clean_ulta_link(url)
    #     else:
    #         return await self.expand_shortened_url(url)


    async def clean_amazon_link(self, url):
        # Define regex patterns
        amazon_product_regex = r'https?://www\.amazon\.com/(?:dp|gp/product)/([A-Z0-9]+)'
        amazon_promocode_regex = r'https?://www\.amazon\.com/promocode/([A-Z0-9]+)'
        amazon_search_regex = r'https?://www\.amazon\.com/s\?k=([^&]+)'

        # Tags to remove from the URL
        tags_to_remove = ['ref', 'ref_' 'brr', 'crid', 'SubscriptionId', 'fbclid', 'linkCode', 'ascsubtag',
                        'psc', 'm', 'tag', 'marketplaceID', 'qid', 's', 'sr', 'th', 'language', 'pf_rd_i', 'linkId',
                        'pf_rd_r', 'pf_rd_t', 'pf_rd_p', '_encoding', 'smid', 'geniuslink', 'starsLeft', 'maas', '?ref_=as_li_ss_tl',
                        '&linkCode', 'refinements', 'sbo', 'pf_rd_s', 'dib', 'url', 'dib_tag', 'keywords', 'pf_rd_i', 'rnid']


        # Parse the URL to easily manipulate query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Remove specified tags from query parameters
        cleaned_params = {key: value for key, value in query_params.items() if key not in tags_to_remove}

        # Initialize cleaned_url with the original URL
        cleaned_url = url

        # Check for Amazon product, promocode, or search URLs and simplify them
        if re.search(amazon_product_regex, url):
            asin = re.search(amazon_product_regex, url).group(1)
            cleaned_url = f'https://www.amazon.com/dp/{asin}'
        elif re.search(amazon_promocode_regex, url):
            promocode = re.search(amazon_promocode_regex, url).group(1)
            cleaned_url = f'https://www.amazon.com/promocode/{promocode}'
        elif re.search(amazon_search_regex, url):
            search_query = re.search(amazon_search_regex, url).group(1)
            cleaned_url = f'https://www.amazon.com/s?k={search_query}'
        else:
            # If no specific patterns matched, reconstruct the original URL without the removed query parameters
            cleaned_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

        # For product, promocode, and search URLs, append cleaned query parameters if they exist
        if cleaned_params:
            query_string = urlencode(cleaned_params, doseq=True)
            cleaned_url += "?" + query_string if query_string else ""

        return cleaned_url

    async def clean_walmart_link(self, url):
        walmart_regex = r'(https://www\.walmart\.com/ip/[^\s/]+)'
        match = re.match(walmart_regex, url)
        if match:
            product_id = re.findall(r'/(\d+)', url)
            return f"https://www.walmart.com/ip/{product_id[0]}" if product_id else url
        return url
    
    async def clean_bestbuy_link(self, url):
        # Regular expression to extract the essential part of a Best Buy URL
        bestbuy_regex = r'https://www\.bestbuy\.com/site/(.*?)(?:\?|$)'
        match = re.search(bestbuy_regex, url)
        if match:
            path_segment = match.group(1)
            return f"https://www.bestbuy.com/site/{path_segment}"
        return url

    async def clean_lowes_link(self, url):
        # Regular expression to extract the essential part of a Lowe's URL
        lowes_regex = r'https://www\.lowes\.com/pd/[^/]+/(\d+)'
        match = re.search(lowes_regex, url)
        if match:
            product_id = match.group(1)
            return f"https://www.lowes.com/pd/p/{product_id}"
        return url

    async def clean_ulta_link(self, url):
        # Remove query parameters from Ulta URL
        url_parts = url.split("?")
        return url_parts[0] if url_parts else url

    async def expand_shortened_url(self, url):
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())

            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                async with session.head(url, allow_redirects=True) as response:
                    return str(response.url)
        except aiohttp.ClientError as e:
            print(f"Error expanding shortened URL: {e}")
            return url  # Fallback to original UR