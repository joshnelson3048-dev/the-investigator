from collections import Counter

# Step 1: Open and read the log file
with open("server_access.log", "r") as log_file:
    lines = log_file.readlines()

# Step 2: Keep only lines that contain a failed login
failed_lines = [line for line in lines if "FAILED LOGIN" in line]

# Step 3: Extract the IP address from each failed login line
ips = []
for line in failed_lines:
    # IP appears after "from " (e.g. "... from 192.168.1.50" or "... from 203.0.113.42 (Moscow)")
    ip_part = line.split("from ")[1].strip()
    ip = ip_part.split()[0]
    ips.append(ip)

# Step 4: Count how many times each IP appears
ip_counts = Counter(ips)

# Step 5: Print a summary sorted from most to fewest failed attempts
print("=== Failed Login Summary ===")
for ip, count in ip_counts.most_common():
    line = f"{ip}: {count} failed attempt(s)"
    if count >= 3:
        line += " ⚠ LIKELY BRUTE FORCE"
    print(line)
