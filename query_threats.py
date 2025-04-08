from dynamodb_handler import DynamoDBHandler

def display_pulses(pulses):
    """
    Helper function to print pulse details in a user-friendly format.
    """
    if not pulses:
        print("No relevant cyber threats found.")
        return

    for pulse in pulses:
        print(f"\n Threat: {pulse[1]}\n Description: {pulse[2]}\n Author: {pulse[3]}\n"
              f" Created: {pulse[4]}\n TLP Level: {pulse[6]}")
    print("\n")

def main():
    db_handler = DynamoDBHandler()
    db_handler.connect()

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

    db_handler.conn.close()

if __name__ == "__main__":
    main()
