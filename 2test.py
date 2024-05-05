from urllib.parse import urlparse


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

domain_ = "https://www.amazon.com/dp/B001GMY7AA"

print(domain(domain_))