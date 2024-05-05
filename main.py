# import json, asyncio, re, os, logging
# from asyncio.queues import Queue
# from dotenv import load_dotenv

# from listeners.telegramListener.telegramListener import TelegramMessageRetriever
# from helpers.helper import Helper
# from senders.discordSender.sendMessages import DiscordSender
# from APICalls.userAgents.scrapers import get_useragents

# # Load environment variables
# load_dotenv()
# MAX_CONCURRENT_MESSAGES = 3

# # Setup logging
# logging.basicConfig(level=logging.INFO)

# print_message_instance = PrintMessage()
# helper = Helper()
# def is_valid_url(url):
#     return re.match(r'https?://[^\s]+', url) is not None

# async def message_worker(queue: Queue, discord_sender, semaphore: asyncio.Semaphore):
#     while True:
#         message_data = await queue.get()
#         async with semaphore:
#             await print_message_instance.print_message(message_data, discord_sender)
#         queue.task_done()

# async def process_messages(payload, discord_sender):
#     queue = Queue()
#     semaphore = asyncio.Semaphore(MAX_CONCURRENT_MESSAGES)

#     # Create worker tasks to process messages from the queue
#     workers = [asyncio.create_task(message_worker(queue, discord_sender, semaphore)) for _ in range(MAX_CONCURRENT_MESSAGES)]

#     msg_retriever = TelegramMessageRetriever(payload, lambda message_data: asyncio.create_task(helper.main_helper(message_data=message_data, discord_sender=discord_sender)))
#     await msg_retriever.run()

#     # Wait for the queue to be empty
#     await queue.join()

#     # Cancel worker tasks
#     for worker in workers:
#         worker.cancel()

#     # Wait for all worker tasks to be cancelled
#     await asyncio.gather(*workers, return_exceptions=True)

# async def main():
#     #config_data = json.load(open(".../database/config.json"))
#     # config_data = json.load(open(r"C:\Users\micha\Python Projects\DiamondAIO\Telegram\Utility\database\config.json"))
    
#     await get_useragents()
#     # Relative path
#     config_data = json.load(open("./configurations/config.json"))
    
#     discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
#     discord_channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
#     discord_sender = DiscordSender(discord_bot_token, discord_channel_id)

#     payload = next((item for item in config_data["telegram_keys"] if int(item["key_number"]) == 1), None)
#     if not payload:
#         print("No payload found.")
#         return

#     # Run both the Discord bot and the message processing concurrently
#     await asyncio.gather(
#         discord_sender.run(),  # This starts the Discord bot
#         process_messages(payload, discord_sender)  # This starts processing messages concurrently
#     )

# if __name__ == "__main__":
#     asyncio.run(main())


import json
import asyncio
import os
from asyncio.queues import Queue
from dotenv import load_dotenv
import sys

# Custom imports
from listeners.telegramListener.telegramListener import TelegramMessageRetriever
from helpers.helper import Helper
from senders.discordSender.sendMessages import DiscordSender
from APICalls.userAgents.scrapers import get_useragents
from utils.logger import configure_logger

sys.dont_write_bytecode = True

# Load environment variables
load_dotenv()
MAX_CONCURRENT_MESSAGES = 3

# Setup logging
logger = configure_logger(__name__)

# Setup instances of Helper and DiscordSender
def initialize_helpers_and_senders():
    discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
    discord_channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
    discord_sender = DiscordSender(discord_bot_token, discord_channel_id)
    helper = Helper(message_data={}, discord_sender=discord_sender)  # Assuming message_data is provided here or updated dynamically
    return discord_sender, helper

async def message_worker(queue: Queue, helper: Helper, semaphore: asyncio.Semaphore, discord_sender: DiscordSender):
    while True:
        message_data = await queue.get()
        print('\n')
        print(f'Message Data message_worker : {message_data}\n')
        async with semaphore:
            # Assuming a method in helper uses discord_sender to send messages
            await helper.process_links(message_data, discord_sender)
        queue.task_done()


async def process_messages(payload, discord_sender, helper):
    queue = Queue()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_MESSAGES)

    # Create worker tasks to process messages from the queue
    # workers = [asyncio.create_task(message_worker(queue, helper, semaphore)) for _ in range(MAX_CONCURRENT_MESSAGES)]
    workers = [asyncio.create_task(message_worker(queue, helper, semaphore, discord_sender)) for _ in range(MAX_CONCURRENT_MESSAGES)]

    msg_retriever = TelegramMessageRetriever(payload, lambda message_data: logger.info(f"Enqueuing message: {message_data}\n") or queue.put_nowait(message_data))
    await msg_retriever.run()

    # Wait for the queue to be empty
    await queue.join()

    # Cancel worker tasks
    for worker in workers:
        worker.cancel()

    # Wait for all worker tasks to be cancelled
    await asyncio.gather(*workers, return_exceptions=True)

async def main():
    await get_useragents()
    config_data = json.load(open("./configurations/config.json"))
    
    discord_sender, helper = initialize_helpers_and_senders()
    payload = next((item for item in config_data["telegram_keys"] if int(item["key_number"]) == 1), None)
    
    if not payload:
        logger.info("No payload found.")
        return

    # Run both the Discord bot and the message processing concurrently
    await asyncio.gather(
        discord_sender.run(),  # This starts the Discord bot
        process_messages(payload, discord_sender, helper)  # This starts processing messages concurrently
    )

if __name__ == "__main__":
    asyncio.run(main())
