from twilio.rest import Client

# Twilio credentials
ACCOUNT_SID = "AC20917bc01f16312181d5036ef679f53a"
AUTH_TOKEN = "29f89587ddc864f13bf24a8e1ce33b01"
TWILIO_PHONE_NUMBER = "+17622262729"

# Initialize Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms_notification(accident_location, recipients):
    """
    Sends an SMS notification to the specified recipients with a response link.
    
    Args:
    - accident_location (str): Location of the accident.
    - recipients (dict): Dictionary with recipient roles and their phone numbers.
    """

    # Base URL for local server
    base_response_url = "https://unbiased-factually-blowfish.ngrok-free.app"

    for role, phone_number in recipients.items():
        # Generate response link for the recipient
        response_link = f"{base_response_url}/respond?responder={role}"
        message_body = (
            f"Accident Alert! An accident has occurred at: {accident_location}. "
            f"Click here to respond: {response_link}"
        )

        try:
            # Send SMS
            message = client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            print(f"Notification sent to {role}: Message SID {message.sid}")
        except Exception as e:
            print(f"Failed to send notification to {role}: {e}")

def detect_accident_and_notify(location, is_accident_detected, recipient_phone_numbers):
    """
    Detects an accident and triggers SMS notifications if confirmed.
    
    Args:
    - location (str): The location where the accident occurred.
    - is_accident_detected (bool): Whether the accident has been detected.
    - recipient_phone_numbers (dict): Dictionary of recipient roles and their phone numbers.
    """
    if is_accident_detected:
        print(f"Accident detected at {location}. Sending notifications...")
        send_sms_notification(location, recipient_phone_numbers)
    else:
        print("No accident detected. No notifications sent.")

if __name__ == "__main__":
    # Simulate accident detection
    accident_location = "https://maps.app.goo.gl/J9bRGED7YZpUhKXm9"
    is_accident_detected = True

    # Phone numbers for recipients
    recipient_phone_numbers = {
        "Ambulance": "+919141137749",
    }

    detect_accident_and_notify(accident_location, is_accident_detected, recipient_phone_numbers)
