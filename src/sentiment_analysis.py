from textblob import TextBlob
import json

# Load cleaned tweets
with open("data/cleaned_tweets.json", "r") as f:
    cleaned = json.load(f)

# Add sentiment scores
for tweet in cleaned:
    if "cleaned_text" in tweet:
        blob = TextBlob(tweet["cleaned_text"])
        tweet["polarity"] = blob.sentiment.polarity
        tweet["subjectivity"] = blob.sentiment.subjectivity
        tweet["sentiment"] = (
            "positive" if blob.sentiment.polarity > 0
            else "negative" if blob.sentiment.polarity < 0
            else "neutral"
        )
    else:
        print("⚠️ Skipping tweet with no 'cleaned_text' key:", tweet)

# Save with sentiments
with open("data/sentiment_tweets.json", "w") as f:
    json.dump(cleaned, f, indent=4)

print("✅ Sentiment analysis complete. Saved to data/sentiment_tweets.json")
