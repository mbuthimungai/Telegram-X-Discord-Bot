from requests_html import AsyncHTMLSession
import secrets


class Response:
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = AsyncHTMLSession()
                
    async def content_html(self):
        
        headers = {"User-Agent": user_agents()}
        
        response = await self.session.get(self.base_url, headers=headers)
        response.raise_for_status()
        
        return response.text


def random_values(d_lists):
    idx = secrets.randbelow(len(d_lists))
    return d_lists[idx]

def user_agents():
    with open('user-agents.txt') as f:
        agents = f.read().split("\n")
        return random_values(agents).strip()