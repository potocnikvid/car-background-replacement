#!/usr/bin/env python3

"""Example of using API4AI car image background removal and adding it to a new background."""

import asyncio
import base64
import os
import sys
from PIL import Image
import aiohttp


# Use 'demo' mode just to try api4ai for free. Free demo is rate limited.
# For more details visit:
#   https://api4.ai
#
# Use 'rapidapi' if you want to try api4ai via RapidAPI marketplace.
# For more details visit:
#   https://rapidapi.com/api4ai-api4ai-default/api/cars-image-background-removal/details
MODE = 'demo'


# Your RapidAPI key. Fill this variable with the proper value if you want
# to try api4ai via RapidAPI marketplace.
RAPIDAPI_KEY = ''

# Processing mode influences returned result. Supported values are:
# * fg-image-shadow - Foreground image with shadow added.
# * fg-image - Foreground image.
# * fg-mask - Mask image.
RESULT_MODE = 'fg-image-shadow'

OPTIONS = {
    'demo': {
        'url': f'https://demo.api4ai.cloud/img-bg-removal/v1/cars/results?mode={RESULT_MODE}',
        'headers': {'A4A-CLIENT-APP-ID': 'sample'}
    },
    'rapidapi': {
        'url': f'https://cars-image-background-removal.p.rapidapi.com/v1/results?mode={RESULT_MODE}',
        'headers': {'X-RapidAPI-Key': RAPIDAPI_KEY}
    }
}


async def process_image(session, image_path, output_path, background_path):
    """Process a single image and add it to a background."""
    with open(image_path, 'rb') as image_file:
        data = {'image': image_file}
        # Make request.
        async with session.post(OPTIONS[MODE]['url'],
                                data=data,
                                headers=OPTIONS[MODE]['headers']) as response:
            resp_json = await response.json()

        img_b64 = resp_json['results'][0]['entities'][0]['image'].encode('utf8')

        # Decode the processed image and save temporarily
        processed_img_path = "processed_temp.png"
        with open(processed_img_path, 'wb') as img:
            img.write(base64.decodebytes(img_b64))

        # Open the processed image and the background image
        processed_img = Image.open(processed_img_path).convert("RGBA")
        background_img = Image.open(background_path).convert("RGBA")

        # Resize processed image to fit background if necessary
        processed_img = processed_img.resize((background_img.width, background_img.height), Image.LANCZOS)

        # Paste the processed image onto the background image
        background_img.paste(processed_img, (0, 0), processed_img)

        # Save the final image as PNG
        output_path_png = os.path.splitext(output_path)[0] + ".png"
        background_img.save(output_path_png)

        # Remove the temporary file
        os.remove(processed_img_path)


async def process_image_bg(session, image_path, output_path, background_path):
    """Process a single image and add it to a background."""
    with open(image_path, 'rb') as image_file:
        data = {'image': image_file, 'image-bg': open(background_path, 'rb')}
        # Make request.
        async with session.post(OPTIONS[MODE]['url'],
                                data=data,
                                headers=OPTIONS[MODE]['headers']) as response:
            resp_json = await response.json()

        img_b64 = resp_json['results'][0]['entities'][0]['image'].encode('utf8')

        # Decode the processed image and save temporarily
        processed_img_path = "processed_temp.png"
        with open(processed_img_path, 'wb') as img:
            img.write(base64.decodebytes(img_b64))

        # Open the processed image
        processed_img = Image.open(processed_img_path).convert("RGBA")

        # Save the final image as PNG
        output_path_png = os.path.splitext(output_path)[0] + "_bg.png"
        processed_img.save(output_path_png)

        # Remove the temporary file
        os.remove(processed_img_path)


async def main():
    """Entry point."""
    input_dir = 'input_images'
    output_dir = 'output_images'
    background_path = 'background_images/BG+1-1920w.webp'  # Path to your background image

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # List all images in the input directory
    image_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for image_file in image_files:
            input_path = os.path.join(input_dir, image_file)
            file_name, file_ext = os.path.splitext(image_file)
            output_file_name = f"{file_name}_{RESULT_MODE}{file_ext}"
            output_path = os.path.join(output_dir, output_file_name)
            tasks.append(process_image_bg(session, input_path, output_path, background_path))

        # Process all images concurrently
        await asyncio.gather(*tasks)

    print('💬 All images have been processed and saved to the output_images directory.')


if __name__ == '__main__':
    # Run async function in asyncio loop.
    asyncio.run(main())
