import firebase_admin
from firebase_admin import credentials
import os

if not firebase_admin._apps:
    service_account_path = os.path.join(os.path.dirname(__file__), 'firebase_service_account.json')
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin initialized successfully.")
else:
    print("Firebase Admin already initialized.")

# Test Firebase connection
try:
    from firebase_admin import auth
    # This should work if Firebase is properly configured
    print("✅ Firebase auth module imported successfully")
except Exception as e:
    print("❌ Firebase configuration error:", e)