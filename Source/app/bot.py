import aiogram.methods
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, ContentType
from aiogram.utils.formatting import Bold, CustomEmoji, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import TELEGRAM_TOKEN
import app.EmojiAPI2 as EmojiAPI2
import app.mysql_database as mysql_database


bot = Bot(TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Stack of users whose requests are currently being processed
Processing_users = []

# Allowed types of content to which the bot should react
Allowed_types = [ContentType.TEXT]


# React on /start message
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Hi, <b>{message.from_user.full_name}</b> 👋\n\n"
                         "Send me a description of your emoji and I will generate it!")


# Function to create a new sticker pack (emoji pack) for given user and put first emoji
async def create_new_pack_and_put_emoji(user_id, pack_link_from_database, full_name, bytes_image):
    try:
        # Define and create new sticker pack
        await bot.create_new_sticker_set(
            user_id=user_id,
            name=f"{pack_link_from_database}_by_{await get_username()}",
            title=f"{full_name}’s emojis by @{await get_username()}",
            stickers=[
                aiogram.types.input_sticker.InputSticker(
                    emoji_list=["🖼️"],
                    sticker=BufferedInputFile(bytes_image, "emoji.png"),
                    format="static"
                )
            ],
            sticker_format="static",
            sticker_type="custom_emoji",
        )
        return await get_latest_custom_emoji_id(pack_link_from_database)
    except Exception as e:
        raise Exception(f"Error occurred while trying to create new pack and put an emoji: {e}")


# Function to append new emoji to the already existing sticker pack
async def add_new_emoji_to_pack(user_id, pack_link_from_database, bytes_image):
    try:
        # Define and add new sticker to existing set
        await bot.add_sticker_to_set(
            user_id=user_id,
            name=f"{pack_link_from_database}_by_{await get_username()}",
            sticker=aiogram.types.input_sticker.InputSticker(
                emoji_list=["🖼️"],
                sticker=BufferedInputFile(bytes_image, "emoji.png"),
                format="static"
            ),
        )
        return await get_latest_custom_emoji_id(pack_link_from_database)
    except Exception as e:
        raise Exception(f"Error occurred while trying to add new emoji to the pack: {e}")


async def add_emoji_to_pack(user_id, full_name, emoji_image_bytes):
    pack_username, pack_was_created = await mysql_database.return_pack_username_and_activated_status(user_id)
    custom_emoji_id = ""

    # Add sticker to existing pack
    if pack_was_created:  # Check pack is not deleted by user
        if await set_exists(pack_username):  # Pack was not touched
            sticker_set = await bot.get_sticker_set(f"{pack_username}_by_{await get_username()}")
            amount_of_stickers = len(sticker_set.stickers)
            if amount_of_stickers >= 200:
                pack_username = await mysql_database.update_pack_name_in_db(user_id)
                custom_emoji_id = await create_new_pack_and_put_emoji(
                    user_id,
                    pack_username,
                    full_name,
                    emoji_image_bytes,
                )
            else:
                custom_emoji_id = await add_new_emoji_to_pack(
                    user_id,
                    pack_username,
                    emoji_image_bytes,
                )
        else:  # Pack was deleted
            pack_username = await mysql_database.update_pack_name_in_db(user_id)
            custom_emoji_id = await create_new_pack_and_put_emoji(
                user_id,
                pack_username,
                full_name,
                emoji_image_bytes,
            )
    else:  # Create new pack and add first sticker
        custom_emoji_id = await create_new_pack_and_put_emoji(
            user_id,
            pack_username,
            full_name,
            emoji_image_bytes,
        )

    return pack_username, custom_emoji_id


# Message that is being sent if user tries to start processing new emoji until the previous one is done
@dp.message(F.content_type.in_(Allowed_types) and F.from_user.id.in_(Processing_users))
async def wait_until_finished(message: types.Message) -> None:
    await message.reply("<b>Not so fast!</b> 😅\n\n"
                        "You need to wait for the processing of your previous emoji to finish.")


