import json
import re
import os

import requests
from bs4 import BeautifulSoup
import backoff

# The blog to crawl
START_URL = "https://blog.papermatch.me/"

# Folder to store the results
data_folder = "dataset/data/"
os.makedirs(data_folder, exist_ok=True)

# File name for the crawled data
crawled_filename = "dataset/data/crawled_links.json"

# Scrape blog for links
# Add backoff for automatic retry in case the page fails 
@backoff.on_exception(backoff.expo, requests.exceptions.RequestException)
def scrape_index(url:str)->bytes:
    
    # Request page 
    response = requests.get(url)
    
    # Raise error for failed requests
    response.raise_for_status()
    
    # return the page content
    return response.content

# Get the blog's frontpage
blog_index = scrape_index(START_URL)

# Create a soup to parse html content
soup = BeautifulSoup(blog_index, 'html.parser')

# Gather all the relative links in the frontpage
relative_links = []
for link in soup.find_all('a'):
    relative_links.append(link.get('href'))

# Filter out the ones that are blog links with a following path
blogs_re = re.compile(r"html\/.+")

def filter_links(relative_links:list)->list:
    filtered_relative_links = []
    
    for relative_link in relative_links:
        match = blogs_re.search(relative_link)
        
        if match:
            filtered_relative_links.append(match.group())
    
    # Return unique blogs list
    return list(set(filtered_relative_links))


relevant_links = [ START_URL + link for link in filter_links(relative_links) ]

print(f"Found {len(relevant_links)} blog links")

# Save the lists to a json file
with open(crawled_filename, 'w') as file:
    json.dump(relevant_links, file, indent=2)