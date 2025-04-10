from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import re
import boto3
import json
import awsgi2
from time import sleep
import datetime
from config import PROMPT_BUCKET_NAME, PC_REGION, INDEX_N, openAI_Secret_name, openAI_key_name,PC_Secret_name,PC_key_name
import uuid
from pinecone import Pinecone

# Load secret key
def get_secret(secret_name, key_name):
    client = boto3.client('secretsmanager', region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret.get(key_name)

# load configs
PINECONE_REGION = PC_REGION
INDEX_NAME = INDEX_N
DIMENSION = 1536

# Retrieve API key securely
api_key = get_secret(openAI_Secret_name, openAI_key_name)
pc_api_key = get_secret(PC_Secret_name, PC_key_name)

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

# Initialize flask app
app = Flask(__name__)
CORS(app)

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('AttackVectors')

# === Pinecone Setup ===

# Initialize pinecone client
pc = Pinecone(api_key=pc_api_key)
index = pc.Index(INDEX_NAME)

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return response.data[0].embedding

def retrieve_context_from_pinecone(user_query, top_k=5):
    embedding = get_embedding(user_query)
    result = index.query(vector=embedding, top_k=top_k, include_metadata=True)

    context_chunks = [match['metadata']['description'] for match in result['matches'] if 'description' in match['metadata']]
    return "\n---\n".join(context_chunks)

def refine_prompt(user_input):
    user_input_lower = user_input.lower()

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
    "ioc": ["indicators of compromise", "file hashes", "malicious IP", "IoCs", "registry changes", "outbound traffic"],
    "cve": ["common vulnerabilities", "CVE", "patch", "exploit", "vulnerability management"],
    "attack timeline": ["reconnaissance", "attack", "initial compromise", "lateral movement", "data exfiltration", "persistence"],
    "incident reports": ["case study", "breach analysis", "threat actor", "malware campaign", "incident response"],
    "threat intelligence": ["threat feeds", "AlienVault", "Recorded Future", "real-time threats", "cyber intelligence"],
    "vulnerabilities": ["advanced persistent threats", "APTs", "insider threats", "zero-day vulnerabilities"]
}

# Function to set dynamic persona based on query
def dynamic_persona(user_input):
    persona_base = "You are a cybersecurity expert, skilled in {category}, providing insights on {specifics}."

    for category, keywords in keyword_categories.items():
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", user_input, re.IGNORECASE):
                specifics = ", ".join(keywords[:3])
                return persona_base.format(category=category, specifics=specifics)

    return "You are a Cyber Threat Analyst, providing expert insights on cybersecurity threats, vulnerabilities, and defenses."

# Uses GPT-4o-mini to correct spelling mistakes while preserving technical terms
def correct_spelling_with_ai(user_input):
    messages = [
        {
            "role": "system",
            "content": "You are a spelling correction assistant. Identify and correct misspelled words while preserving technical and cybersecurity-related terms."
        },
        {
            "role": "user",
            "content": f"Correct any spelling mistakes and only send me the corrected text: {user_input}"
        }
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
    sleep(3)

    pinecone_context = retrieve_context_from_pinecone(corrected_input)

    messages = [
        {"role": "system", "content": dynamic_persona(corrected_input)},
        {
            "role": "system",
            "content": f"""Here is relevant context: Use this to answer the question.
                            Provide the content highlighting the attack vectors, TTP's, IoCs, CVEs, attack timelines, any incident reports, and the feed data.
                            Try to include time values as well.\n{pinecone_context}"""
        },
        {"role": "user", "content": refine_prompt(corrected_input)}
    ]

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

# Create an S3 client
s3_client = boto3.client('s3')

@app.route("/save-to-s3", methods=["POST"])
def save_to_s3():
    prompt = request.json.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        file_name = f"prompt_{timestamp}_{uuid.uuid4().hex[:8]}.txt"

        s3_client.put_object(
            Bucket=PROMPT_BUCKET_NAME,
            Key=file_name,
            Body=prompt.encode("utf-8"),
            ContentType="text/plain"
        )

        return jsonify({"message": "Prompt successfully saved!", "file_name": file_name}), 200

    except Exception as e:
        return jsonify({"error": f"Error saving message: {str(e)}"}), 500

@app.route('/update', methods=['GET'])
def update_attack_vector():
    attackvector = request.args.get('attackVector')

    if not attackvector:
        return jsonify({'error': 'Missing attackvector parameter'}), 400

    response = table.get_item(Key={'attackVector': attackvector})

    if 'Item' in response:
        return jsonify(response['Item'])
    else:
        return jsonify({'error': 'Attack Vector not found'}), 404

@app.route("/get-prompts-results", methods=["GET"])
def get_prompts_and_results():
    try:
        response = s3_client.list_objects_v2(Bucket=PROMPT_BUCKET_NAME)
        if "Contents" not in response:
            return []

        data = []
        for obj in response["Contents"]:
            key = obj["Key"]
            last_updated_time = obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S")

            if key.endswith(".txt") and not key.endswith("_result.txt"):
                result_key = key.replace(".txt", "_result.txt")
                prompt_obj = s3_client.get_object(Bucket=PROMPT_BUCKET_NAME, Key=key)
                prompt_text = prompt_obj["Body"].read().decode("utf-8").strip()

                sleep(3)
                result_text = "Processing..."

                try:
                    result_obj = s3_client.get_object(Bucket=PROMPT_BUCKET_NAME, Key=result_key)
                    result_text = result_obj["Body"].read().decode("utf-8").strip()
                    last_updated_time = result_obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
                except s3_client.exceptions.NoSuchKey:
                    pass

                data.append({
                    "prompt": prompt_text,
                    "result": result_text,
                    "last_updated": last_updated_time
                })

        return data
    except Exception as e:
        print(f"Error fetching prompts and results: {str(e)}")
        return []

def handler(event, context):
    return awsgi2.response(app, event, context)

if __name__ == "__main__":
    app.run(debug=True)
