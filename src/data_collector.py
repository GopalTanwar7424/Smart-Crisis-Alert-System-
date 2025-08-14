import json
import os
import time
import logging
import sys
from datetime import datetime
import requests

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/collector.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class SmartCrisisDataCollector:
    def __init__(self):
        self.output_file = "data/raw_tweets.json"
        self.max_tweets_per_cycle = 50
        self.refresh_interval = 300  # 5 minutes
        self.crisis_keywords = [
            "earthquake", "flood", "fire", "storm", "explosion", "landslide",
            "tsunami", "cyclone", "hurricane", "tornado", "volcano", "eruption",
            "accident", "crash", "collapse", "blast", "riot", "shooting",
            "protest", "emergency", "disaster", "rescue", "injured", "fatalities"
        ]
        os.makedirs("data", exist_ok=True)
        
        # Setup requests session
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Crisis Data Collector 1.0'})

    def build_search_query(self):
        return "(" + " OR ".join(self.crisis_keywords) + ") lang:en"

    def collect_with_snscrape(self):
        try:
            import snscrape.modules.twitter as sntwitter
            import urllib3
            urllib3.disable_warnings()

            query = self.build_search_query()
            tweets = []

            logging.info("Collecting with snscrape...")
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                if i >= self.max_tweets_per_cycle:
                    break
                
                tweets.append({
                    "id": str(tweet.id) if hasattr(tweet, 'id') else f"tweet_{i}",
                    "created_at": tweet.date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(tweet, 'date') and tweet.date else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user": str(tweet.user.id) if hasattr(tweet, 'user') and hasattr(tweet.user, 'id') else 'unknown',
                    "text": str(tweet.content) if hasattr(tweet, 'content') else "",
                    "url": str(tweet.url) if hasattr(tweet, 'url') else "",
                    "source": "snscrape"
                })
            
            logging.info(f"Collected {len(tweets)} tweets")
            return tweets
        except ImportError:
            logging.warning("snscrape not installed")
            return None
        except Exception as e:
            logging.error(f"snscrape failed: {e}")
            return None

    def collect_from_rss_feeds(self):
        rss_feeds = [
            {"url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.atom", "name": "USGS"},
            {"url": "https://alerts.weather.gov/cap/wwaatmget.php?x=0", "name": "Weather"}
        ]
        tweets = []
        
        try:
            import feedparser
        except ImportError:
            logging.warning("feedparser not installed")
            return []
        
        for feed in rss_feeds:
            try:
                response = self.session.get(feed["url"], timeout=30)
                parsed_feed = feedparser.parse(response.content)
                
                for i, entry in enumerate(parsed_feed.entries[:5]):
                    title = getattr(entry, 'title', 'No title')
                    summary = getattr(entry, 'summary', getattr(entry, 'description', ''))[:200]
                    
                    tweets.append({
                        "id": str(hash(entry.link) % (10**10)) if hasattr(entry, 'link') else f"rss_{feed['name']}_{i}",
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "user": f"official_{feed['name'].lower()}",
                        "text": f"{title}: {summary}...",
                        "url": getattr(entry, 'link', ''),
                        "source": "rss"
                    })
                
                logging.info(f"Collected {len([t for t in tweets if feed['name'].lower() in t['user']])} items from {feed['name']}")
            
            except Exception as e:
                logging.error(f"RSS error for {feed['name']}: {e}")
        
        return tweets

    def load_existing_tweets(self):
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logging.info(f"Loaded {len(data)} existing items")
                    return data
            except Exception as e:
                logging.error(f"Error loading tweets: {e}")
                # Backup corrupted file
                if os.path.exists(self.output_file):
                    os.rename(self.output_file, f"{self.output_file}.corrupted")
        return []

    def save_tweets(self, tweets):
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(tweets, f, indent=2, ensure_ascii=False)
            logging.info(f"Saved {len(tweets)} total items")
            return True
        except Exception as e:
            logging.error(f"Error saving tweets: {e}")
            return False

    def collect_tweets(self):
        all_tweets = []
        
        # Try snscrape first
        snscrape_tweets = self.collect_with_snscrape()
        if snscrape_tweets:
            all_tweets.extend(snscrape_tweets)
        
        # Always try RSS feeds
        rss_tweets = self.collect_from_rss_feeds()
        if rss_tweets:
            all_tweets.extend(rss_tweets)
        
        return all_tweets

    def run_continuous_collection(self):
        logging.info("Starting Crisis Data Collector")
        all_tweets = self.load_existing_tweets()
        existing_ids = {str(tweet.get('id')) for tweet in all_tweets if tweet.get('id')}
        cycle_count = 0

        try:
            while True:
                cycle_count += 1
                logging.info(f"Cycle #{cycle_count}")

                new_tweets = self.collect_tweets()
                if new_tweets:
                    unique_tweets = [t for t in new_tweets if str(t.get('id')) not in existing_ids]
                    if unique_tweets:
                        all_tweets.extend(unique_tweets)
                        existing_ids.update(str(t.get('id')) for t in unique_tweets)
                        if self.save_tweets(all_tweets):
                            logging.info(f"Added {len(unique_tweets)} new items. Total: {len(all_tweets)}")
                    else:
                        logging.info("No new unique items found")
                else:
                    logging.warning("No tweets collected this cycle")

                logging.info(f"Waiting {self.refresh_interval} seconds...")
                time.sleep(self.refresh_interval)
        
        except KeyboardInterrupt:
            logging.info("Collection stopped by user")
        except Exception as e:
            logging.error(f"Fatal error: {e}")

def main():
    collector = SmartCrisisDataCollector()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logging.info("Running test mode...")
        tweets = collector.collect_tweets()
        logging.info(f"Test collected {len(tweets)} items")
        
        for i, tweet in enumerate(tweets[:3]):
            print(f"{i+1}. [{tweet.get('source')}] {tweet.get('text', '')[:80]}...")
    else:
        logging.info("Starting continuous collection (Ctrl+C to stop)")
        collector.run_continuous_collection()

if __name__ == "__main__":
    main()