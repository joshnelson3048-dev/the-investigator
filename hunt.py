from collections import defaultdict

# Step 1: Open and read the traffic log
with open("network_traffic.log", "r") as log_file:
    lines = log_file.readlines()

# Step 2: Parse each line into time, source, destination:port, and bytes
pair_counts = defaultdict(int)
pair_times = defaultdict(list)

for line in lines:
    line = line.strip()
    if not line:
        continue

    left, right = line.split(" -> ")
    time, source = left.split()
    dest_port = right.split()[0]

    pair = f"{source} -> {dest_port}"
    pair_counts[pair] += 1
    pair_times[pair].append(time)

# Step 3: Find the (source -> destination:port) pair with the most connections
top_pair = max(pair_counts, key=pair_counts.get)
top_count = pair_counts[top_pair]
top_times = pair_times[top_pair]

# Step 4: Print the beaconing suspect summary
print("=== Beaconing Suspect ===")
print(f"Pair: {top_pair}")
print(f"Connections: {top_count}")
print("Timestamps:")
for time in top_times:
    print(f"  {time}")
