from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
import csv
import re
import boto3
import json
import awsgi2
import io
from config import CSV_FILE_NAME, PROMPT_BUCKET_NAME

# Load environment variables
#load_dotenv()

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name="us-east-1")  
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret.get("OPENAI_API_KEY")

# Retrieve API key securely
api_key = get_secret("OPENAI_API_KEY")

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

# Initialize client
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize flask app
app = Flask(__name__)
CORS(app)  # cors- enable FE to make API calls to flask server

def refine_prompt(user_input):

    user_input_lower = user_input.lower()

    # Intent classification using keyword matching
    if re.search(r"\b(explain|describe|define)\b", user_input_lower):
        return f"Explain in simple terms:\n{user_input}"
    elif re.search(r"\b(compare|contrast|difference)\b", user_input_lower):
        return f"Provide a comparison in table form:\n{user_input}"
    elif re.search(r"\b(how|steps|procedure)\b", user_input_lower):
        return f"Step-by-step guide:\n{user_input}"
    elif re.search(r"\b(list|options)\b", user_input_lower):
        return f"Create a numbered list:\n{user_input}"
    elif re.search(r"\b(explore|analyze|consequences)\b", user_input_lower):
        return f"Analyze the flow and impact:\n{user_input}"
    elif "beginner" in user_input_lower:
        return "Explain concepts in the simplest way possible.\n\n"
    elif "expert" in user_input_lower or "detailed analysis" in user_input_lower:
        return "Provide deep technical insights.\n\n"
    else:
        return f"Reply me\nUser: {user_input}\nAssistant:"

# Cybersecurity keyword categories
keyword_categories = {
    "attack vectors": ["phishing", "malware", "ransomware", "DoS", "supply chain", "zero-day", "SQL injection"],
    "ttp": ["tactics", "techniques", "procedures", "MITRE ATT&CK", "credential dumping", "spear phishing"],
    "ioc": ["indicators of compromise",  "file hashes", "malicious IP", "IoCs", "registry changes", "outbound traffic"],
    "cve": ["common vulnerabilities", "CVE", "patch", "exploit", "vulnerability management"],
    "attack timeline": ["reconnaissance","attack", "initial compromise", "lateral movement", "data exfiltration", "persistence"],
    "incident reports": ["case study", "breach analysis", "threat actor", "malware campaign", "incident response"],
    "threat intelligence": ["threat feeds", "AlienVault", "Recorded Future", "real-time threats", "cyber intelligence"],
    "vulnerabilities": ["advanced persistent threats", "APTs", "insider threats", "zero-day vulnerabilities"]
} 

# Function to set dynamic persona based on query
def dynamic_persona(user_input):

    persona_base = "You are a cybersecurity expert, skilled in {category}, providing insights on {specifics}."

    for category, keywords in keyword_categories.items():
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", user_input, re.IGNORECASE):  # Match whole words
                specifics = ", ".join(keywords[:3])  # Pick first 3 keywords for details
                return persona_base.format(category=category, specifics=specifics)

    return "You are a Cyber Threat Analyst, providing expert insights on cybersecurity threats, vulnerabilities, and defenses."

#Uses GPT-4o-mini to correct spelling mistakes while preserving technical terms.
def correct_spelling_with_ai(user_input):
    
    messages = [
        {"role": "system", "content": "You are a spelling correction assistant. Identify and correct misspelled words while preserving technical and cybersecurity-related terms."},
        {"role": "user", "content": f"Correct any spelling mistakes and only send me the corrected text: {user_input}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2 
    )
    
    return response.choices[0].message.content.strip()


# Route to get user prompts
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("prompt")

    if not user_input:
        return jsonify({"error": "No prompt provided"}), 400
    
    corrected_input = correct_spelling_with_ai(user_input)

    messages = [
        {"role": "system", "content":  dynamic_persona(corrected_input)},
        {"role": "user", "content": refine_prompt(corrected_input)}
    ]
    
    # Print the generated prompt to debug
    print("\n=== Final Prompt Sent to API ===")
    print(messages)
    print("================================\n")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )

        assistant_reply = response.choices[0].message.content
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Create an S3 client using the IAM role associated with your AWS resource
s3_client = boto3.client('s3')


# Route to save user
@app.route("/save-to-s3", methods=["POST"])
def save_to_s3():
    # Get the prompt from the request
    prompt = request.json.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:

        try:
            # Get the current content of user_prompts.csv from S3
            response = s3_client.get_object(Bucket=PROMPT_BUCKET_NAME, Key=CSV_FILE_NAME)
            current_content = response["Body"].read().decode("utf-8")
            csv_file = io.StringIO(current_content)
        except s3_client.exceptions.NoSuchKey:
            
            # If the file doesn't exist, create an in-memory file
            csv_file = io.StringIO()
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Prompt"])  # Add header for new CSV file
        
            # Prepare to write to the CSV file
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([prompt])  # Write the new prompt
          
            # Upload the updated content back to prompts.txt
            s3_client.put_object(
                Bucket=PROMPT_BUCKET_NAME,
                Key=CSV_FILE_NAME,
                Body=csv_file.getvalue(),
                ContentType="text/csv"
        )

        return jsonify({"message": "Prompt successfully added to S3!"}), 200
    except Exception as e:
        return jsonify({"error": f"Error saving message: {str(e)}"}), 500


def handler(event, context):
    return awsgi2.response(app, event, context)

if __name__ == "__main__":
    app.run(debug=True)