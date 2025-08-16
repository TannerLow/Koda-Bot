import logging
from datetime import datetime, timedelta
from typing import Optional

import discord
from discord import Message

from ..Logging.logger import Logger
from ..API.koda import Koda
from ..API.model import (
    Stats,
    User,
    Checkin
)

LOGGER = Logger(__file__, "debug")

class CommandParser:

    def __init__(self, command_prefix: str, koda_api: Koda):
        self.prefix = command_prefix
        self.actions = {
            "?": self.help,
            "stats": self.get_stats,
            "checkin": self.checkin,
            "register": self.register,
            "clear": self.clear_user,
        }
        self.api = koda_api

    def is_command(self, message: str) -> bool:
        return (message[:len(self.prefix)] == self.prefix)
    
    async def parse_command(self, message: Message) -> None:
        command: str = message.content[len(self.prefix):].split()
        LOGGER.debug(f"Command after splitting: {command}")
        
        if len(command) < 1:
            LOGGER.debug("Command has no arguments")
            return

        action: str = command[0]
        if action in self.actions:
            LOGGER.debug(f"Action detected: {action}")
            await self.actions[action](message, command)
        
        else:
            LOGGER.debug("Command not recognized")

    async def help(self, message: Message, command: list[str]) -> None:
        LOGGER.debug("It's a help command")
        response_message:str = self.api.get_help_text()
        dm_channel = await message.author.create_dm()
        await dm_channel.send(response_message)

    async def get_stats(self, message: Message, command: list[str]) -> None:
        LOGGER.debug("It's a stats command")

        self._handle_new_user_case(message)

        stats: Stats = self.api.get_stats(message.author.id)
        await message.channel.send(stats.model_dump_json())

    async def checkin(self, message: Message, command: list[str]) -> None:
        LOGGER.debug("It's a checkin command")

        expected_command_length: int = 2
        command_length: int = len(command)
        if command_length < expected_command_length:
            LOGGER.debug(f"Command not long enough: expected {expected_command_length}, received {command_length}")
            await message.channel.send("I don't understand. Say `koda ?` for help.")
            return

        self._handle_new_user_case(message)

        checkin: Checkin = Checkin(
            user_id=message.author.id,
            date=datetime.now(),
            proof=command[1]
        )
        remaining_cooldown: Optional[timedelta] = self.api.checkin(message.author.id, checkin)
        if remaining_cooldown:
            cooldown_str: str = self._format_timedelta(remaining_cooldown)
            await message.channel.send(f"You already checked in today. Cooldown: {cooldown_str}")
        else:
            self.api.give_xp(message.author.id, 50)
            await message.channel.send("Check in confirmed :star: +50 xp")

    def _format_timedelta(self, td: timedelta) -> str:
        total_seconds = int(td.total_seconds())
        if total_seconds < 0:
            raise ValueError("timedelta must be positive")

        days, remainder = divmod(total_seconds, 86400)  # 24*60*60
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if minutes: parts.append(f"{minutes}m")
        if seconds: parts.append(f"{seconds}s")

        return " ".join(parts) if parts else "0s"

    async def register(self, message: Message, command: list[str]) -> None:
        LOGGER.debug("It's a register command")
        raise NotImplementedError("UNIMPLEMENTED COMMAND")

    async def clear_user(self, message: Message, command: list[str]) -> None:
        LOGGER.debug("It's a clear command")
        raise NotImplementedError("UNIMPLEMENTED COMMAND")
    
    def _handle_new_user_case(self, message: Message) -> None:
        if self.api.new_user_detected(message.author.id):
            author: discord.User = message.author
            user: User = User(
                id=author.id
            )
            self.api.establish_new_user(user)
            LOGGER.info(f"New user established: {user.model_dump_json()}")
    