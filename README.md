# Emoji AI bot

Source code of an Aiogram 3.x-based Telegram bot that can generate an emoji based on the description provided by the user and automatically add it to the sticker pack.

![](https://github.com/matt-novoselov/Emoji-AI/blob/f8b483a476a40183be642daa3e056477ee7e67d7/EmojiAIBot.png)

[![Telegram Bot](https://github.com/matt-novoselov/matt-novoselov/blob/4fddb3cb2c7e952d38b8b09037040af183556a77/Files/telegram_button.svg)](https://t.me/EmojiAi_bot)

## Requirements
- Python 3.8
- aiogram 3.12.0
- python-dotenv 1.0.1
- fastapi 0.112.1
- uvicorn 0.30.6
- aiomysql 0.2.0
- Pillow 10.4.0
- aiohttp 3.9.0
- replicate 0.32.0

## Installation
1. Clone repository using the following URL: `https://github.com/matt-novoselov/Emoji-AI.git`
2. Create Environment File:
   - Create a file named `.env` in the root directory of the source folder.
   - Use the provided `.env.example` file as a template.
3. Replace the placeholder values with your specific configuration:
   - TELEGRAM_TOKEN: Insert your Telegram Bot Token obtained from the [BotFather](https://t.me/botfather).
   - WEBHOOK_DOMAIN: Public SSL domain that will be listening for webhooks request from Telegram.
   - REPLICATE_API_TOKEN: Insert your Replicate API Token obtained from the [Replicate](https://replicate.com/).
   - DB_NAME: The name of the MySQL database your bot will use.
   - DB_PORT: This is the port for your MySQL database.
   - DB_USERNAME: The username used to access your MySQL database.
   - DB_HOST: This is the host address for your MySQL database.
   - DB_PASSWORD: The password associated with the provided username for accessing the MySQL database.
4. Build and run `main.py`

## Credits
- [sdxl-emoji](https://replicate.com/fofr/sdxl-emoji) - fine tuned SDXL based on Apple's emojis.
- [rembg](https://replicate.com/cjwbw/rembg) - remove images background model.
- [EmojiGen](https://github.com/cbh123/emoji) - original emoji generator.

<br>

Distributed under the MIT license. See **LICENSE** for more information.

Developed with ❤️ by Matt Novoselov
