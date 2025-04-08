import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables (if used for region or secret name)
load_dotenv()

def get_aws_secret(secret_name=None, region="ap-southeast-2"):
    if not secret_name:
        secret_name = os.getenv("AWS_SECRET_NAME", "my/project/secrets")

    client = boto3.client('secretsmanager', region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString")
        if secret_string:
            return json.loads(secret_string)
    except Exception as e:
        print(f"Failed to load secrets: {e}")
        return {}

    return {}
