from dynamodb_handler import DynamoDBHandler

def display_pulses(pulses):
    """
    Helper function to print pulse details in a user-friendly format.
    """
    if not pulses:
        print("No relevant cyber threats found.")
        return

    for pulse in pulses:
        print(f"""
    Threat: {pulse.get('name')}
    Description: {pulse.get('description')}
    Author: {pulse.get('author_name')}
    Created: {pulse.get('created')}
    Modified: {pulse.get('modified')}
    TLP: {pulse.get('tlp')}
    Attack Vector: {pulse.get('attack_vector')}
    MITRE TTPs: {pulse.get('mitre_ttps')}
    CVEs: {pulse.get('cves')}
        """)
    print("\n")

def main():
    db_handler = DynamoDBHandler()

    while True:
        user_query = input("\nAsk about cyber threats (or type 'exit' to quit): ").strip().lower()

        if user_query == "exit":
            print("Goodbye!")
            break
        elif "recent" in user_query or "latest" in user_query:
            print("\nFetching the most recent cyber threats...\n")
            pulses = db_handler.fetch_recent_pulses()
        else:
            print(f"\nSearching for threats related to '{user_query}'...\n")
            pulses = db_handler.search_pulses(user_query)

        display_pulses(pulses)

if __name__ == "__main__":
    main()

