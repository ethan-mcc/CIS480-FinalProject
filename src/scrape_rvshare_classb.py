"""
RVshare Class B Scraper
Scrapes Class B RV listings from RVshare.com focusing on:
- Vehicle year
- Nightly price
- Location (for geographic analysis)
- Detailed amenities (TV, bathroom sink, etc.)
"""

import scrapy
from scrapy.crawler import CrawlerProcess
import json
import re
from datetime import datetime

class ClassBRVItem(scrapy.Item):
    """Define the data structure for Class B RV listings"""
    listing_id = scrapy.Field()
    name = scrapy.Field()
    year = scrapy.Field()
    make = scrapy.Field()
    model = scrapy.Field()
    price_nightly = scrapy.Field()
    price_weekly = scrapy.Field()
    price_monthly = scrapy.Field()
    location = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    sleeps = scrapy.Field()
    length = scrapy.Field()
    # Amenities - broken down by category
    has_shower = scrapy.Field()
    has_toilet = scrapy.Field()
    has_bathroom_sink = scrapy.Field()
    has_refrigerator = scrapy.Field()
    has_microwave = scrapy.Field()
    has_kitchen_sink = scrapy.Field()
    has_stove = scrapy.Field()
    has_oven = scrapy.Field()
    has_tv = scrapy.Field()
    has_dvd_player = scrapy.Field()
    has_radio = scrapy.Field()
    has_bluetooth = scrapy.Field()
    has_ac = scrapy.Field()
    has_heating = scrapy.Field()
    has_generator = scrapy.Field()
    has_solar = scrapy.Field()
    has_awning = scrapy.Field()
    has_backup_camera = scrapy.Field()
    # Raw amenity lists for reference
    bathroom_amenities = scrapy.Field()
    kitchen_amenities = scrapy.Field()
    entertainment_amenities = scrapy.Field()
    climate_amenities = scrapy.Field()
    other_amenities = scrapy.Field()
    
