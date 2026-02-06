"""
Simple diagnostic script to check .env file loading.

Run this script to verify that your .env file is being found and loaded correctly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

print("=" * 70)
print("Environment Configuration Diagnostic")
print("=" * 70)

# 1. Show current working directory
print(f"\n1. Current working directory:")
print(f"   {os.getcwd()}")

# 2. Show script location
script_path = Path(__file__).parent.absolute()
print(f"\n2. Script location:")
print(f"   {script_path}")

# 3. Try to find .env file
print(f"\n3. Searching for .env file...")
dotenv_path = find_dotenv(usecwd=True)

if dotenv_path:
    print(f"   ✓ Found .env file at: {dotenv_path}")
    # Load it
    load_dotenv(dotenv_path)
else:
    print(f"   ✗ No .env file found")
    print(f"   Searched from: {os.getcwd()}")
    # Try loading anyway (checks default locations)
    load_dotenv()

# 4. Check for CMC_API_KEY
print(f"\n4. Checking for CMC_API_KEY environment variable...")
api_key = os.getenv("CMC_API_KEY")

if api_key:
    # Mask the key for security
    if len(api_key) > 12:
        masked = api_key[:8] + "..." + api_key[-4:]
    else:
        masked = "***"
    print(f"   ✓ CMC_API_KEY found: {masked}")
    print(f"   ✓ Key length: {len(api_key)} characters")
else:
    print(f"   ✗ CMC_API_KEY NOT found")
    print(f"\n   Troubleshooting:")
    print(f"   - Make sure you have a .env file in the project root")
    print(f"   - The .env file should contain: CMC_API_KEY=your_api_key_here")
    print(f"   - No quotes needed around the value")
    print(f"   - No spaces around the = sign")

# 5. List all environment variables starting with CMC
print(f"\n5. All CMC-related environment variables:")
cmc_vars = {k: v for k, v in os.environ.items() if k.startswith("CMC")}
if cmc_vars:
    for key, value in cmc_vars.items():
        if "KEY" in key or "SECRET" in key:
            # Mask sensitive values
            if len(value) > 12:
                masked = value[:8] + "..." + value[-4:]
            else:
                masked = "***"
            print(f"   {key} = {masked}")
        else:
            print(f"   {key} = {value}")
else:
    print(f"   No CMC-related environment variables found")

# 6. Check if .env file exists in expected location
print(f"\n6. Checking common .env file locations:")
common_locations = [
    Path.cwd() / ".env",
    script_path / ".env",
    script_path.parent / ".env" if script_path != Path.cwd() else None,
]

for loc in common_locations:
    if loc and loc.exists():
        print(f"   ✓ Found: {loc}")
    elif loc:
        print(f"   ✗ Not found: {loc}")

print("\n" + "=" * 70)
print("Diagnostic complete!")
print("=" * 70)

if not api_key:
    print("\n⚠️  ACTION REQUIRED:")
    print(f"Create a .env file at: {Path.cwd() / '.env'}")
    print("Add this line: CMC_API_KEY=your_actual_api_key")
    print("\n" + "=" * 70)
