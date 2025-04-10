import json
import boto3
import requests
from config import PROMPT_BUCKET_NAME

# API Endpoint
CHAT_API_URL = "https://ulaq2p5pomaufimwt3pfxr3tpa0szfux.lambda-url.us-east-1.on.aws/chat"

# AWS Clients
s3_client = boto3.client("s3")

def lambda_handler(event, context):
    try:
        # List all objects in the S3 bucket
        response = s3_client.list_objects_v2(Bucket=PROMPT_BUCKET_NAME)
        if "Contents" not in response:
            return {"statusCode": 400, "body": json.dumps({"error": "No prompt files found."})}

        all_keys = [obj["Key"] for obj in response["Contents"]]
        prompt_keys = [key for key in all_keys if key.endswith(".txt") and not key.endswith("_result.txt")]

        results = {}

        for prompt_key in prompt_keys:
            try:
                # Read prompt content
                prompt_obj = s3_client.get_object(Bucket=PROMPT_BUCKET_NAME, Key=prompt_key)
                prompt_data = prompt_obj["Body"].read().decode("utf-8").strip()

                if not prompt_data:
                    results[prompt_key] = "Skipped (empty prompt)"
                    continue

                # Send prompt to API
                api_response = requests.post(CHAT_API_URL, json={"prompt": prompt_data}, timeout=30)

                if api_response.status_code == 200:
                    result_text = api_response.json().get("response", "No response received")
                else:
                    result_text = f"Error: {api_response.status_code} - {api_response.text}"

                # Define the result file key
                result_key = prompt_key.replace(".txt", "_result.txt")

                # Overwrite or create the result file in S3
                s3_client.put_object(
                    Bucket=PROMPT_BUCKET_NAME,
                    Key=result_key,
                    Body=result_text.encode("utf-8")
                )

                results[prompt_key] = "Processed and result overwritten"

            except Exception as e:
                results[prompt_key] = f"Error: {str(e)}"

        return {"statusCode": 200, "body": json.dumps(results)}

    except Exception as e:
        print(f"Lambda execution error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

if __name__ == "__main__":
    print(lambda_handler({}, {}))
