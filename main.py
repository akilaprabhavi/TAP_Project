from alienvault_api import AlienVaultAPI
from dynamodb_handler import DynamoDBHandler

def main():
    av_api = AlienVaultAPI()

    # Fetch all subscribed pulses with pagination
    try:
        pulses = av_api.get_all_subscribed_pulses()
        print(f"Retrieved {len(pulses)} pulses from the OTX API.")
    except Exception as e:
        print(f"Failed to fetch pulses: {e}")
        return

    # Connect to DynamoDB
    db_handler = DynamoDBHandler()

    count_updated = 0

    for pulse in pulses:
        db_handler.insert_or_update_pulse(pulse)
        count_updated += 1

    print(f"{count_updated} pulses inserted or updated successfully.")

if __name__ == "__main__":
    main()

