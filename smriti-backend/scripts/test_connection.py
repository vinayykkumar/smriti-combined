"""Quick test to check MongoDB connection"""
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")

if mongodb_uri:
    print(f"Connection string found: {mongodb_uri[:30]}...")
    print(f"Length: {len(mongodb_uri)}")
    
    # Check if password might need encoding
    if "@cluster" in mongodb_uri:
        parts = mongodb_uri.split("@")
        if len(parts) >= 2:
            print("\n[INFO] Connection string structure looks correct")
            
            # Extract username and password
            if "://" in parts[0]:
                creds = parts[0].split("://")[1]
                if ":" in creds:
                    username, password = creds.split(":", 1)
                    print(f"Username: {username}")
                    print(f"Password length: {len(password)} characters")
                    
                    # Check for special characters
                    special_chars = ['@', '#', '$', '%', '&', '/', ':', '?', '=']
                    found_special = [c for c in special_chars if c in password]
                    
                    if found_special:
                        print(f"\n[WARNING] Password contains special characters: {found_special}")
                        print("[INFO] These need to be URL-encoded!")
                        print(f"\nURL-encoded password: {quote_plus(password)}")
                        
                        # Reconstruct the URI with encoded password
                        encoded_uri = mongodb_uri.replace(f":{password}@", f":{quote_plus(password)}@")
                        print(f"\n[SUGGESTION] Update your .env with:")
                        print(f"MONGODB_URI={encoded_uri}")
                    else:
                        print("\n[INFO] No special characters found in password")
else:
    print("[ERROR] MONGODB_URI not found in .env")
