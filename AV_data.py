import os
import boto3
import json
import requests
from time import sleep
from openai import OpenAI
import pinecone
from pinecone import Pinecone, ServerlessSpec
from config.config import AV_URl, PC_REGION, INDEX_N

# === AlienVault API Setup ===
class AlienVaultAPI:

    # Load secrets from AWS secret manager
    def get_secret(secret_name,key_name):
        client = boto3.client('secretsmanager', region_name="us-east-1")  
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret.get(key_name)

    alientVault_URl=AV_URl

    def __init__(self, api_key: str, base_url: str = alientVault_URl):
        self.api_key = api_key
        self.base_url = base_url

    def get_subscribed_pulses(self):
        url = f"{self.base_url}/pulses/subscribed"
        headers = {"X-OTX-API-KEY": self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            raise Exception(f"Error fetching data: {response.status_code}")

    def get_pulse_details(self, pulse_id):
        """
        Get full details for a specific pulse by ID.
        """
        url = f"{self.base_url}/pulses/{pulse_id}"
        headers = {"X-OTX-API-KEY": self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve pulse {pulse_id}: {response.status_code}")
            return None

# Load secret key openAI
def get_secret(secret_name,key_name):
    client = boto3.client('secretsmanager', region_name="us-east-1")  
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret.get(key_name)

# Retrieve API key securely
pc_api_key = get_secret("PINECONE_API_KEY","PINECONE_API_KEY")

# === Pinecone Setup ===
PINECONE_REGION = PC_REGION  
INDEX_NAME = INDEX_N
DIMENSION = 1536  # adjust based on your embedding model

# Create Pinecone client instance
pc = pinecone.Pinecone(api_key=pc_api_key)

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION)
    )

# Connect to the index
index = pc.Index(INDEX_NAME)

# Retrieve API key securely
av_api_key = get_secret("ALIENVAULT_API_KEY","ALIENVAULT_API_KEY")

# === Process and Upload Data ===
alienvault_api = AlienVaultAPI(api_key=av_api_key)
pulses = alienvault_api.get_subscribed_pulses()
print(f"Retrieved {len(pulses)} pulses.")

# Retrieve API key securely
api_key = get_secret("OPENAI_API_KEY_NEW","OPENAI_API_KEY_NEW")

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

#embedding
def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

vectors = []
for pulse in pulses:
    pulse_id = pulse.get("id")

    full_pulse = alienvault_api.get_pulse_details(pulse_id)
    if not full_pulse:
        continue

    name = full_pulse.get("name", "")
    description = full_pulse.get("description", "")
    combined_text = f"{name}\n{description}"

    try:
        embedding = get_embedding(combined_text)
    except Exception as e:
        print(f"Embedding failed for pulse {pulse_id}: {e}")
        continue

    vectors.append({
    "id": pulse_id,
    "values": embedding,
    "metadata": {
        "name": name,
        "description": description
    }
    })


# Upload to Pinecone
if vectors:
    index.upsert(vectors=vectors)
    print("Embeddings uploaded successfully.")
else:
    print("No vectors to upsert.")

