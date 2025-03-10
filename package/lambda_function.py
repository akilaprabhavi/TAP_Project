#from openai import OpenAI
import json
#from flask import Flask, request, jsonify
#from flask_cors import CORS
import csv
import requests

CHAT_API_URL = "http://127.0.0.1:5000/chat"

def read_prompts_from_csv():
    try:
        FILE_PATH = "user_prompts.csv"

        # Read the CSV file and extract prompts
        prompts = []
        with open(FILE_PATH, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row (if any)
            for row in csv_reader:
                if row:
                    prompts.append(row[0])          
        
        return prompts
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return []

def lambda_handler(event, context):
    # Read prompts from the CSV file
    prompts = read_prompts_from_csv()
    
    if not prompts:
        return {"statusCode": 400, "body": json.dumps({"error": "No prompts found in CSV."})}

    results = {}
    for prompt in prompts:
        try:
            # Send request to Flask API
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