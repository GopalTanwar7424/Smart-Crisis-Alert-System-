import matplotlib.pyplot as plt
import json
import re

# Load real-time data and extract time (hour) and magnitudes
with open('data/crisis_tweets.json', 'r') as f: data = json.load(f)['crisis_tweets']
time_mag_data = [(int(re.search(r'(\d{2}):(\d{2})', t.get('original_text','')).group(1)), float(re.search(r'[Mm]\s*(\d+\.\d+)', t.get('original_text','')).group(1))) for t in data if re.search(r'(\d{2}):(\d{2})', t.get('original_text','')) and re.search(r'[Mm]\s*(\d+\.\d+)', t.get('original_text',''))]

# Separate hours and magnitudes
hours, magnitudes = zip(*time_mag_data) if time_mag_data else ([], [])

# Create timeline plot
plt.scatter(hours, magnitudes, s=100, alpha=0.7, c=magnitudes, cmap='plasma')
plt.plot(hours, magnitudes, alpha=0.5, color='cyan', linewidth=1)
plt.xlabel('Hour of Day (UTC)'); plt.ylabel('Earthquake Magnitude'); plt.title('Earthquake Timeline Analysis')
plt.colorbar(label='Magnitude'); plt.grid(True, alpha=0.3); plt.show()