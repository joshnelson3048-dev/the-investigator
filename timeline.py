from datetime import datetime

# Step 1: Read events from both log files
with open("auth_events.log", "r") as auth_file:
    auth_events = auth_file.readlines()

with open("file_events.log", "r") as file_file:
    file_events = file_file.readlines()

# Step 2: Merge all events into one list
all_events = auth_events + file_events

# Step 3: Sort events chronologically (each line starts with date and time)
all_events.sort()

# Step 4: Print the merged timeline, marking key events
print("=== Incident Timeline ===")
for line in all_events:
    line = line.strip()
    if not line:
        continue

    if "SUCCESS LOGIN" in line or ".locked" in line or "READ_ME" in line:
        print(f"*** KEY EVENT *** {line}")
    else:
        print(line)

# Step 5: Calculate dwell time from first successful login to first .locked file
first_success = None
first_locked = None

for line in all_events:
    line = line.strip()
    if not line:
        continue

    timestamp = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")

    if first_success is None and "SUCCESS LOGIN" in line:
        first_success = timestamp
    if first_locked is None and ".locked" in line:
        first_locked = timestamp

if first_success and first_locked:
    dwell_seconds = (first_locked - first_success).total_seconds()
    dwell_minutes = round(dwell_seconds / 60, 1)
    print()
    print(f"Dwell time: {dwell_minutes} minutes (first successful login -> first .locked file)")
