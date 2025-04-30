from alienvault_api import AlienVaultAPI
from dynamodb_handler import DynamoDBHandler

def lambda_handler(event, context):
    print("Auto threat sync Lambda is running...")

    try:
        av_api = AlienVaultAPI()
        db_handler = DynamoDBHandler()

        pulses = av_api.get_all_subscribed_pulses()
        print(f"Retrieved {len(pulses)} pulses")

        for pulse in pulses:
            db_handler.insert_or_update_pulse(pulse)

        print("DynamoDB updated successfully.")
        return {"status": "success", "updated_count": len(pulses)}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
