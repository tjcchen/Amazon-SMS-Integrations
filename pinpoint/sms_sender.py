import os
import boto3
from dotenv import load_dotenv

# Load AWS credentials from .env file
load_dotenv()

# Get credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
PINPOINT_PROJECT_ID = os.getenv("PINPOINT_PROJECT_ID")

# Initialize the Pinpoint client
pinpoint_client = boto3.client(
    'pinpoint',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def send_sms(phone_number: str, message: str, project_id: str = None, message_type: str = "TRANSACTIONAL"):
    """
    Send SMS using Amazon Pinpoint
    
    Args:
        phone_number (str): The recipient's phone number with country code (e.g., +12363005078)
        message (str): The SMS message body
        project_id (str, optional): The Pinpoint project ID. Defaults to value from .env file.
        message_type (str, optional): SMS message type - TRANSACTIONAL or PROMOTIONAL. Defaults to "TRANSACTIONAL".
    
    Returns:
        dict: Response from the Pinpoint API
    """
    try:
        # Use provided project ID or fall back to .env value
        pinpoint_project_id = project_id or PINPOINT_PROJECT_ID
        
        if not pinpoint_project_id:
            raise ValueError("Pinpoint Project ID is required. Provide it as an argument or set PINPOINT_PROJECT_ID in .env file")
        
        response = pinpoint_client.send_messages(
            ApplicationId=pinpoint_project_id,
            MessageRequest={
                'Addresses': {
                    phone_number: {
                        'ChannelType': 'SMS'
                    }
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'MessageType': message_type  # TRANSACTIONAL or PROMOTIONAL
                    }
                }
            }
        )

        result = response['MessageResponse']['Result'][phone_number]
        print(f"✅ SMS sent via Pinpoint! Status: {result['StatusCode']} - {result['StatusMessage']}")
        print(f"   Message ID: {result.get('MessageId', 'N/A')}")
        return response
    except Exception as e:
        print(f"❌ Failed to send SMS via Pinpoint: {str(e)}")
        raise e

# Example usage
if __name__ == "__main__":
    # Use your verified number and project ID here
    # Where to find project_id:
    # https://us-east-1.console.aws.amazon.com/pinpoint/home?region=us-east-1#/apps/8367e8209e234a2aa6b772f98e41557d/settings/sms
    # the project id is: 8367e8209e234a2aa6b772f98e41557d
    verified_phone_number = "+12363005078"
    message = "👋 Hello from AWS Pinpoint!"
    
    # Option 1: Using project ID from .env file
    send_sms(verified_phone_number, message)
    
    # Option 2: Explicitly providing project ID
    # project_id = "8367e8209e234a2aa6b772f98e41557d"  # Replace with your actual Pinpoint project ID
    # send_sms(verified_phone_number, message, project_id)
