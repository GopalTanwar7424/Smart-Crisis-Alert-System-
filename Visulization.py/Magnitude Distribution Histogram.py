import matplotlib.pyplot as plt
import json
import re

# Load real-time data and extract magnitudes
with open('data/crisis_tweets.json', 'r') as f: data = json.load(f)['crisis_tweets']
magnitudes = [float(re.search(r'[Mm]\s*(\d+\.\d+)', t.get('original_text','')).group(1)) for t in data if re.search(r'[Mm]\s*(\d+\.\d+)', t.get('original_text',''))]

# Create histogram
plt.hist(magnitudes, bins=8, color='red', alpha=0.7, edgecolor='black')
plt.axvline(sum(magnitudes)/len(magnitudes), color='blue', linestyle='--', linewidth=2, label=f'Average: {sum(magnitudes)/len(magnitudes):.2f}')
plt.xlabel('Earthquake Magnitude'); plt.ylabel('Frequency'); plt.title('Magnitude Distribution Histogram')
plt.legend(); plt.grid(True, alpha=0.3); plt.show()