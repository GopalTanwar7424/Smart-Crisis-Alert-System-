import matplotlib.pyplot as plt
import json

# Load real-time data and extract locations
with open('data/crisis_tweets.json', 'r') as f: data = json.load(f)['crisis_tweets']
locations = ['Hawaii' if 'hawaii' in t.get('original_text','').lower() else 'Alaska' if 'alaska' in t.get('original_text','').lower() else 'California' if 'ca:' in t.get('original_text','').lower() else 'Oklahoma' if 'oklahoma' in t.get('original_text','').lower() else 'Texas' if 'texas' in t.get('original_text','').lower() else 'Other' for t in data]

# Count earthquakes per location
location_counts = {loc: locations.count(loc) for loc in set(locations) if locations.count(loc) > 0}

# Create bar chart
plt.bar(location_counts.keys(), location_counts.values(), color=['red', 'blue', 'green', 'orange', 'purple'][:len(location_counts)], alpha=0.7)
for i, (loc, count) in enumerate(location_counts.items()): plt.text(i, count + 0.1, str(count), ha='center', fontweight='bold')
plt.xlabel('Location'); plt.ylabel('Number of Earthquakes'); plt.title('Earthquake Crises by Location')
plt.xticks(rotation=45); plt.grid(True, alpha=0.3, axis='y'); plt.show()