import json

# Crisis keywords
CRISIS_KEYWORDS = [
    "earthquake", "flood", "fire", "storm", "explosion", "landslide",
    "tsunami", "cyclone", "hurricane", "tornado", "volcano", "eruption",
    "accident", "crash", "emergency", "disaster", "rescue", "injured",
    # USGS/Weather specific terms
    "magnitude", "seismic", "alert", "warning", "severe", "km", "advisory"
]

def is_crisis_tweet(tweet):
    """Check if tweet is crisis-related"""
    text = tweet.get("cleaned_text", "").lower()
    source = tweet.get("source", "")
    user = tweet.get("user", "")
    
    # All RSS data from official sources = crisis
    if source == "rss" or "official" in user:
        return True
    
    # Check for crisis keywords
    return any(keyword in text for keyword in CRISIS_KEYWORDS)

def main():
    # Load cleaned tweets
    try:
        with open("data/cleaned_tweets.json", "r") as f:
            tweets = json.load(f)
        print(f"✅ Loaded {len(tweets)} tweets")
    except:
        print("❌ Error loading cleaned_tweets.json")
        return

    # Analyze tweets
    crisis_tweets = []
    non_crisis_tweets = []
    
    for tweet in tweets:
        if is_crisis_tweet(tweet):
            crisis_tweets.append(tweet)
        else:
            non_crisis_tweets.append(tweet)

    # Results
    print("\n🚨 CRISIS SUMMARY")
    print(f"🔴 Crisis-related tweets: {len(crisis_tweets)}")
    print(f"🟢 Non-crisis tweets: {len(non_crisis_tweets)}")
    print(f"📊 Total tweets: {len(tweets)}")
    
    # Show sample crisis tweets
    print("\n📝 Sample Crisis Tweets:")
    for i, tweet in enumerate(crisis_tweets[:3]):
        text = tweet.get("cleaned_text", "")[:60] + "..."
        print(f"   {i+1}. {text}")

    # Save results
    result = {
        "crisis_tweets": crisis_tweets,
        "non_crisis_tweets": non_crisis_tweets
    }
    
    with open("data/crisis_tweets.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✅ Crisis detection complete. Saved to data/crisis_tweets.json")

if __name__ == "__main__":
    main()