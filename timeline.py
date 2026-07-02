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
