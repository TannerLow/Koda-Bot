import logging
import os
from datetime import timedelta

import discord
from discord import Message
from dotenv import load_dotenv

from src.Discord.command_parser import CommandParser
from src.Logging.logger import Logger
from src.API.koda import Koda
from src.API.model import (
    CheckinSettings,
    LevelingSettings
)
from src.Database.in_memory_database_facade import InMemoryDatabaseFacade
from src.Database.in_memory_db import InMemoryDatabase
from src.Database.model import DatabaseSettings


load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")

# Create a client with message intent
intents = discord.Intents.default()
intents.message_content = True  # Required to read message text
client = discord.Client(intents=intents)

# Create components
database_settings = DatabaseSettings(
    save_filename='db.json',
    save_folder='persistance'
)
database = InMemoryDatabase("KodaDB")
database_facade = InMemoryDatabaseFacade(database, database_settings)

checkin_settings = CheckinSettings(
    base_cooldown=timedelta(seconds=10)
)
leveling_settings = LevelingSettings(
    checkin_reward=500
)
koda_api = Koda(
    "templates",
    database_facade, 
    checkin_settings, 
    leveling_settings
)

parser = CommandParser("koda", koda_api)
LOGGER = Logger(__file__, "debug")

#test.create_test_data_in_db(database)


@client.event
async def on_ready():
    LOGGER.info(f"Bot connected as {client.user}")

@client.event
async def on_message(message: Message):
    # Prevent bot from replying to itself
    if message.author == client.user:
        return
    
    LOGGER.debug(f"Read message: {message}")
    LOGGER.debug(f"Contents: {message.content}")
    
    #await message.channel.send(f"Processing: '{message.content}'")

    if parser.is_command(message.content):
        LOGGER.debug("Command detected")
        await parser.parse_command(message)
    


# Start the bot
client.run(TOKEN)
