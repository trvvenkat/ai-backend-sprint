import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime


load_dotenv()
client = OpenAI()

# A Mock Database Function (The "Tool")
def get_flight_status(flight_number):
    """Mock backend logic to fetch flight status from a DB."""
    database = {
        "AI101": {"status": "On Time", "gate": "A12", "time": "10:30 PM"},
        "6E502": {"status": "Delayed", "gate": "B3", "time": "11:45 PM"}
    }
    return json.dumps(database.get(flight_number, {"error": "Flight not found"}))

# A Mock Time Function (The "Tool")
def get_time():
    """Mock backend logic to fetch the current time."""
    return datetime.now().strftime("%H:%M:%S")

# Define the "Contract" (What the AI sees)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_flight_status",
            "description": "Get the current status and gate info for a specific flight number",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_number": {
                        "type": "string",
                        "description": "The flight number, e.g. AI101",
                    },
                },
                "required": ["flight_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# Map of available functions
available_functions = {"get_flight_status": get_flight_status, "get_time": get_time}

def run_conversation(user_prompt):
    # Step 1: Send the user prompt and the tool definitions to the AI
    messages = [{"role": "user", "content": user_prompt}]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    # print("--------------------------------")
    # print(str(response.dict()))
    # print("--------------------------------")
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: Check if the AI wants to call a function
    if tool_calls:
        
        # Add AI's request to the message history
        messages.append(response_message)

        for tool_call in tool_calls:
            # print("--------------------------------")
            # print(str(tool_call.dict()))
            # print("--------------------------------")
            function_args = {}
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute your Python function
            print(f"--- Backend: Executing {function_name}({function_args}) ---")
            function_response = function_to_call(**function_args)

            # Send the result back to the AI so it can "read" the data
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })
        
        # Get a final natural language response from the AI
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        # print("--------------------------------")
        # print(str(second_response.dict()))
        # print("--------------------------------")
        return second_response.choices[0].message.content

# Test it
print(run_conversation("what time is it? is flight AI101 on time?"))