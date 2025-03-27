import json
import csv
import boto3
import requests
import os
from config import CSV_FILE_NAME, PROMPT_BUCKET_NAME

# API Endpoint (Replace with actual deployed URL)
CHAT_API_URL = "https://27eimt2ok2inv62obguq22krsa0ruaiv.lambda-url.us-east-1.on.aws/chat"

# AWS Clients
s3_client = boto3.client("s3")

def read_prompts_from_s3():
    try:
        # Download CSV from S3 to /tmp/ (Lambda's temporary storage)
        local_path = f"/tmp/{CSV_FILE_NAME}"
        s3_client.download_file(PROMPT_BUCKET_NAME, CSV_FILE_NAME, local_path)

        prompts = []
        with open(local_path, mode="r", encoding="utf-8") as file:
            for line in file:
                prompt = line.strip()
                if prompt:
                    prompts.append(prompt)         
        
        return prompts
    except Exception as e:
        print(f"Error reading text file from S3: {str(e)}")
        return []

def lambda_handler(event, context):
    # Read prompts from S3
    prompts = read_prompts_from_s3()
    
    if not prompts:
        return {"statusCode": 400, "body": json.dumps({"error": "No prompts found in S3."})}

    results = {}
    for prompt in prompts:
        try:
            # Send request to external API
            response = requests.post(CHAT_API_URL, json={"prompt": prompt}, timeout=30)
            if response.status_code == 200:
                results[prompt] = response.json().get("response", "No response received")
            else:
                results[prompt] = f"Error: {response.status_code} - {response.text}"
        
        except Exception as e:
            results[prompt] = f"Error: {str(e)}"

        print(json.dumps({prompt: results[prompt]}, indent=2))

    return {"statusCode": 200, "body": json.dumps(results)}

if __name__ == "__main__":
    lambda_handler({}, {})
