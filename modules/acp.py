import os
import json
from pyrogram import filters
from pyrogram.types import Message

MODULES_PATH = 'data'
BACKUP_FILE = os.path.join(MODULES_PATH, 'backup.json')

def register(client, bot):
    @client.on_message(filters.command("acp", prefixes=bot.prefix) & filters.user(int(bot.owner_id)))
    async def ac_handler(client, message: Message):
        # Извлечение аргумента команды
        args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

        if args == "backup":
            await message.edit_text("🔄 Сохранение текущего состояния...")
            try:
                me = await client.get_me()
                backup_data = {
                    "first_name": me.first_name,
                    "last_name": me.last_name
                }

                # Сохранение аватарки
                async for photo in client.get_chat_photos("me", limit=1):
                    file_path = os.path.join(MODULES_PATH, 'backup_avatar.jpg')
                    await client.download_media(photo.file_id, file_path)
                    backup_data["avatar"] = file_path

                with open(BACKUP_FILE, 'w') as f:
                    json.dump(backup_data, f)

                await message.edit_text("✅ Текущее состояние успешно сохранено.")
            except Exception as e:
                await message.edit_text(f"❌ Произошла ошибка при сохранении: {str(e)}")

        elif args == "restore":
            await message.edit_text("🔄 Восстановление из бэкапа...")
            try:
                if not os.path.exists(BACKUP_FILE):
                    await message.edit_text("⚠️ Нет сохранённых данных для восстановления.")
                    return

                with open(BACKUP_FILE, 'r') as f:
                    backup_data = json.load(f)

                # Восстановление имени и фамилии
                await client.update_profile(
                    first_name=backup_data.get("first_name", ''),
                    last_name=backup_data.get("last_name", '')
                )

                # Удаление всех текущих аватарок
                async for photo in client.get_chat_photos("me", limit=1):
                    await client.delete_profile_photos([photo.file_id])

                # Установка сохраненной аватарки
                if "avatar" in backup_data and os.path.exists(backup_data["avatar"]):
                    await client.set_profile_photo(photo=backup_data["avatar"])

                await message.edit_text("✅ Восстановление успешно завершено.")
            except Exception as e:
                await message.edit_text(f"❌ Произошла ошибка при восстановлении: {str(e)}")

        else:
            # Копирование данных другого пользователя
            if not args and not message.reply_to_message:
                await message.edit_text("⚠️ Укажите юзернейм или ответьте на сообщение.")
                return

            try:
                if message.reply_to_message:
                    target_user = message.reply_to_message.from_user
                else:
                    target_user = await client.get_users(args)

                await message.edit_text("🔄 Копирование данных пользователя...")

                # Сохранение аватарки
                async for photo in client.get_chat_photos(target_user.id, limit=1):
                    file_path = os.path.join(MODULES_PATH, 'temp_avatar.jpg')
                    await client.download_media(photo.file_id, file_path)

                    # Установка аватарки
                    await client.set_profile_photo(photo=file_path)

                    # Удаление временного файла
                    os.remove(file_path)

                # Обновление имени и фамилии
                await client.update_profile(
                    first_name=target_user.first_name or '',
                    last_name=target_user.last_name or ''
                )

                await message.edit_text("✅ Данные пользователя успешно скопированы.")
            except Exception as e:
                await message.edit_text(f"❌ Произошла ошибка: {str(e)}")
                
COMMANDS = ["acp backup", "acp restore", "acp {username}, {reply_to_message}"]
ModuleName = "AccountCopy"