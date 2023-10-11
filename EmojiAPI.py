import aiohttp
import asyncio
from os import getenv
import dotenv
from PIL import Image
from io import BytesIO

dotenv.load_dotenv()
token = getenv('EMOJI_TOKEN')
url = 'https://emojis.sh/'
headers = {'next-action': 'b27e61a1c2593d4e15cff5b93551619145cf5d06'}
connector = aiohttp.TCPConnector(ssl=False)


async def post_prompt(prompt: str):
    data = {
        '1_prompt': prompt,
        '1_token': token,
        '0': '["$undefined","$K1"]',
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, headers=headers, data=data) as response:
            full_link = response.headers.get("X-Action-Redirect")
            if full_link is None:
                raise Exception(f"Failed to create a link for the emoji. Response: {response}")

            result_str = full_link.replace("/p/", "")
            return result_str


async def check_image_status(image_url):
    count = 0
    image_url = f"https://emojis.sh/api/emojis/{image_url}"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        while True:
            async with session.get(image_url) as response:
                data = await response.json()
                if data.get("emoji").get("noBackgroundUrl"):
                    return data.get("emoji").get("noBackgroundUrl")
                if data.get("emoji").get("isFlagged"):
                    raise Exception("NSFW Content detected")
            count += 1
            if count >= 5:
                raise Exception("It took too long to get noBackgroundUrl")
            await asyncio.sleep(5)  # Adjust the sleep duration based on your requirements


async def download_image(url_no_background):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url_no_background) as response:
            return await response.read()


async def transform_image(input_image_bytes, output_size=(100, 100)):
    input_image = Image.open(BytesIO(input_image_bytes)).convert("RGBA")
    resized_image = input_image.resize(output_size)

    output_buffer = BytesIO()
    resized_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    return output_buffer
