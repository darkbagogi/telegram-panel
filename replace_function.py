#!/usr/bin/env python3
# Script to replace the send_promo_message function in main.py

# Read the original file
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Read the new function
with open('promo_message_fix.py', 'r', encoding='utf-8') as f:
    new_function_lines = f.readlines()

# Remove the comment line from new function
new_function_lines = [line for line in new_function_lines if not line.strip().startswith('#')]

# Find the start and end of the old function
start_line = None
end_line = None

for i, line in enumerate(lines):
    if line.strip() == 'async def send_promo_message():':
        start_line = i
    elif start_line is not None and line.strip() == 'async def main():':
        end_line = i
        break

if start_line is None or end_line is None:
    print(f"Error: Could not find function boundaries")
    print(f"start_line: {start_line}, end_line: {end_line}")
    exit(1)

print(f"Found function from line {start_line+1} to {end_line}")

# Replace the function
new_lines = lines[:start_line] + new_function_lines + ['\n'] + lines[end_line:]

# Write the new file
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Function replaced successfully!")
