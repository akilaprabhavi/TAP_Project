from alienvault_api import AlienVaultAPI
from dynamodb_handler import DynamoDBHandler

def main():
    db_handler = DynamoDBHandler()

    print("Welcome to the Threat Intelligence Search Tool!\n")
    while True:
        keyword = input("Enter keyword to search for (or 'exit' to quit): ").strip()
        if keyword.lower() == 'exit':
            break

        results = db_handler.search_pulses(keyword)
        if not results:
            print("No matching threats found.\n")
        else:
            print(f"\nFound {len(results)} matching threat(s):\n")
            for pulse in results:
                print(f"- {pulse.get('name')} (TTPs: {pulse.get('mitre_ttps')}, CVEs: {pulse.get('cves')})")
            print("\n")


if __name__ == "__main__":
    main()

