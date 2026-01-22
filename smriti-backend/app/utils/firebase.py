import firebase_admin
from firebase_admin import credentials, messaging
from app.config.settings import settings
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_app = None

import json
import os

def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app
    
    if _firebase_app:
        return _firebase_app
    
    # Try to load from JSON string (Environment Variable) - Preferred for Render/Production
    cred_json = settings.FIREBASE_CREDENTIALS_JSON
    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    
    try:
        if cred_json:
            # Parse JSON string from environment variable
            # Only log a small part to avoid leaking secrets
            logger.info("Loading Firebase credentials from FIREBASE_CREDENTIALS_JSON env var")
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully (from JSON env var)")
            return _firebase_app
            
        elif cred_path and os.path.exists(cred_path):
            # Load from file path (Development)
            logger.info(f"Loading Firebase credentials from file: {cred_path}")
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully (from file)")
            return _firebase_app
            
        else:
            logger.warning("No Firebase credentials found (checked FIREBASE_CREDENTIALS_JSON and FIREBASE_CREDENTIALS_PATH). Push notifications disabled.")
            return None
            
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return None

# Firebase will be initialized explicitly in main.py startup event

def send_push_notification(
    tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Send push notification to multiple devices
    
    Args:
        tokens: List of FCM device tokens
        title: Notification title
        body: Notification body
        data: Optional data payload
    
    Returns:
        Dict with success and failure counts
    """
    if not _firebase_app:
        logger.warning("Firebase not initialized - skipping notification")
        return {"success": 0, "failed": 0, "error": "Firebase not initialized"}
    
    if not tokens:
        return {"success": 0, "failed": 0, "error": "No tokens provided"}
    
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        tokens=tokens,
    )
    
    try:
        response = messaging.send_each_for_multicast(message)
        logger.info(f"Sent notifications: {response.success_count} success, {response.failure_count} failed")
        
        # Log individual failures for debugging
        if response.failure_count > 0:
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    # Note: resp.exception might be a MessagingError object, which has a .code attribute
                    # For more detailed logging, you might want to log resp.exception.code as well.
                    logger.error(f"Failed to send to token at index {idx}: {resp.exception}")
        
        return {
            "success": response.success_count,
            "failed": response.failure_count
        }
    except Exception as e:
        logger.error(f"Failed to send notifications: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {str(e)}")
        return {"success": 0, "failed": len(tokens), "error": str(e)}
