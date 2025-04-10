from alienvault_api import AlienVaultAPI
from dynamodb_handler import DynamoDBHandler

def lambda_handler(event, context):
    print("Lambda triggered!")

    try:
        av_api = AlienVaultAPI()
        db_handler = DynamoDBHandler()

        pulses = av_api.get_all_subscribed_pulses()
        print(f"Retrieved {len(pulses)} pulses")

        for pulse in pulses:
            db_handler.insert_or_update_pulse(pulse)

        print("Pulses updated successfully")
        return {"status": "success", "count": len(pulses)}

    except Exception as e:
        print(f"Error updating threat data: {str(e)}")
        return {"status": "error", "message": str(e)}
