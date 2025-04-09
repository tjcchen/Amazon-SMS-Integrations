# Amazon Pinpoint Integration Guide

This guide explains how to integrate Amazon Pinpoint for sending SMS messages in your Python applications, with advanced features compared to SNS.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Setup and Configuration](#setup-and-configuration)
4. [Implementation](#implementation)
5. [Usage Examples](#usage-examples)
6. [Advanced Features](#advanced-features)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

Amazon Pinpoint is a flexible and scalable outbound and inbound marketing communications service. Unlike Amazon SNS, which is primarily for simple notifications, Pinpoint offers additional features like segmentation, campaigns, analytics, and multi-channel communication. For SMS messaging, Pinpoint provides more detailed delivery metrics and campaign management capabilities.

## Prerequisites

- An AWS account
- Python 3.6 or later
- boto3 library
- python-dotenv library
- A Pinpoint project set up in your AWS account

## Setup and Configuration

### 1. Create a Pinpoint Project

1. Log in to your AWS Management Console
2. Navigate to the Amazon Pinpoint service
3. Click "Create a project" and enter a project name
4. Enable the SMS channel in your project settings:
   - Select your project
   - Navigate to "Settings" in the left sidebar
   - Click on "SMS and voice"
   - Click "Enable SMS channel"

### 2. Configure SMS Settings

1. In your Pinpoint project settings under "SMS and voice":
   - Set your default message type (Transactional or Promotional)
   - Configure spending limits
   - Set up a dedicated origination identity (optional but recommended for production)

### 3. Request Production Access (When Ready)

By default, your account is in sandbox mode, which limits SMS sending. To move to production:
1. In the AWS Console, go to "Support Center"
2. Create a new case, choose "Service Limit Increase"
3. Select "Pinpoint" as the service, and "SMS Production Access" as the limit type
4. Complete the request form with details about your SMS use case

### 4. Set Up Environment Variables

Create a `.env` file in your project root with the following parameters:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_preferred_region  # e.g., us-east-1
PINPOINT_PROJECT_ID=your_pinpoint_project_id
```

### 5. Install Required Dependencies

```bash
pip install boto3 python-dotenv
```

## Implementation

This project includes a Python module (`pinpoint/sms_sender.py`) that handles SMS sending through Amazon Pinpoint:

```python
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
```

## Usage Examples

### Basic Usage

```python
from pinpoint.sms_sender import send_sms

# Send an SMS message using project ID from .env
phone_number = "+12363005078"  # Replace with a verified number
message = "Hello from my Pinpoint application!"
send_sms(phone_number, message)

# Or specify project ID explicitly
project_id = "8367e8209e234a2aa6b772f98e41557d"  # Your Pinpoint project ID
send_sms(phone_number, message, project_id)
```

### Sending to Multiple Recipients

```python
from pinpoint.sms_sender import send_sms

phone_numbers = ["+12363005078", "+14155552671"]  # Replace with verified numbers
message = "Important notification for all users!"
project_id = "8367e8209e234a2aa6b772f98e41557d"  # Your Pinpoint project ID

for number in phone_numbers:
    send_sms(number, message, project_id)
```

### Setting Message Type

```python
from pinpoint.sms_sender import send_sms

phone_number = "+12363005078"
message = "Check out our latest promotion!"
project_id = "8367e8209e234a2aa6b772f98e41557d"

# Use PROMOTIONAL type for marketing messages
send_sms(phone_number, message, project_id, message_type="PROMOTIONAL")
```

## Advanced Features

### 1. Creating Segments for Targeted Messaging

Pinpoint allows you to create segments for more targeted messaging:

```python
def create_segment(project_id, segment_name, phone_numbers):
    response = pinpoint_client.create_segment(
        ApplicationId=project_id,
        WriteSegmentRequest={
            'Name': segment_name,
            'SegmentGroups': {
                'Groups': [
                    {
                        'SourceType': 'IMPORT',
                        'Dimensions': [
                            {
                                'DimensionType': 'INCLUSIVE',
                                'Values': phone_numbers
                            }
                        ]
                    }
                ]
            }
        }
    )
    return response['SegmentResponse']['Id']
```

### 2. Creating and Scheduling Campaigns

For recurring messages or large-scale campaigns:

```python
def create_campaign(project_id, segment_id, campaign_name, message):
    response = pinpoint_client.create_campaign(
        ApplicationId=project_id,
        WriteCampaignRequest={
            'Name': campaign_name,
            'SegmentId': segment_id,
            'Schedule': {
                'StartTime': 'IMMEDIATE'
            },
            'MessageConfiguration': {
                'SMSMessage': {
                    'Body': message,
                    'MessageType': 'TRANSACTIONAL'
                }
            }
        }
    )
    return response['CampaignResponse']['Id']
```

### 3. Tracking and Analytics

Pinpoint provides rich analytics that you can access programmatically:

```python
def get_campaign_analytics(project_id, campaign_id):
    response = pinpoint_client.get_campaign_activities(
        ApplicationId=project_id,
        CampaignId=campaign_id
    )
    return response['ActivitiesResponse']['Item']
```

## Best Practices

1. **Message Type Selection**:
   - Use `TRANSACTIONAL` for time-sensitive messages (higher reliability)
   - Use `PROMOTIONAL` for marketing messages (more cost-effective)

2. **Segmentation Strategy**:
   - Group users with similar characteristics for targeted campaigns
   - Use dynamic segments for evolving user populations

3. **Message Content**:
   - Keep messages concise (SMS has a 160 character limit per segment)
   - Include an opt-out option for marketing messages (required by regulations)
   - Personalize messages when possible using Pinpoint's attributes

4. **Compliance and Regulations**:
   - Follow local SMS regulations for each country you send to
   - Maintain proper opt-in/opt-out records
   - Adhere to sending time restrictions

5. **Cost Management**:
   - Set spending limits in your AWS Pinpoint settings
   - Monitor usage patterns and adjust as needed
   - Use promotional message type for non-critical messages

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Failures**:
   - Verify your AWS credentials are correct
   - Check if your IAM user has the `AmazonPinpointFullAccess` policy attached, this should be a custom inline policy, for example:
    
   ```json
   {
	    "Version": "2012-10-17",
	    "Statement": [
			{
				"Effect": "Allow",
				"Action": [
					"mobiletargeting:SendMessages"
				],
				"Resource": "*"
			}
		]
   }
   ```

2. **Project ID Issues**:
   - Ensure you're using the correct Pinpoint project ID
   - Verify the project is correctly set up with SMS channel enabled

3. **SMS Not Delivered**:
   - In sandbox mode, verify the recipient's phone number is confirmed
   - Check if you've exceeded your spending limit
   - Verify the phone number format (include country code with + prefix)

4. **Campaign Failures**:
   - Verify your segment contains valid endpoints
   - Check that your message content meets the requirements
   - Review campaign execution metrics in the Pinpoint console

---

For more detailed information, refer to the [official Amazon Pinpoint documentation](https://docs.aws.amazon.com/pinpoint/latest/userguide/welcome.html).
