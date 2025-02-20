from openai import OpenAI
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv() 

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# chatbot function
def chat_conversation():
    messages = [
        {"role": "system", "content": "You are a Cyber Threat Analyst. Provide answer for my cyber security related questions in two paragraphs. "}
    ]
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            assistant_reply = response.choices[0].message.content
            print(f"Assistant: {assistant_reply}")
            messages.append({"role": "assistant", "content": assistant_reply})
            
        except Exception as e:
            print(f"Error: {e}")
            break

chat_conversation()

