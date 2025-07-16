import json
import matplotlib.pyplot as plt
from PIL import Image  # pentru deschidere imagine


with open("speedtest_results.json", "r") as f:
    data = json.load(f)

threads = data["threads_results"]

# Extrage date pentru grafic
protocols = [t["protocol"] for t in threads]
directions = [t.get("direction", "upload") for t in threads]
speeds = []
labels = []

for idx, t in enumerate(threads):
    sp = float(t["speed"].split()[0])
    unit = t["speed"].split()[1]
    speeds.append(sp)
    labels.append(f"{t['protocol']} T{idx+1}")

# Plot pe threaduri
plt.figure(figsize=(10, 5))
bars = plt.bar(labels, speeds, color='skyblue')
plt.title("Speed per Thread")
plt.xlabel("Thread")
plt.ylabel(f"Speed ({unit})")
plt.ylim(0, max(speeds) * 1.2)

for bar, sp in zip(bars, speeds):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f"{sp:.2f}", ha='center', va='bottom')

plt.tight_layout()
plt.savefig("speedtest_plot.png")
print("[PLOT] Saved as speedtest_plot.png")

# viteza agregata
agg_speed = data["aggregate"]["speed"]
agg_data = data["aggregate"]["data_sent"]
agg_duration = data["aggregate"]["total_duration_s"]

print("\n=== AGGREGATE RESULTS ===")
print(f"Data Sent: {agg_data}")
print(f"Duration: {agg_duration:.2f} s")
print(f"Average Speed: {agg_speed}")

# Deschide imaginea automat pentru vizualizare
try:
    img = Image.open("speedtest_plot.png")
    img.show()
except Exception as e:
    print(f"[ERROR] Nu s-a putut deschide imaginea: {e}")
