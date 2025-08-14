import json
import re
import string

def clean_crisis_text(text):
    """Clean text while preserving important crisis information"""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs but keep the rest
    text = re.sub(r"http\S+", "", text)
    
    # Remove @ mentions and hashtags (not relevant for RSS data)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#\w+", "", text)
    
    # Clean HTML-like tags that appear in RSS feeds
    text = re.sub(r"<[^>]+>", "", text)
    
    # Fix common RSS feed artifacts
    text = re.sub(r"dldttimedtdd", " time: ", text)
    text = re.sub(r"dddd", " ", text)
    text = re.sub(r"utcdddd", " utc ", text)
    text = re.sub(r"epicenterdddtlocationdtdd", " epicenter: ", text)
    text = re.sub(r"dddtdepthdtdd", " depth: ", text)
    text = re.sub(r"midddl", " miles", text)
    text = re.sub(r"degn", "°N", text)
    text = re.sub(r"degw", "°W", text)
    text = re.sub(r"deged", "°E", text)
    
    # Keep important punctuation (periods for decimals, commas for coordinates)
    # Only remove excessive punctuation
    text = re.sub(r"[^\w\s\.\,\:\-\°]", "", text)
    
    # Clean up extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

# Load raw tweets
try:
    with open("data/raw_tweets.json", "r", encoding="utf-8") as f:
        tweets = json.load(f)
    print(f"✅ Loaded {len(tweets)} raw tweets")
except Exception as e:
    print(f"❌ Error loading raw tweets: {e}")
    exit()

cleaned = []

for tweet in tweets:
    original_text = tweet.get("text", "")
    cleaned_text = clean_crisis_text(original_text)
    
    cleaned.append({
        "id": tweet["id"],
        "created_at": tweet["created_at"],
        "user": tweet["user"],
        "source": tweet.get("source", "unknown"),
        "url": tweet.get("url", ""),
        "original_text": original_text,  # Keep original for reference
        "cleaned_text": cleaned_text
    })

# Save cleaned tweets
try:
    with open("data/cleaned_tweets.json", "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
    print("✅ Preprocessing complete. Saved to data/cleaned_tweets.json")
    
    # Show sample of cleaned data
    print(f"\n📝 Sample cleaned tweets:")
    for i, tweet in enumerate(cleaned[:3]):
        print(f"{i+1}. Original: {tweet['original_text'][:80]}...")
        print(f"   Cleaned:  {tweet['cleaned_text'][:80]}...")
        print()
        
except Exception as e:
    print(f"❌ Error saving cleaned tweets: {e}")