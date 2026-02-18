import asyncio
from io import BytesIO

import aiohttp
from PIL import Image

from app.config import REPLICATE_API_TOKEN

REPLICATE_API_BASE_URL = "https://api.replicate.com/v1/predictions"
EMOJI_MODEL_VERSION = "e6484351b3c943cbd507d938df8abc598cb05c44f4e67ee82be0beea5f495f31"
REMOVE_BACKGROUND_MODEL_VERSION = "fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003"
PREDICTION_POLL_INTERVAL_SECONDS = 1
PREDICTION_POLL_ATTEMPTS = 120


def _replicate_headers() -> dict[str, str]:
    if not REPLICATE_API_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN is missing")
    return {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }


async def _run_prediction(model_version: str, input_payload: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            REPLICATE_API_BASE_URL,
            json={"version": model_version, "input": input_payload},
            headers=_replicate_headers(),
        ) as response:
            prediction_data = await response.json(content_type=None)
            if response.status >= 400:
                raise RuntimeError(
                    f"Replicate create prediction failed ({response.status}): {prediction_data}"
                )

        prediction_id = prediction_data.get("id")
        if not prediction_id:
            raise RuntimeError("Replicate response did not include a prediction id")

        for _ in range(PREDICTION_POLL_ATTEMPTS):
            async with session.get(
                f"{REPLICATE_API_BASE_URL}/{prediction_id}",
                headers=_replicate_headers(),
            ) as poll_response:
                poll_data = await poll_response.json(content_type=None)
                if poll_response.status >= 400:
                    raise RuntimeError(
                        f"Replicate prediction polling failed ({poll_response.status}): {poll_data}"
                    )

            status = poll_data.get("status")
            if status == "succeeded":
                return poll_data.get("output")
            if status in {"failed", "canceled"}:
                raise RuntimeError(f"Replicate prediction {status}: {poll_data.get('error')}")

            await asyncio.sleep(PREDICTION_POLL_INTERVAL_SECONDS)

    raise TimeoutError("Replicate prediction polling timed out")


# Function that generates emoji and returns an image
async def generate_emoji(description: str):
    output = await _run_prediction(
        EMOJI_MODEL_VERSION,
        {
            "width": 768,
            "height": 768,
            "prompt": f"A TOK emoji of a {description}",
            "num_inference_steps": 30,
            "negative_prompt": "racist, xenophobic, antisemitic, islamophobic, bigoted",
        },
    )
    if isinstance(output, list) and output:
        return output[0]
    if isinstance(output, str):
        return output
    raise RuntimeError("Replicate emoji generation output format is unexpected")


# Function that removes background from generated image
async def remove_background(image_url):
    output = await _run_prediction(
        REMOVE_BACKGROUND_MODEL_VERSION,
        {
            "image": image_url,
        },
    )
    if isinstance(output, list) and output:
        return output[0]
    if isinstance(output, str):
        return output
    raise RuntimeError("Replicate background removal output format is unexpected")


# Function that download image from web hosting
async def download_image(url_no_background):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url_no_background) as response:
            response.raise_for_status()
            return await response.read()


# Function that resizes image to match emoji size
async def resize_image(input_image_bytes, output_size=(100, 100)):
    # Allow transparency
    input_image = Image.open(BytesIO(input_image_bytes)).convert("RGBA")
    resized_image = input_image.resize(output_size)

    output_buffer = BytesIO()
    resized_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    return output_buffer
