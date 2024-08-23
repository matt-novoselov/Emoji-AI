from PIL import Image
from io import BytesIO
import replicate
import aiohttp


# Function that generates emoji and returns an image
async def generate_emoji(description: str):
    try:
        # Define prompt for AI model
        output = replicate.run(
            "fofr/sdxl-emoji:e6484351b3c943cbd507d938df8abc598cb05c44f4e67ee82be0beea5f495f31",
            input={
                "width": 768,
                "height": 768,
                "prompt": f"A TOK emoji of a {description}",
                "num_inference_steps": 30,
                "negative_prompt": "racist, xenophobic, antisemitic, islamophobic, bigoted",
            }
        )
        return output[0]

    except Exception as e:
        print(f'[!] There was an error while trying to generate emoji: {e}')


# Function that removes background from generated image
async def remove_background(image_url):
    try:
        # Define prompt for AI model
        output = replicate.run(
            "cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",
            input={
                "image": image_url
            }
        )
        return output

    except Exception as e:
        print(f'[!] There was an error while trying to remove background: {e}')


# Function that download image from web hosting
async def download_image(url_no_background):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url_no_background) as response:
                return await response.read()

    except Exception as e:
        print(f'[!] There was an error while trying to download image: {e}')


# Function that resizes image to match emoji size
async def resize_image(input_image_bytes, output_size=(100, 100)):
    try:
        # Allow transparency
        input_image = Image.open(BytesIO(input_image_bytes)).convert("RGBA")
        resized_image = input_image.resize(output_size)

        output_buffer = BytesIO()
        resized_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        return output_buffer

    except Exception as e:
        print(f'[!] There was an error while trying to resize image: {e}')
