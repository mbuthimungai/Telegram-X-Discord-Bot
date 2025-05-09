from urllib.parse import urlparse
import itertools
import aiohttp
import secrets
import yaml
import re
import asyncio

proxy_username = "Ns634q1v"
proxy_password = "tJ79p4XS"
proxy_host = "172.120.40.15"
proxy_port = "64502"

proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

class Response:
    def __init__(self, base_url):
        """
        Initialize a Response object with a base URL.

        Args:
        - base_url (str): The base URL for the HTTP requests.
        """
        self.base_url = base_url


    async def content(self, retries=10):
        """
        Perform an asynchronous HTTP GET request with retries and return the response content.

        Parameters:
        - retries (int): Number of times to retry the request in case of failure.

        Returns:
        - bytes: The content of the HTTP response.
        """
        attempt = 0
        while attempt < retries:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {'User-Agent': userAgents()}
                    async with session.get(self.base_url, headers=headers) as resp:
                        cont = await resp.text()
                        # Check if the response contains the specific phrase
                        if resp.status == 200 and "please make sure your browser is accepting cookies" not in cont:                            
                            return cont
                        else:
                            attempt += 1
                            await asyncio.sleep(5)  # Wait for 5 seconds before retrying
                            print(f"Attempt {attempt}: Failed to fetch valid data, retrying...")
            except aiohttp.ClientError as e:
                print(f"Attempt {attempt}: HTTP Client Error occurred: {e}")
                attempt += 1
                await asyncio.sleep(5)  # Wait for 5 seconds before retrying
        raise Exception("Failed to fetch data after several retries")

    async def response(self):
        """
        Perform an asynchronous HTTP GET request and return the response status code.

        Returns:
        - int: The HTTP status code of the response.
        """
        async with aiohttp.ClientSession() as session:
            headers = {'User-Agent': userAgents()}
            async with session.get(self.base_url, headers = headers) as resp:
                cont = resp.status               
                return cont


class TryExcept:
    """
    A class containing methord for seafely extracting information from HTML elements.
    """
    async def text(self, element):
        """
        Returns the text content of an HTML element, or "N/A" if the element is not found.

        Args:
            -element: An HTML element object.

        Returns:
            -A string representing the text content of the elemen, or "N/A" if the element is not found.
        """
        try:
            elements = element.text.strip()
        except AttributeError:
            elements = "N/A"
        return elements

    async def attributes(self, element, attr):
        """
        Returns the value fo an attribute of an HTML element, of "N/A" if the attribute or element is not found.

        Args:
            -element: An HTML element object.
            -attr: A string representing the name of the attribute to extract.

        Returns:
             A string representing the value of the attribute, or "N/A" if the attribute or element is not found.
        """
        try:
            elements = element.get(attr)
        except AttributeError:
            elements = "N/A"
        return elements


def domain(url):
    """
    Extract the domain from a given URL.

    Args:
    - url (str): The URL from which to extract the domain.

    Returns:
    - str: The extracted domain.
    """
    domain = ""
    parsed_url = urlparse(url)
    raw_domain = parsed_url.netloc.split(".")
    if len(raw_domain) == 3:
        domain += raw_domain[-1]
    elif len(raw_domain) == 4:
        domain += ".".join(raw_domain[-2:])
    return domain


def filter(raw_lists):
    """
    Remove duplicates from a list.

    Args:
    - raw_lists (list): The input list containing potential duplicates.

    Returns:
    - list: A filtered list with duplicates removed.
    """
    filtered_lists = []
    for file in raw_lists:
        if not file in filtered_lists:
            filtered_lists.append(file)
    return filtered_lists


def flat(d_lists):
    """
    Flatten a multi-dimentional list.

    Args:
    - d_lists (list): A multi-dimensional list.

    Returns:
    - list: A flattened version of the input list.
    """
    return list(itertools.chain(*d_lists))


async def verify_amazon(url):
    """
    Verifies if the input URL is a vaild Amazon URL.

    Args:
        -url: A string representing the URL to verify.

    Returns:
        -True if the URL is invalid or False if it is valud.
    """
    amazon_pattern = re.search("""^(https://|www.)|amazon\.(com|co\.uk|pl|in|com\.br)(/s\?.|/b/.)+""", url)
    if amazon_pattern == None:
        return True
    else:
        pass


def random_values(d_lists):
    """
    Returns a random value from a list.

    Args
    """
    idx = secrets.randbelow(len(d_lists))
    return d_lists[idx]


async def randomTime(val):
    """
    Generates a random time interval between requests to avaoid overloading the server. Scrape resonponsibly.

    Args:
        -val: An interger representing the maxinum time interval in seconds.

    Returns:
        -A random interger between 2 and the input value. So, the default time interval is 2 seconds.
    """
    ranges = [i for i in range(0, val+1)]
    return random_values(ranges)


def userAgents():
    """
    Returns a random user agent string from a file containing a list of user agents.

    Args:
        -None

    Returns:
        -A string representing a ranom user agent.
    """
    with open('./user-agents.txt') as f:
        agents = f.read().split("\n")
        return random_values(agents)


def yaml_load(selectors):
    """
    Loads a YAML file containing selectors for web scraping.

    Args:
        -selectors: A string representing the name of the YAML file containing the selectors.

    Returns:
        -A dictionary containing the selectors.
    """
    with open(f"./APIcalls/amazon/scrapers/{selectors}.yaml") as file:
        sel = yaml.load(file, Loader=yaml.SafeLoader)
        return sel