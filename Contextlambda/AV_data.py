import boto3
import json
import requests
from openai import OpenAI
import pinecone
from pinecone import ServerlessSpec
from config import (
    AV_URl, PC_REGION, INDEX_N,
    openAI_Secret_name, openAI_key_name,
    PC_Secret_name, PC_key_name,
    AV_Secret_name, AV_key_name
)

# === AlienVault API Setup ===
class AlienVaultAPI:
    alientVault_URl = AV_URl

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
        url = f"{self.base_url}/pulses/{pulse_id}"
        headers = {"X-OTX-API-KEY": self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve pulse {pulse_id}: {response.status_code}")
            return None


# === Secret Retrieval ===
def get_secret(secret_name, key_name):
    client = boto3.client('secretsmanager', region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])
    return secret.get(key_name)


# === Embedding function ===
def get_embedding(text: str, client: OpenAI) -> list:
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


# === Lambda Handler ===
def lambda_handler(event, context):

    # Retrieve API keys securely
    pc_api_key = get_secret(PC_Secret_name, PC_key_name)
    av_api_key = get_secret(AV_Secret_name, AV_key_name)
    openai_api_key = get_secret(openAI_Secret_name, openAI_key_name)

    # Initialize OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Setup Pinecone index
    pc = pinecone.Pinecone(api_key=pc_api_key)
    if INDEX_N not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_N,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PC_REGION)
        )
    index = pc.Index(INDEX_N)

    # AlienVault data retrieval
    alienvault_api = AlienVaultAPI(api_key=av_api_key)
    pulses = alienvault_api.get_subscribed_pulses()

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
            embedding = get_embedding(combined_text, client)
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

    if vectors:
        index.upsert(vectors=vectors)
        print("Embeddings uploaded successfully.")
    else:
        print("No vectors to upsert.")
