import json
import boto3
import uuid

# Initialize S3 client
s3 = boto3.client("s3")

# Define the S3 bucket name
BUCKET_NAME = "promptbucketakila"

def lambda_handler(event, context):
    try:
        # Parse request body
        body = json.loads(event["body"])
        message = body.get("prompt", "")

        if not message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No message provided"})
            }

        # Generate a unique filename
        file_name = f"messages/{uuid.uuid4()}.txt"

        # Upload message to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=message)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Message saved to S3!", "file": file_name})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
