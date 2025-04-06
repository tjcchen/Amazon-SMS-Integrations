# Amazon SNS Integration Guide

This guide explains how to integrate Amazon Simple Notification Service (SNS) for sending SMS messages in your Python applications.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Setup and Configuration](#setup-and-configuration)
4. [Implementation](#implementation)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Introduction

Amazon Simple Notification Service (SNS) is a fully managed messaging service that enables you to send SMS messages to mobile phone numbers. This integration guide demonstrates how to implement Amazon SNS for sending SMS messages using Python and the boto3 AWS SDK.

## Prerequisites

- An AWS account
- Python 3.6 or later
- boto3 library
- python-dotenv library

## Setup and Configuration

### 1. Set Up AWS Account for SNS

1. Create or log in to your AWS account
2. Navigate to the SNS service in the AWS Management Console
3. If you're testing in a sandbox environment, you need to add verified phone numbers:
   - Go to "Mobile text messaging (SMS)" in the left sidebar
   - Click on "Sandbox destination phone numbers"
   - Add and verify the phone numbers you want to send messages to

### 2. Create IAM User with SNS Permissions

1. Go to the IAM service in AWS Console
2. Create a new user or use an existing one
3. Attach the `AmazonSNSFullAccess` policy (for development) or create a custom policy with more limited permissions for production
4. Generate and save the Access Key ID and Secret Access Key

### 3. Set Up Environment Variables

Create a `.env` file in your project root with the following parameters:

```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=your_preferred_region  # e.g., us-east-1
```

### 4. Install Required Dependencies

```bash
pip install boto3 python-dotenv
```

## Implementation

This project includes a Python module (`sns/sms_sender.py`) that handles SMS sending through Amazon SNS:

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
        return response
    except Exception as e:
        print("❌ Failed to send SMS:", str(e))
        raise e
```

## Usage Examples

### Basic Usage

```python
from sns.sms_sender import send_sms

# Send an SMS message
phone_number = "+12363005078"  # Replace with a verified number
message = "Hello from my application!"
send_sms(phone_number, message)
```

### Sending to Multiple Recipients

```python
from sns.sms_sender import send_sms

phone_numbers = ["+12363005078", "+14155552671"]  # Replace with verified numbers
message = "Important notification for all users!"

for number in phone_numbers:
    send_sms(number, message)
```

## Best Practices

1. **SMS Type Selection**:
   - Use `Transactional` for time-sensitive messages (higher reliability)
   - Use `Promotional` for marketing messages (more cost-effective)

2. **Error Handling**:
   - Always implement proper error handling when sending SMS
   - Log failures for debugging and monitoring

3. **Message Content**:
   - Keep messages concise (SMS has a 160 character limit per segment)
   - Include an opt-out option for marketing messages
   - Avoid using URL shorteners which may trigger spam filters

4. **Environment Management**:
   - Never hardcode AWS credentials in your code
   - Use different IAM users/roles for development and production

5. **Moving from Sandbox to Production**:
   - Request production access when ready to go live
   - Set a monthly SMS spending limit to avoid unexpected costs
   - Monitor your usage through AWS console

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Failures**:
   - Double-check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   - Ensure the IAM user has the correct SNS permissions

2. **SMS Not Delivered**:
   - In sandbox mode, verify the recipient's phone number is confirmed
   - Check if you've exceeded your spending limit
   - Verify the phone number format (include country code with + prefix)

3. **Rate Limiting**:
   - If sending large volumes, implement exponential backoff for retries
   - Consider using Amazon Pinpoint for high-volume SMS campaigns

4. **Region Issues**:
   - Some features and pricing vary by region
   - Ensure you're using a region that supports SMS messaging

### Monitoring and Logging

In a production environment, consider:

- Setting up CloudWatch alarms for SMS delivery failures
- Using AWS X-Ray for tracing requests
- Implementing detailed logging for troubleshooting

---

For more detailed information, refer to the [official Amazon SNS documentation](https://docs.aws.amazon.com/sns/latest/dg/sns-mobile-phone-number-as-subscriber.html).
