import json
from pyrogram import filters
from pyrogram.types import Message
import os

PMBL_CONFIG_FILE = 'data/pmbl_config.json'
WHITELIST_FILE = 'data/whitelist.json'

def register(client, bot):
    # Инициализация конфигурации PM Blocker
    if not os.path.exists(PMBL_CONFIG_FILE):
        with open(PMBL_CONFIG_FILE, 'w') as f:
            json.dump({"enabled": False}, f)

    with open(PMBL_CONFIG_FILE, 'r') as f:
        config = json.load(f)

    # Инициализация белого списка
    if not os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, 'w') as f:
            json.dump(["BotFather"], f)

    with open(WHITELIST_FILE, 'r') as f:
        whitelist = json.load(f)

    @client.on_message(filters.command("pmbl", prefixes=bot.prefix) & filters.user(int(bot.owner_id)))
    async def pmbl_toggle(client, message: Message):
        command = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not command:
            usage_message = (
                "ℹ️ Использование:\n"
                f"{bot.prefix}pmbl {{on/off}} {{help}}\n"
                f"{bot.prefix}pmwl {{ответ на сообщение/используйте в ЛС}}"
            )
            await message.edit_text(usage_message)
            return

        if command == 'help':
            help_message = (
                "🛡 Команды PM Blocker:\n"
                f"{bot.prefix}pmbl on/off - Включить/выключить блокировку ЛС.\n"
                f"{bot.prefix}pmwl - Добавить пользователя в белый список (используйте в личке или ответом на сообщение).\n"
                f"{bot.prefix}pmbl help - Показать это сообщение."
            )
            await message.edit_text(help_message)
            return

        config['enabled'] = (command == 'on')
        with open(PMBL_CONFIG_FILE, 'w') as f:
            json.dump(config, f)

        status = "включен" if config['enabled'] else "выключен"
        await message.edit_text(f"🔒 PM Blocker {status}.")

    @client.on_message(filters.command("pmwl", prefixes=bot.prefix) & filters.user(int(bot.owner_id)))
    async def pmwl_add(client, message: Message):
        args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        user_id = None

        if message.chat.type == "private":
            user_id = message.chat.id
        elif message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        elif args:
            try:
                user = await client.get_users(args)
                user_id = user.id
            except Exception as e:
                await message.edit_text(f"❌ Ошибка получения пользователя: {str(e)}")
                return

        if not user_id:
            await message.edit_text("⚠️ Используйте команду в личке, ответом на сообщение или укажите юзернейм.")
            return

        if user_id not in whitelist:
            whitelist.append(user_id)
            with open(WHITELIST_FILE, 'w') as f:
                json.dump(whitelist, f)
            await message.edit_text("✅ Пользователь добавлен в белый список.")
        else:
            await message.edit_text("ℹ️ Пользователь уже в белом списке.")

    @client.on_message(filters.private & ~filters.user(whitelist))
    async def pmbl_handler(client, message: Message):
        if not config['enabled']:
            return

        try:
            if message.chat.type == "private" and message.from_user:
                await message.edit_text("🚫 Извините, я не принимаю сообщения от незнакомцев. Вы были заблокированы.")
                await client.block_user(message.from_user.id)
        except Exception as e:
            await message.edit_text(f"❌ Произошла ошибка: {str(e)}")

COMMANDS = ["pmbl on/off", "pmwl"]
ModuleName = "PMBlocker"