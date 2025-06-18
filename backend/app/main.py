import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta, UTC
import os
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['blogquest']
articles_collection = db['articles']

# Create TTL index for automatic deletion
articles_collection.create_index("expireAt", expireAfterSeconds=0)

def scrape_and_save(url):
    try:
        # Scrape the webpage
        web = requests.get(url)
        soup = BeautifulSoup(web.content, 'html.parser')
        
        # Extract the text content
        text = ' '.join(soup.get_text().split())
        
        # Get domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        # Create article document
        article = {
            'title': soup.title.string if soup.title else 'Untitled',
            'content': text,
            'url': url,
            'scraped_at': datetime.now(UTC),
            'expireAt': datetime.now(UTC) + timedelta(minutes=30),
            'source': domain
        }
        
        # Save to database
        result = articles_collection.insert_one(article)
        print(f"Article saved successfully with ID: {result.inserted_id}")
        
        return article
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    url = input("\nEnter the URL to scrape: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        print("Please enter a valid URL starting with http:// or https://")
        exit()
        
    print(f"\nScraping: {url}")
    result = scrape_and_save(url)
    
    if result:
        print("Scraping completed successfully!")
    else:
        print("Failed to scrape the URL.")
    exit()