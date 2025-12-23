import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_meeting_data(messy_text):
    prompt = f"""
    You are a backend data parser. Extract the following information from the text:
    - Participants (names)
    - Meeting Date (convert to YYYY-MM-DD)
    - Action Items (task description and who is assigned)

    Return the output ONLY as a valid JSON object.
    Today's date is {datetime.now().strftime("%Y-%m-%d")}
    
    Text: "{messy_text}"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini", # Use 'mini' models for speed/cost
        messages=[{"role": "system", "content": prompt}],
        response_format={ "type": "json_object" } # forces JSON output
    )

    return json.loads(response.choices[0].message.content)

# Test it
raw_input = "Hey, just finished the sync with Rahul and Sneha. We decided to move the deployment to next Friday, Dec 26. Sneha is going to fix the login bug, and I'll update the Dockerfile."

structured_data = extract_meeting_data(raw_input)
print(json.dumps(structured_data, indent=2))