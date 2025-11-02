import asyncio
import json
import os

import aiohttp
from bs4 import BeautifulSoup

# Folder to store text files in
dataset_folder = "dataset/data/scraped"
os.makedirs(dataset_folder, exist_ok=True)


# Function to fetch the url contents
# https://dev.to/hexshift/how-to-make-multiple-http-requests-concurrently-in-python-using-asyncio-and-aiohttp-2jd1
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


# Function to fetch
# https://dev.to/hexshift/how-to-make-multiple-http-requests-concurrently-in-python-using-asyncio-and-aiohttp-2jd1
async def main(urls: str):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)

        for content in responses:
            # Create a soup to parse html content
            soup = BeautifulSoup(content, "html.parser")

            # Parse filename from title
            file_name = (
                soup.title.string.lower().replace(" ", "_").replace("/", "_") + ".txt"
            )

            with open(f"{dataset_folder}/{file_name}", "w") as file:
                file.writelines(soup.get_text(separator=" ", strip=True))


if __name__ == "__main__":
    # Read the file with links
    crawled_filename = "dataset/data/crawled/links.json"
    with open(crawled_filename, "r") as file:
        crawled_links = json.load(file)

    asyncio.run(main(crawled_links))
