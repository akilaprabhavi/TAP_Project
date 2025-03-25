from alienvault_api import AlienVaultAPI
from db_handler import DatabaseHandler

def main():
    # Use a hardcoded API key (you should remove this in production!)
    api_key = "5d9eba49048f27bad61c05321a1737894fbe2ae0e20114422b0bedb5bbdb2064"

    av_api = AlienVaultAPI(api_key)
    
    # Fetch pulses from AlienVault OTX
    try:
        pulses = av_api.get_subscribed_pulses()
        print(f"Retrieved {len(pulses)} pulses from the OTX API.")
    except Exception as e:
        print(f"Failed to fetch pulses: {e}")
        return

    # Initialize the database handler and connect to the database
    db_handler = DatabaseHandler()
    conn = db_handler.connect()

    # Insert pulses into the database
    for pulse in pulses:
        db_handler.insert_pulse(pulse)

    print("Data has been successfully stored in the local database.\n")

    # Retrieve and display stored pulses
    stored_pulses = db_handler.fetch_all_pulses()
    
    if stored_pulses:
        print("Stored Pulses in Database:")
        for pulse in stored_pulses:
            print(f"ID: {pulse[0]}, Name: {pulse[1]}, Description: {pulse[2]}, Author: {pulse[3]}, "
                  f"Created: {pulse[4]}, Modified: {pulse[5]}, TLP: {pulse[6]}")
    else:
        print("No pulses found in the database.")

    conn.close()

if __name__ == "__main__":
    main()
