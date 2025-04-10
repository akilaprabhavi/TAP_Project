import boto3
from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv
import os

class DynamoDBHandler:
    """
    A class to handle DynamoDB operations for threat pulses.
    """

    def __init__(self, table_name=None):
        load_dotenv()

        # Get table name from env or default to CDK-created table
        self.table_name = table_name or os.getenv("DYNAMODB_TABLE_NAME", "ThreatPulses")
        self.region = os.getenv("AWS_REGION", "us-east-1")

        # Create DynamoDB resource using default AWS credential chain (IAM role, CLI config, etc.)
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.table = self.dynamodb.Table(self.table_name)

    def insert_or_update_pulse(self, pulse: dict):
        """
        Insert a new pulse or update existing one based on its ID and modified time.
        """
        pulse_id = pulse.get("id")
        if not pulse_id:
            return

        # Check for existing item to avoid unnecessary overwrite
        existing = self.table.get_item(Key={"id": pulse_id})
        existing_item = existing.get("Item")

        if existing_item and existing_item.get("modified") == pulse.get("modified"):
            return  # No update needed

        self.table.put_item(Item={
            "id": pulse_id,
            "name": pulse.get("name", ""),
            "description": pulse.get("description", ""),
            "author_name": pulse.get("author", {}).get("name", ""),
            "created": pulse.get("created", ""),
            "modified": pulse.get("modified", ""),
            "tlp": pulse.get("tlp", "white"),
            "attack_vector": pulse.get("attack_vector", ""),
            "mitre_ttps": pulse.get("mitre_ttps", ""),
            "cves": pulse.get("cves", "")
        })

    def update_pulse_with_analysis(self, pulse_id, attack_vector, mitre_ttps, cves):
        """
        Update a pulse record with AI-generated threat tags.
        """
        self.table.update_item(
            Key={"id": pulse_id},
            UpdateExpression="SET attack_vector = :av, mitre_ttps = :ttps, cves = :cves",
            ExpressionAttributeValues={
                ":av": attack_vector,
                ":ttps": mitre_ttps,
                ":cves": cves
            }
        )

    def fetch_all_pulses(self):
        """
        Fetch all pulse records from DynamoDB.
        """
        response = self.table.scan()
        return response.get("Items", [])

    def fetch_recent_pulses(self, limit=5):
        """
        Fetch the most recent pulses, sorted by created timestamp.
        """
        all_pulses = self.fetch_all_pulses()
        sorted_pulses = sorted(all_pulses, key=lambda x: x.get("created", ""), reverse=True)
        return sorted_pulses[:limit]

    def search_pulses(self, keyword):
        """
        Search for pulses that contain a keyword in the name or description.
        """
        response = self.table.scan(
            FilterExpression=Attr("name").contains(keyword) | Attr("description").contains(keyword)
        )
        return response.get("Items", [])

