from flask import Flask, request, jsonify
from flask_cors import CORS
import os
#from dotenv import load_dotenv
from openai import OpenAI
import csv
import re
import boto3
import json

# Load environment variables
#load_dotenv()

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name="us-east-1")  
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret.get("OPENAI_API_KEY")

# Retrieve API key securely
api_key = get_secret("OpenAI_API_Key")

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

# Route to save prompt data to CSV
@app.route('/save-to-csv', methods=['POST'])
def save_to_csv():
    data = request.get_json()

    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Define the CSV file path
    file_path = 'user_prompts.csv'

    # Check if the file exists, if not create it with a header
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write header if file is new
        if not file_exists:
            writer.writerow(["Prompt"])

        # Write the user's prompt as a new row in the CSV
        writer.writerow([prompt])

    return jsonify({"message": "Message saved to CSV"}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
