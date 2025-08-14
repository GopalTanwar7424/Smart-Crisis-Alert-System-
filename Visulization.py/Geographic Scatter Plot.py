import matplotlib.pyplot as plt
import json
import re

# Load real-time data and extract coordinates/magnitudes
with open('data/crisis_tweets.json', 'r') as f: data = json.load(f)['crisis_tweets']
coords = {t.get('original_text',''): ((-155.5,19.9) if 'hawaii' in t.get('original_text','').lower() else (-149.9,61.2) if 'alaska' in t.get('original_text','').lower() else (-119.4,36.8) if 'ca:' in t.get('original_text','').lower() else (-97.5,35.5) if 'oklahoma' in t.get('original_text','').lower() else None, float(re.search(r'[Mm]\s*(\d+\.\d+)', t.get('original_text','')).group(1)) if re.search(r'[Mm]\s*(\d+\.\d+)', t.get('original_text','')) else 0) for t in data}
valid_data = [(coord[0], coord[1]) for coord in coords.values() if coord[0] and coord[1] > 0]
lons, lats = zip(*[(d[0][0], d[0][1]) for d in valid_data])
mags = [d[1] for d in valid_data]

# Plot real-time earthquake data
plt.scatter(lons, lats, s=[m*100 for m in mags], alpha=0.7, c=mags, cmap='Reds')
plt.xlabel('Longitude'); plt.ylabel('Latitude'); plt.title('Real-Time Earthquake Distribution')
plt.colorbar(label='Magnitude'); plt.show()