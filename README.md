# Emoji AI bot

Source code of Aiogram 3.x based Telegram bot that can generate an emoji based on the description and add it to the pack.

![](https://github.com/matt-novoselov/Emoji-AI/blob/f8b483a476a40183be642daa3e056477ee7e67d7/EmojiAIBot.png)

[![Telegram Bot](https://github.com/matt-novoselov/matt-novoselov/blob/4fddb3cb2c7e952d38b8b09037040af183556a77/Files/telegram_button.svg)](https://t.me/EmojiAi_bot)

## Requirements
- Python 3.8
- aiogram 3.1.1
- python-dotenv 1.0.0
- aiomysql 0.2.0
- Pillow 10.0.1
- aiohttp 3.8.6
- replicate 0.15.8

## Installation
1. Clone repository using the following URL: `https://github.com/matt-novoselov/Emoji-AI.git`
2. Create Environment File:
   - Create a file named `.env` in the root directory of the source folder.
   - Use the provided `.env.example` file as a template.
3. Replace the placeholder values with your specific configuration:
   - TELEGRAM_TOKEN: Insert your Telegram Bot Token obtained from the [BotFather](https://t.me/botfather).
   - REPLICATE_API_TOKEN: Insert your Replicate API Token obtained from the [Replicate](https://replicate.com/).
   - DATABASE: The name of the MySQL database your bot will use.
   - DB_USERNAME: The username used to access your MySQL database.
   - HOST: This is the host address for your MySQL database.
   - PASSWORD: The password associated with the provided username for accessing the MySQL database.
   - DB_PORT: This is the port for your MySQL database.
4. Build and run `main.py`

## Credits
- [sdxl-emoji](https://replicate.com/fofr/sdxl-emoji) - fine tuned SDXL based on Apple's emojis.
- [rembg](https://replicate.com/cjwbw/rembg) - remove images background model.
- [EmojiGen](https://github.com/cbh123/emoji) - original emoji generator.

<br>

Distributed under the MIT license. See **LICENSE** for more information.

Developed with ❤️ by Matt Novoselov
