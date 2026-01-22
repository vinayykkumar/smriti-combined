import json
import os

# Read the service account file
try:
    with open('serviceAccountKey.json', 'r') as f:
        data = json.load(f)
        
    # Dump as minified JSON string
    minified_json = json.dumps(data, separators=(',', ':'))
    
    print("\n✅ Copy the following line and paste it as the value for 'FIREBASE_CREDENTIALS_JSON' in Render:\n")
    print(minified_json)
    print("\n")
    
except FileNotFoundError:
    print("❌ serviceAccountKey.json not found!")
