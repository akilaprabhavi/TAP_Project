import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_aws_secret(secret_name=None, region=None):
    """
    Load a secret from AWS Secrets Manager and return it as a dictionary.
    """
    secret_name = secret_name or os.getenv("AWS_SECRET_NAME", "my_project/tap/secrets")
    region = region or os.getenv("AWS_REGION", "us-east-2")

    client = boto3.client('secretsmanager', region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString")
        if secret_string:
            try:
                return json.loads(secret_string)
            except json.JSONDecodeError:
                print("Secret found but is not valid JSON.")
                return {}
    except Exception as e:
        print(f"Failed to load secrets: {e}")
        return {}

    return {}