# React on message type "Text" -> Generate an emoji based on description
@dp.message(F.content_type == Allowed_types[0])  # TEXT
async def process_text(message: types.Message) -> None:
    # Send warning if user doesn't have premium
    if not message.from_user.is_premium:
        await message.answer("<b>⭐️ It looks like you don't have a Telegram Premium subscription.</b>\n\n"
                             "You won't be able to use stickers that you create.")

    prompt = message.text
    processing_message = Text(
        CustomEmoji("⏳", custom_emoji_id="5307981757063110606"),
        " We are processing your emoji of ",
        Bold(prompt),
    )
    progress_message = await message.reply(**processing_message.as_kwargs())
    try:
        await add_user_to_processing(message.from_user.id)

        full_response = await EmojiAPI2.generate_emoji(prompt)
        no_background_url = await EmojiAPI2.remove_background(full_response)
        downloaded_image_bytes = await EmojiAPI2.download_image(no_background_url)
        transformed_image_buffer = await EmojiAPI2.resize_image(downloaded_image_bytes)
        transformed_image_bytes = transformed_image_buffer.getvalue()
        pack_username, custom_emoji_id = await add_emoji_to_pack(
            message.from_user.id,
            message.from_user.full_name,
            transformed_image_bytes,
        )

        await progress_message.delete()
        builder = InlineKeyboardBuilder()
        builder.button(text=f"📂 Open emoji pack", url=f"https://t.me/addemoji/{pack_username}_by_{await get_username()}")
        success_text_message = Text(Bold("Emoji generated!"))
        emoji_message = Text(CustomEmoji("🖼️", custom_emoji_id=custom_emoji_id))
        try:
            await message.reply(**success_text_message.as_kwargs(), reply_markup=builder.as_markup())
            await message.reply(**emoji_message.as_kwargs())
        except Exception:
            await message.reply("<b>Emoji generated</b> ✅", reply_markup=builder.as_markup())

        print(f"[v] User {message.from_user.id} successfully generated {prompt} emoji. "
              f"Link: https://t.me/addemoji/{pack_username}_by_{await get_username()}")

    except Exception as e:
        await progress_message.delete()
        print(f"[!] User {message.from_user.id} was trying to generate {message.text} and got an error: {e}")
        if str(e.args[0]) == "NSFW Content detected":
            await message.reply("<b>🔞 We do not allow NSFW content</b>\n\n"
                                "Your emoji was not generated. Please try again")
        else:
            await message.reply("<b>Oups... Something went wrong</b> 🤕\n\n"
                                "Your emoji was not generated. Please try again")
        return

    finally:
        await remove_user_from_processing(message.from_user.id)


# Respond to unsupported content type (ex. photo)
@dp.message(~F.content_type.in_(Allowed_types))
async def wrong_type_input(message: types.Message) -> None:
    await message.reply(
        f"<b>Sorry, I can't generate an emoji from the "
        f"{message.content_type.lower().replace('_', ' ')} yet...</b> 😔\n\n"
        "Please send a text description of your emoji. For example: <code>Travel cat</code>")


# Add user to processing queue
async def add_user_to_processing(user_id):
    try:
        Processing_users.append(user_id)
    except Exception as e:
        raise Exception(f"Error occurred while trying to add the user to the processing list: {e}")


# Remove user to processing queue
async def remove_user_from_processing(user_id):
    try:
        Processing_users.remove(user_id)
    except Exception as e:
        raise Exception(f"Error occurred while trying to remove the user from the processing list: {e}")


# Function to check if sticker set already exists
async def set_exists(sticker_set):
    try:
        await bot.get_sticker_set(f"{sticker_set}_by_{await get_username()}")
        return True
    except Exception:  # The pack was deleted
        pass
        return False


async def get_latest_custom_emoji_id(sticker_set):
    try:
        full_sticker_set = await bot.get_sticker_set(f"{sticker_set}_by_{await get_username()}")
        if not full_sticker_set.stickers:
            raise Exception("Sticker set is empty")

        custom_emoji_id = full_sticker_set.stickers[-1].custom_emoji_id
        if not custom_emoji_id:
            raise Exception("Latest sticker does not have custom_emoji_id")

        return custom_emoji_id
    except Exception as e:
        raise Exception(f"Error occurred while trying to retrieve custom emoji id: {e}")


# Remove user to processing queue
async def get_username():
    info = await bot.get_me()
    username = info.username
    return username
