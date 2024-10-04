import os
from pyrogram import filters
from pyrogram.types import Message

def register(client, bot):
    @client.on_message(filters.command("example", prefixes=bot.prefix) & filters.user(int(bot.owner_id)))
    async def example_handler(client, message: Message):
        await message.edit_text("Это пример команды.")

COMMANDS = ["example"]
ModuleName = "example"