class RVShareClassBSpider(scrapy.Spider):
    name = 'rvshare_classb'
    allowed_domains = ['rvshare.com']
    
    # start with major cities to get good coverage
    start_urls = [
        'https://rvshare.com/rv-rental/los-angeles-ca',
        'https://rvshare.com/rv-rental/san-francisco-ca',
        'https://rvshare.com/rv-rental/san-diego-ca',
        'https://rvshare.com/rv-rental/seattle-wa',
        'https://rvshare.com/rv-rental/portland-or',
        'https://rvshare.com/rv-rental/denver-co',
        'https://rvshare.com/rv-rental/phoenix-az',
        'https://rvshare.com/rv-rental/austin-tx',
        'https://rvshare.com/rv-rental/miami-fl',
        'https://rvshare.com/rv-rental/new-york-ny',
        'https://rvshare.com/rv-rental/chicago-il',
        'https://rvshare.com/rv-rental/boston-ma',
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 2,  # be respectful 2 second delay between requests
        'CONCURRENT_REQUESTS': 1,
        'FEEDS': {
            '../Data/raw/rvshare_classb_scraped.json': {
                'format': 'json',
                'overwrite': True,
            }
        }
    }
    
    def parse(self, response):
        """Parse city search results page"""
        self.logger.info(f"Parsing city page: {response.url}")
        
        # find all rv listing cards
        # note xpath selectors may need updating based on current rvshare structure
        listings = response.css('div[data-testid="search-result-card"]')
        
        if not listings:
            # try alternative selector
            listings = response.css('div.rv-card, div.listing-card')
        
        self.logger.info(f"Found {len(listings)} listings on page")
        
        for listing in listings:
            # extract listing url
            listing_url = listing.css('a::attr(href)').get()
            if listing_url:
                if not listing_url.startswith('http'):
                    listing_url = response.urljoin(listing_url)
                
                # check if its a class b from the preview
                vehicle_type = listing.css('span.vehicle-type::text, div.rv-type::text').get()
                if vehicle_type and 'class b' in vehicle_type.lower():
                    yield scrapy.Request(listing_url, callback=self.parse_listing)
        
        # follow pagination
        next_page = response.css('a[rel="next"]::attr(href), a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
    
    def parse_listing(self, response):
        """Parse individual RV listing page"""
        self.logger.info(f"Parsing listing: {response.url}")
        
        item = ClassBRVItem()
        
        # extract listing id from url
        listing_id_match = re.search(r'/(\d+)/?$', response.url)
        item['listing_id'] = listing_id_match.group(1) if listing_id_match else None
        
        # basic info
        item['name'] = response.css('h1.rv-title::text, h1[data-testid="rv-title"]::text').get()
        
        # extract year make model from title or structured data
        title = item['name'] or ''
        year_match = re.search(r'(19|20)\d{2}', title)
        item['year'] = int(year_match.group(0)) if year_match else None
        
        # pricing
        price_nightly = response.css('span[data-testid="nightly-rate"]::text, div.nightly-rate span::text').get()
        item['price_nightly'] = self.clean_price(price_nightly)
        
        price_weekly = response.css('span[data-testid="weekly-rate"]::text, div.weekly-rate span::text').get()
        item['price_weekly'] = self.clean_price(price_weekly)
        
        price_monthly = response.css('span[data-testid="monthly-rate"]::text, div.monthly-rate span::text').get()
        item['price_monthly'] = self.clean_price(price_monthly)
        
        # location
        location = response.css('div.location::text, span[data-testid="location"]::text').get()
        item['location'] = location
        if location:
            parts = location.split(',')
            if len(parts) >= 2:
                item['city'] = parts[0].strip()
                item['state'] = parts[-1].strip()
        
        # specs
        sleeps = response.css('span[data-testid="sleeps"]::text, div.sleeps::text').get()
        if sleeps:
            sleeps_match = re.search(r'\d+', sleeps)
            item['sleeps'] = int(sleeps_match.group(0)) if sleeps_match else None
        
        length = response.css('span[data-testid="length"]::text, div.length::text').get()
        item['length'] = length
        
        # amenities extract from amenity sections
        bathroom_amenities = response.css('div[data-id="bathroom-amenities"] li::text, div.bathroom-amenities li::text').getall()
        kitchen_amenities = response.css('div[data-id="kitchen-amenities"] li::text, div.kitchen-amenities li::text').getall()
        entertainment_amenities = response.css('div[data-id="entertainment-amenities"] li::text, div.entertainment-amenities li::text').getall()
        climate_amenities = response.css('div[data-id="temperature-amenities"] li::text, div.climate-amenities li::text').getall()
        other_amenities = response.css('div[data-id="other-amenities"] li::text, div.other-amenities li::text').getall()
        
        # store raw amenity lists
        item['bathroom_amenities'] = bathroom_amenities
        item['kitchen_amenities'] = kitchen_amenities
        item['entertainment_amenities'] = entertainment_amenities
        item['climate_amenities'] = climate_amenities
        item['other_amenities'] = other_amenities
        
        # create binary amenity flags
        all_amenities = ' '.join(bathroom_amenities + kitchen_amenities + entertainment_amenities + climate_amenities + other_amenities).lower()
        
        # bathroom
        item['has_shower'] = 1 if 'shower' in all_amenities else 0
        item['has_toilet'] = 1 if 'toilet' in all_amenities else 0
        item['has_bathroom_sink'] = 1 if 'bathroom sink' in all_amenities else 0
        
        # kitchen
        item['has_refrigerator'] = 1 if 'refrigerator' in all_amenities or 'fridge' in all_amenities else 0
        item['has_microwave'] = 1 if 'microwave' in all_amenities else 0
        item['has_kitchen_sink'] = 1 if 'kitchen sink' in all_amenities or 'sink' in all_amenities else 0
        item['has_stove'] = 1 if 'stove' in all_amenities or 'range' in all_amenities else 0
        item['has_oven'] = 1 if 'oven' in all_amenities else 0
        
        # entertainment
        item['has_tv'] = 1 if 'tv' in all_amenities or 'television' in all_amenities else 0
        item['has_dvd_player'] = 1 if 'dvd' in all_amenities else 0
        item['has_radio'] = 1 if 'radio' in all_amenities or 'am/fm' in all_amenities else 0
        item['has_bluetooth'] = 1 if 'bluetooth' in all_amenities else 0
        
        # climate
        item['has_ac'] = 1 if 'air conditioning' in all_amenities or 'a/c' in all_amenities or 'ac' in all_amenities else 0
        item['has_heating'] = 1 if 'heat' in all_amenities or 'furnace' in all_amenities else 0
        
        # other
        item['has_generator'] = 1 if 'generator' in all_amenities else 0
        item['has_solar'] = 1 if 'solar' in all_amenities else 0
        item['has_awning'] = 1 if 'awning' in all_amenities else 0
        item['has_backup_camera'] = 1 if 'backup camera' in all_amenities or 'rear camera' in all_amenities else 0
        
        yield item
    
    def clean_price(self, price_str):
        """Clean price string to numeric value"""
        if not price_str:
            return None
        # remove commas and any text
        cleaned = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(cleaned)
        except:
            return None

def run_scraper():
    """Run the scraper"""
    process = CrawlerProcess()
    process.crawl(RVShareClassBSpider)
    process.start()

if __name__ == '__main__':
    print("="*60)
    print("RVshare Class B Scraper")
    print("="*60)
    print("\nStarting scraper...")
    print("This will take several minutes due to respectful delays.")
    print("\nOutput will be saved to: Data/raw/rvshare_classb_scraped.json")
    print("="*60)
    run_scraper()

