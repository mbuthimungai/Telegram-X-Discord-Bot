import os
import re
import asyncio
import base64
import logging
import urlexpander
import aiohttp
from urllib.parse import unquote, urlparse, urljoin
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from helpers.user_agent_gen import userAgents



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LinkResolver:
    def __init__(self, ):                
        self.ignore_list = [
            'www.amazon.com', 'www.instagram.com', 'http://glitchndealz.com',
            'https://freebieflow.com/', 'https://www.woot.com/?ref=',
            'https://www.edealinfo.com', "http://thefreebieguy.com/"
        ]
        self.endpoint_list = [
            'https://www.amazon.com/dp/', 'https://www.amazon.com/gp/',
            'https://www.walmart.com/ip/', 'https://www.amazon.com/promocode/',
            'https://tools.woot.com', 'https://www.bestbuy.com', 
            'https://www.woot.com/', 'https://www.kohls.com/product/', 
            'https://www.macys.com/shop/'
        ]
        self.retry_attempts = 3 

    async def resolve_url(self, url, attempt=1):
        # Ensure url is a valid string
        if not isinstance(url, str) or not url.strip():
            logger.error("Invalid URL: URL must be a non-empty string.")
            return {'url': None, 'resolved': False}

        # Check for ignored or bot-protected URLs
        if self.should_ignore_url(url) or await self.is_bot_protected(url):
            return {'url': url, 'resolved': True}

        # Initial resolution attempt
        resolved_url, was_resolved = await self.initial_resolution(url)

        # Check resolution status
        if was_resolved:
            return {'url': resolved_url, 'resolved': True}

        # Retry mechanism
        if attempt < self.retry_attempts:
            await asyncio.sleep(1)  # Simple delay before retrying
            return await self.resolve_url(url, attempt + 1)

        # Return the original URL if all attempts fail
        return {'url': url, 'resolved': False}


    def is_endpoint_url(self, url):
        # Ensure url is not None before attempting to iterate
        if url is None:
            return False  # If url is None, it's safe to assume it's not an endpoint URL
        return any(endpoint in url for endpoint in self.endpoint_list)

    async def initial_resolution(self, url):
        if url is None:
            return None, False

        original_url = url

        # Attempt to expand shortened URL
        expanded_url = await self.expand_shortened_url(url)
        url = expanded_url if expanded_url else url
        
        # Check if the expanded URL is an endpoint
        if self.is_endpoint_url(url):
            return url, True if url != original_url else False
        
        # Decode URLs if needed (e.g., for sites that block direct scraping)
        decoded_url = await self.decode_url_if_needed(url)
        url = decoded_url if decoded_url else url
        
        # Check again if the decoded URL is an endpoint
        if self.is_endpoint_url(url):
            return url, True if url != original_url else False

        # Handle special cases (you'll need to implement the logic for this method)
        special_case_url = await self.handle_special_cases(url)
        url = special_case_url if special_case_url else url

        # Check if URL has changed after handling special cases
        if url != original_url:
            return url, True

        # If URL has not changed after special case handling, attempt resolution with JavaScript
        js_resolved_url = await self.resolve_url_using_js(url)
        if js_resolved_url and js_resolved_url != url:
            return js_resolved_url, True

        # Attempt resolution with Playwright for bot-protected sites
        playwright_resolved_url = await self.resolve_url_with_playwright_stealth(url)
        if playwright_resolved_url and playwright_resolved_url != url:
            return playwright_resolved_url, True

        # If none of the above methods changed the URL, return the original with False to indicate no resolution
        return original_url, True
    
    async def expand_shortened_url(self, url):
        # Validate that the URL is a string and not empty or None
        if not isinstance(url, str) or not url.strip():
            logger.error("URL must be a string and cannot be empty.")
            return None

        # Replace backslashes with forward slashes and ensure the URL starts with http:// or https://
        url = url.replace('\\', '/')
        if not re.match(r'^https?://', url):
            logger.error(f"Invalid URL format: {url}. URL must start with http:// or https://")
            return None

        # Skip URLs marked with a client error
        if '__CLIENT_ERROR__' in url:
            logger.error(f"URL contains error marker, skipping: {url}")
            return None

        try:
            async with aiohttp.ClientSession() as session:
                session.max_redirects = 20  # Set a limit on the maximum number of redirects
                while True:
                    try:
                        async with session.head(url, allow_redirects=True, timeout=10) as response:
                            if response.status in (301, 302, 307, 308):
                                # Follow redirects if the status code indicates a redirection
                                next_url = response.headers.get('Location')
                                if not next_url:
                                    logger.error(f"No 'Location' header found for redirect from {url}")
                                    break
                                # Make sure the next URL is absolute
                                next_url = next_url if next_url.startswith('http') else urljoin(url, next_url)
                                logger.info(f"Redirected: {response.status} - {next_url}")
                                url = next_url
                            else:
                                # Once no more redirects, return the final URL
                                return str(response.url)
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout while resolving URL: {url}. Using last known URL.")
                        return url  # Use the last known good URL on timeout
        except aiohttp.ClientError as e:
            logger.error(f"Error while expanding URL {url}: {e}")
            return None  # Return None in case of client errors

        return url 

    
    async def resolve_urls_concurrently(self, urls):
        return await asyncio.gather(*(self.resolve_url(url) for url in urls))
    
    def should_ignore_url(self, url):
        return any(domain in url for domain in self.ignore_list)

    def is_endpoint_url(self, url):
        return any(endpoint in url for endpoint in self.endpoint_list)
    
    def extract_asin_from_url(self, url):
        # Extract ASIN from Amazon URL
        match = re.search(r"(?:/dp/|/gp/product/)(B[0-9A-Z]{9})", url)
        if match:
            return match.group(1)
        return None
        
    async def is_ignored_or_blocked(self, url):
        # Check if the URL is in the ignore list or identified as blocked by bot protection
        return self.should_ignore_url(url) or await self.is_bot_protected(url)

    async def decode_url_if_needed(self, url):
        if 'www.walmart.com/blocked?url=' in url:
            return await self.decode_walmart_link(url)
        return url

    async def handle_special_cases(self, url, ignore_list=None, endpoint_list=None):
        if ignore_list is None:
            ignore_list = self.ignore_list
        if endpoint_list is None:
            endpoint_list = self.endpoint_list
        if 'bizrate.com' in url:
            return self.decode_and_extract_bizrate_url(url)
        elif 'shopstyle.com' in url:
            return self.decode_and_extract_shopstyle_url(url)
        elif 'facebook.com' in url:
            return await self.resolve_facebook_link(url)  # Handle Facebook links
        elif await self.is_bot_protected(url):
            return url
        return await self.resolve_url_with_playwright_stealth(url)
    
    async def retry_with_expansion(self, url, attempt):
        try:
            expanded_url = urlexpander.expand(url)
            return await self.resolve_url(expanded_url, attempt + 1)
        except Exception as e:
            print(f"Error expanding URL with urlexpander: {e}")
            return url  # Fallback to original URL if expansion fails

    @staticmethod
    async def resolve_url_using_js(url):
        if 'facebook' in url:
            return None, None  # Skip resolving Facebook links

        if 'walmart' in url:
            captured_url = await LinkResolver.decode_walmart_link(url)
            return captured_url, None

        if 'amazon' in url:
            url = url.split('&')[0]
            return url, None

        # Prepare the command
        cmd = ["node", os.path.join("js", "resolve_url.js"), f"{url}&user_agent=my_user_agent"]

        # Execute the command asynchronously
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            text=True  # Set text=True to handle stdout and stderr as strings
        )

        stdout, stderr = await proc.communicate()  # Wait for the subprocess to finish

        if proc.returncode == 0:
            return stdout.strip(), None
        else:
            return None, stderr.strip()
    async def resolve_url_with_playwright_stealth(self, url, timeout=90000, headless=True):
        if not url or not url.startswith(('http://', 'https://')):
            logger.error(f"Invalid or empty URL passed to Playwright: {url}")
            return None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=headless)                
                selected_user_agent = userAgents()
                context = await browser.new_context(user_agent=selected_user_agent)
                page = await context.new_page()

                # Apply stealth techniques to the page to evade detection.
                await stealth_async(page)

                try:
                    await page.goto(url, wait_until='load', timeout=timeout)
                    resolved_url = page.url
                except TimeoutError as e:
                    logger.error(f"Navigation timeout for URL {url}: {e}")
                    resolved_url = None
                except Exception as e:
                    logger.error(f"Error navigating to URL {url}: {e}")
                    resolved_url = None
                finally:
                    await page.close()
                    await context.close()
                    await browser.close()
                return resolved_url
        except Exception as e:
            logger.error(f"General error with Playwright stealth: {e}")
            return None
        
    @staticmethod
    async def decode_walmart_link(url):
        try:
            # Extract the portion after "url="
            url_param_start = url.find("url=")
            if url_param_start != -1:
                # Find the end of the base64-encoded string
                url_param_end = url.find("&", url_param_start)
                base64_encoded_url = url[url_param_start + 4 : url_param_end] if url_param_end != -1 else url[url_param_start + 4:]

                # Remove any additional characters that might interfere with decoding
                base64_encoded_url = base64_encoded_url.split('?')[0].split('&')[0]

                # Base64 decode the URL
                decoded_path_and_query = base64.b64decode(base64_encoded_url).decode('utf-8', 'ignore')

                # Construct the full Walmart URL
                walmart_base_url = "https://www.walmart.com"
                final_url = walmart_base_url + decoded_path_and_query

                #print(f"Decoded Walmart URL after base64 decoding: {final_url}")

                return final_url

        except Exception as e:
            print(f"Error decoding Walmart URL: {e}")

        # Return the original URL if decoding fails
        return url 

    @staticmethod
    def decode_and_extract_bizrate_url(encoded_url):
        decoded_url = unquote(encoded_url)
        while '%3A' in decoded_url or '%2F' in decoded_url or '%3D' in decoded_url or '%26' in decoded_url:
            decoded_url = unquote(decoded_url)
        target_url_match = re.search(r'url=([^&]+)', decoded_url)
        return unquote(target_url_match.group(1)) if target_url_match else None
        pass

    @staticmethod
    def decode_and_extract_shopstyle_url(encoded_url):
        decoded_url = unquote(encoded_url)
        while '%3A' in decoded_url or '%2F' in decoded_url or '%3D' in decoded_url or '%26' in decoded_url:
            decoded_url = unquote(decoded_url)
        target_url_match = re.search(r'url=([^&]+)', decoded_url)
        return unquote(target_url_match.group(1)) if target_url_match else None
        pass

    @staticmethod
    async def is_bot_protected(url):
        # Patterns that indicate a URL is blocked due to bot protection
        bot_protection_patterns = [
            r'www\.walmart\.com/blocked\?url=',  
            r'www\.amazon\.com/errors/404\.html',  
            r'%5C__CLIENT_ERROR__$',
            r'%5C__CLIENT_ERROR',
            r'__CONNECTIONPOOL_ERROR__',
            r'__CLIENT_ERROR__' 
        ]

        # Check if the URL matches any of the bot protection patterns
        if any(re.search(pattern, url) for pattern in bot_protection_patterns):
            #print(f"Bot protection detected for URL: {url}")
            return True

        return False
    
    @staticmethod
    async def resolve_facebook_link(facebook_url):
        try:
            # Parse the Facebook URL
            parsed_url = urlparse(facebook_url)

            # Extract the path parts from the URL
            path_parts = parsed_url.path.split('/')

            # Identify the type of Facebook link
            link_type = path_parts[1] if len(path_parts) > 1 else None

            # Extract relevant information based on the link type
            if link_type == 'groups':
                # For group links
                group_name = path_parts[2]

                # Scrape links from the post
                content, post_links = await LinkResolver.scrape_facebook_post_content(facebook_url)

                # Return the results
                return group_name, post_links, content
            elif link_type == 'pages':
                # For page links
                page_name = path_parts[2]

                # Scrape links from the post
                content, post_links = await LinkResolver.scrape_facebook_post_content(facebook_url)

                # Return the results
                return page_name, post_links, content
            else:
                # For other types of links
                post_links = await LinkResolver.scrape_facebook_post_content(facebook_url)

                # Return the results
                return "Generic", post_links, content

        except Exception as e:
            print(f"Error resolving Facebook link: {e}")

        # Return None if resolution fails
        return None


    
    async def scrape_facebook_post_content(facebook_url):
        content = ""
        extracted_links = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context()
                page = await context.new_page()

                try:
                    await page.goto(facebook_url, timeout=60000)
                    await page.wait_for_load_state('networkidle', timeout=60000)
                    content = await page.evaluate('() => document.body.innerText')                    
                    # Extract URLs from the content using regex
                    urls = re.findall(r'https?://[^\s]+', content)
                    extracted_links.extend(urls)
                    
                except asyncio.TimeoutError:
                    print("Page load timed out. Attempting to extract available content...")
                except Exception as e:
                    print(f"Error navigating to page: {e}")
                finally:
                    await context.close()
                    await browser.close()                

        except Exception as e:
            print(f"Error scraping Facebook post content: {e}")

        return content, extracted_links






