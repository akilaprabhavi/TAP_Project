from openai import OpenAI
from dynamodb_handler import DynamoDBHandler
from secret_manager import get_aws_secret
import time

class GPTThreatAnalyser:
    def __init__(self):
        secrets = get_aws_secret()
        openai_api_key = secrets.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)
        self.db_handler = DynamoDBHandler()

    def generate_threat_analysis(self, threat_description):
        prompt = f"""
        Analyze the following cyber threat and classify it into:
        - Attack Vector (e.g., Phishing, Malware, Ransomware, SQL Injection)
        - MITRE ATT&CK TTPs
        - Common Vulnerabilities and Exposures (CVEs)

        Threat Description:
        {threat_description}

        Respond in JSON format with the following keys:
        {{
            "attack_vector": "...",
            "mitre_ttps": ["...", "..."],
            "cves": ["...", "..."]
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cyber threat intelligence analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            result_text = response.choices[0].message.content.strip()
            return eval(result_text)  # Replace with json.loads() if needed
        except Exception as e:
            print(f"Error in GPT API call:\n{e}")
            return None

    def process_threats(self):
        stored_pulses = self.db_handler.fetch_all_pulses()

        for pulse in stored_pulses:
            pulse_id = pulse.get("id")
            name = pulse.get("name")
            description = pulse.get("description")

            print(f"\nAnalyzing threat: {name}...")

            analysis = self.generate_threat_analysis(description)
            if analysis:
                self.db_handler.update_pulse_with_analysis(
                    pulse_id,
                    analysis.get("attack_vector"),
                    ", ".join(analysis.get("mitre_ttps", [])),
                    ", ".join(analysis.get("cves", []))
                )
                print("Updated with AI-generated threat tags.")

            time.sleep(1)

        print("\nAll threats analyzed and stored.")

if __name__ == "__main__":
    analyser = GPTThreatAnalyser()
    analyser.process_threats()
