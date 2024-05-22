import discord
import asyncio
import os

class DiscordSender:
    def __init__(self, bot_token, default_channel_id,):
        intents = discord.Intents.default()
        intents.messages = True
        self.client = discord.Client(intents=intents)
        self.default_channel_id = default_channel_id
        self.channel_map = {
            'amazon': '1209701851532886086',
            'walmart': '1209701912602214410',
            'samsclub': '1209702296561389658',
            'ulta': '1209702316475940925',
            'lowes': '1209702439222255626',
            'homedepot': '1209702480645062687',
            'bestbuy': '1209702742625362010',
            'woot': '1209702811999281162',
            'kohls': '1209702919335714836',
            'macys': '1209702933449408543',
            'underarmour': '1209969056208126064',
            'chewy': '1209972570728955964',
            'target': '1210068227686932482',
            'zappos': '1210070314969735280',
            'wayfair': '1210224049024929822',
            'disneystore': '1210268740541743205',
            'michaelkors': '1210269013720965150',
            'walgreens': '1210273221304258591',
            'cvs': '1210273282369003591',
            'oldnavy': '1210273448069431318',
            'nike': '1210279585099415572',
            'others': '1209702637193396295',
            'amazon_90_100' : '1094304813820424263',
            'amazon_80_89' : '1094304791561252997',
            'amazon_70_79' : '1094304762024951819',
            'amazon_60_69' : '1094304733893771285',
            'amazon_1_59' : '1142303917393313882',
            'lightning_deals': '1242557327702495263'
        }
        self.bot_token = bot_token
        self.message_queue = asyncio.Queue()
        self.file_queue = asyncio.Queue()
        self.channel_map = {key: int(value) for key, value in self.channel_map.items()}
        self.default_channel_id = int(default_channel_id)
        self.last_channel_id = None


        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user}')
            asyncio.create_task(self.process_message_queue())
            asyncio.create_task(self.process_file_queue())

    async def process_message_queue(self):
        while True:
            message_details = await self.message_queue.get()
            embed = message_details["embed"]
            links = message_details.get("links", [])
            filepath = message_details.get("filepath")

            # Determine the appropriate channel
            channel_id = self.determine_channel_id(links)
            channel = self.client.get_channel(channel_id)

             # Determine the appropriate channel
            channel_id = self.determine_channel_id(links)
            print(f"Channel ID: {channel_id}")
            channel = self.client.get_channel(channel_id)
            print(f"Channel: {channel}")
            
            try:
                if filepath:
                    with open(filepath, 'rb') as file:
                        discord_file = discord.File(file, filename=os.path.basename(filepath))
                        embed.set_image(url=f"attachment://{os.path.basename(filepath)}")
                        await channel.send(embed=embed, file=discord_file)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                else:
                    await channel.send(embed=embed)
                print("Message sent successfully")
            except Exception as e:
                print(f"Error sending message: {e}")
            finally:
                self.message_queue.task_done()

    async def process_file_queue(self):
        while True:
            file_details = await self.file_queue.get()
            filepath = file_details["filepath"]
            filename = file_details.get("filename", "file.jpg")
            channel_id = file_details.get("channel_id", self.default_channel_id)
            
            channel = await self.client.get_channel(channel_id)
            
            try:
                with open(filepath, 'rb') as file:
                    discord_file = discord.File(file, filename=filename)
                    await channel.send(file=discord_file)
                print("File sent successfully")
            except Exception as e:
                print(f"Error in sending file: {e}")
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
                self.file_queue.task_done()

    def determine_channel_id(self, links, is_promo_code_only=False, discount=0):
        # Use the last channel ID if the message is promo code only
        print(f"Disounted price: {discount}")
        discount_channel = ""
        if 90 <= discount <= 100:
            discount_channel = self.channel_map['amazon_90_100']
        if 80 <= discount <= 89:
            discount_channel = self.channel_map['amazon_80_89']
        if 70 <= discount <= 79:
            discount_channel = self.channel_map['amazon_70_79']
        if 60 <= discount <= 69:
            discount_channel = self.channel_map['amazon_60_69']
        if 0 <= discount <= 59:
            discount_channel = self.channel_map['amazon_1_59']
        if is_promo_code_only:
            return self.last_channel_id if self.last_channel_id else self.default_channel_id

        for link in links:
            for key, channel_id in self.channel_map.items():
                if key in link.lower():
                    return channel_id, discount_channel

        return self.channel_map.get('others', self.default_channel_id), discount_channel

    async def send_to_discord(self, embed, links, filepath=None, is_promo_code_only=False, discount=0, is_lightning_deal='N/A'):
        # Determine the channel ID, considering if the message is promo code only
        # print(f'Discount: {discount}\n\n')
        channel_id, discount_channel_id = self.determine_channel_id(links, is_promo_code_only=is_promo_code_only, discount=discount)
        # Send the message to the determined channel
        channel = self.client.get_channel(channel_id)

        if discount_channel_id:
            discount_channel = self.client.get_channel(discount_channel_id)
            await discount_channel.send(embed=embed)
                    
        if is_lightning_deal.lower().strip() == 'lightning deal':
            lightning_deal_channel = self.client.get_channel(self.channel_map['lightning_deals'])
            await lightning_deal_channel.send(embed=embed)

        try:
            if filepath:
                with open(filepath, 'rb') as file:
                    discord_file = discord.File(file, filename=os.path.basename(filepath))
                    await channel.send(embed=embed, file=discord_file)
                if os.path.exists(filepath):
                    os.remove(filepath)
            else:
                await channel.send(embed=embed)
            print("Message sent successfully")
        except Exception as e:
            print(f"Error sending message: {e}")


    async def run(self):
        """Run the Discord client."""
        await self.client.start(self.bot_token)

