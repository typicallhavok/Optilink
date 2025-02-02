# sos_emergency.py
import os
import tkinter as tk
from tkinter import messagebox
import geocoder
from twilio.rest import Client
from datetime import datetime
from dotenv import load_dotenv  # For .env file support

# Load environment variables
load_dotenv()

# Configuration (store these in .env file)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE')
YOUR_PHONE = os.getenv('YOUR_PHONE')
TEST_EMAIL = "test@example.com"

def get_location():
    """Get approximate location with fallback"""
    try:
        g = geocoder.ip('me')
        if g.ok:
            return f"{g.city}, {g.state}, {g.country} (Lat: {g.lat}, Lng: {g.lng})"
        return "Location unavailable (IP lookup failed)"
    except Exception as e:
        print(f"Location error: {e}")
        return "Location unavailable"

def send_sms(location):
    """Send real SMS with Twilio"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"EMERGENCY ALERT! User needs help at: {location}",
            from_=TWILIO_PHONE,
            to=YOUR_PHONE
        )
        return f"SMS sent! SID: {message.sid}"
    except Exception as e:
        return f"SMS failed: {str(e)}"

def trigger_sos():
    """Handle SOS button press"""
    location = get_location()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    emergency_msg = f"""EMERGENCY ALERT ({timestamp})
    
    User requires immediate assistance!
    Location: {location}
    
    This is an automated test message."""
    
    # Show confirmation
    
    # Send notifications
    print("\n=== EMERGENCY PROTOCOL ACTIVATED ===")
    
    # Simulate email
    print(f"\n[Simulated] Email to {TEST_EMAIL}:\n{emergency_msg}")
    
    # Real SMS
    sms_result = send_sms(location)
    print(f"\nSMS Status: {sms_result}")
    

# Create GUI
# root = tk.Tk()
# root.title("EMERGENCY SYSTEM (TEST)")

# # Warning label
# tk.Label(
#     root,
#     text="⚠️ TEST SYSTEM ONLY ⚠️\nDO NOT USE FOR REAL EMERGENCIES",
#     fg="red",
#     font=("Arial", 14, "bold")
# ).pack(pady=20)

# # SOS Button
# tk.Button(
#     root,
#     text="🆘 EMERGENCY",
#     command=trigger_sos,
#     bg="#ff4444",
#     fg="white",
#     font=("Arial", 24, "bold"),
#     height=2,
#     width=15
# ).pack(pady=20, padx=50)

# # Disclaimer
# tk.Label(
#     root,
#     text="This will send real SMS if configured properly\nusing the Twilio service",
#     fg="gray"
# ).pack(pady=10)

# root.mainloop()