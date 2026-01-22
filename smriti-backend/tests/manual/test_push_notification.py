"""
Test script for Firebase push notifications
Run this to test sending a notification to a device
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Setup logging first
from app.config.logging_config import setup_logging
setup_logging()

# Initialize Firebase
from app.utils.firebase import init_firebase
init_firebase()

from app.utils.firebase import send_push_notification

def test_notification():
    """Send a test notification"""
    
    # Replace with your actual FCM device token
    # You'll get this from the frontend when a user registers
    test_token = input("Enter your FCM device token: ").strip()
    
    if not test_token:
        print("❌ No token provided")
        return
    
    print(f"\n📤 Sending test notification to token: {test_token[:20]}...")
    
    result = send_push_notification(
        tokens=[test_token],
        title="Test from Smriti Backend",
        body="If you see this, Firebase push notifications are working! 🎉",
        data={
            "test": "true",
            "timestamp": "now"
        }
    )
    
    print(f"\n✅ Result: {result}")
    
    if result.get("success", 0) > 0:
        print("🎉 Notification sent successfully!")
    else:
        print("❌ Failed to send notification")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_notification()
