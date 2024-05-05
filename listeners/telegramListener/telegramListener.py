from telethon import TelegramClient, events, connection
from telethon.tl.types import InputChannel
import re
import asyncio

from utils.logger import configure_logger

URL_REGEX = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'



class TelegramMessageRetriever:
    def __init__(self, config, message_callback):
        proxy = {
            'proxy_type': 'socks5', 
            'addr': config["proxy_host"],      
            'port': config["proxy_port"],           
            'username': config["proxy_username"],      
            'password': config["proxy_password"]  
            # 'rdns': True            
        }
        self.client = TelegramClient(config["key_session_name"], int(config["key_api_id"]), config["key_api_hash"], timeout=60, 
                                    proxy=proxy
                                    )
        self.message_callback = message_callback  # Ensure this is correctly set
        
        self.logger = configure_logger(__name__)

    async def process_messages(self):
        try:
            input_channels_entities = []
            for d in await self.client.get_dialogs():                                                    
                input_channels_entities.append(InputChannel(d.entity.id, d.entity.access_hash))
                
            # rest of your processing code
        except ConnectionError as e:
            print("Connection error occurred:", e)

        @self.client.on(events.NewMessage(chats=input_channels_entities))
        async def handler(event):
            # Extract URLs from the message text
            urls = re.findall(URL_REGEX, event.message.message)
            # Remove URLs from the message text
            text_without_urls = re.sub(URL_REGEX, "", event.message.message).strip()

            message_data = {
                'text': text_without_urls,
                'urls': urls,
                'image': None
            }
            
            if event.message.media:
                pass
                # if not os.path.exists("images"):
                #     os.makedirs("images")
                # media_path = await self.client.download_media(event.message, "images/", thumb=-1)
                # message_data['image'] = media_path
                        
            
            if callable(self.message_callback):
                # Check if the message_callback is an async function
                if asyncio.iscoroutinefunction(self.message_callback):
                    await self.message_callback(message_data)
                else:
                    # If it's not an async function, you may need to run it in a thread
                    # or just call it directly if it's okay to block (though usually not recommended in async code)
                    self.message_callback(message_data)
            else:
                print("message_callback is not set or not callable.")

    async def run(self):
        await self.client.start()
        await self.process_messages()
        await self.client.run_until_disconnected()

