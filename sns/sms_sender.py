import os
import boto3
from dotenv import load_dotenv

# Load AWS credentials from .env file
load_dotenv()

# Get credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Create the SNS client
sns_client = boto3.client(
    "sns",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# Optional: Configure SMS type as Transactional (safer for most use cases)
def set_sms_attributes():
    sns_client.set_sms_attributes(
        attributes={
            "DefaultSMSType": "Transactional"
        }
    )

# Send SMS to a verified phone number (must be added in Sandbox first)
def send_sms(phone_number: str, message: str):
    try:
        set_sms_attributes()
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        print("✅ SMS sent! Message ID:", response['MessageId'])
    except Exception as e:
        print("❌ Failed to send SMS:", str(e))

# Example usage
if __name__ == "__main__":
    # Use your verified sandbox number here (e.g., US number)
    verified_phone_number = "+12363005078"
    message = "Hello from AWS SNS Sandbox test!"
    send_sms(verified_phone_number, message)
