# Day 2: The "Agency" Phase.

In Day 1, you learned how to use AI as a Parser. Today, you’ll learn how to use AI as a Controller.

For a backend engineer, Function Calling (or "Tool Use") is the most important concept in AI. It allows the LLM to interact with your existing infrastructure—your MySQL/Mongo databases, your AWS S3 buckets, or your internal APIs.

The Concept
Instead of you writing a thousand `if/else` statements to figure out what a user wants, you give the AI a list of functions it is allowed to use. The AI then looks at the user's request and says: "To fulfill this, I need to call `get_user_details` with `user_id=101`"
---

## Refer Code Now!

## Why this is a Game-Changer
**Zero Regex:** You didn't write code to extract "AI101" from the string. The AI did it.

**Intent Routing:** If the user asks about the weather, the AI won't call get_flight_status because the "contract" (description) doesn't match.

**Security:** Your DB is never exposed to the AI. The AI only sees the output of your function.

## Analysing the code and response from the model

### First Response from model
```
{
   "id":"chatcmpl-xxx",
   "choices":[
      {
         "finish_reason":"tool_calls",
         "index":0,
         "logprobs":"None",
         "message":{
            "content":"None",
            "refusal":"None",
            "role":"assistant",
            "annotations":[
               
            ],
            "audio":"None",
            "function_call":"None",
            "tool_calls":[
               {
                  "id":"call_xxx",
                  "function":{
                     "arguments":"{}",
                     "name":"get_time"
                  },
                  "type":"function"
               },
               {
                  "id":"call_xxx",
                  "function":{
                     "arguments":"{\"flight_number\": \"AI101\"}",
                     "name":"get_flight_status"
                  },
                  "type":"function"
               }
            ]
         }
      }
   ],
   "created":1766471967,
   "model":"gpt-4o-mini-2024-07-18",
   "object":"chat.completion",
   "service_tier":"default",
   "system_fingerprint":"fp_xxx",
   "usage":{
      "completion_tokens":45,
      "prompt_tokens":89,
      "total_tokens":134,
      "completion_tokens_details":{
         "accepted_prediction_tokens":0,
         "audio_tokens":0,
         "reasoning_tokens":0,
         "rejected_prediction_tokens":0
      },
      "prompt_tokens_details":{
         "audio_tokens":0,
         "cached_tokens":0
      }
   }
}
```

### Second response from the model

```
{
   "id":"chatcmpl-xxx",
   "choices":[
      {
         "finish_reason":"stop",
         "index":0,
         "logprobs":"None",
         "message":{
            "content":"The current time is 12:28:53. Flight AI101 is on time, scheduled to depart at 10:30 PM from gate A12.",
            "refusal":"None",
            "role":"assistant",
            "annotations":[
               
            ],
            "audio":"None",
            "function_call":"None",
            "tool_calls":"None"
         }
      }
   ],
   "created":1766473134,
   "model":"gpt-4o-mini-2024-07-18",
   "object":"chat.completion",
   "service_tier":"default",
   "system_fingerprint":"fp_xxx",
   "usage":{
      "completion_tokens":32,
      "prompt_tokens":105,
      "total_tokens":137,
      "completion_tokens_details":{
         "accepted_prediction_tokens":0,
         "audio_tokens":0,
         "reasoning_tokens":0,
         "rejected_prediction_tokens":0
      },
      "prompt_tokens_details":{
         "audio_tokens":0,
         "cached_tokens":0
      }
   }
}
```
### Why is it inside a `choices` list?
This is a remnant of how LLMs work under the hood. You can actually ask the model to generate **multiple versions** of the same answer at once (by setting the `n` parameter, though people rarely do this in production because it's expensive).

```
# If you set n=3, the list would have 3 items
response = client.chat.completions.create(model="...", messages="...", n=3)

# choices[0] -> Option 1
# choices[1] -> Option 2
# choices[2] -> Option 3
```

### Handling this in a Production Backend
For the purpose of this study, we had it as `first_response` and `second_response`. For production, you should handle this with a Loop (often called an Agent Loop). Instead of just "First response" and "Second response," professional code usually looks like this:

```
while True:
    response = client.chat.completions.create(...)
    finish_reason = response.choices[0].finish_reason
    
    if finish_reason == "tool_calls":
        # 1. Execute your backend functions
        # 2. Append results to 'messages'
        # 3. Continue the loop (let the AI look at the results)
        continue 
        
    elif finish_reason == "stop":
        return response.choices[0].message.content # Return final answer
        
    else:
        raise Exception(f"Unexpected finish reason: {finish_reason}")
```
This way, if the AI needs to call get_time, then get_flight_status, and then maybe send_email based on that status, your backend handles that chain of thought automatically.


> you can think of finish_reason as the "Exit Code" of the model's processing loop.

| Reason | What it means in "Backend Speak" |
|---| ---|
| `tool_calls` |Interrupt/Callback: The model has reached a point where it needs external data. It’s handing the execution pointer back to you (the caller) to run a function. |
| `stop` | Success/EOF: The model has finished its thought and generated a complete natural language response. |
| `length` | "Timeout/Overflow: The model ran out of ""Context Window"" (tokens) before it could finish." |
| `content_filter` | "Exception: The output was omitted because it triggered a safety flag (e.g., hate speech, PII)." |

### Multi-Model Consistency (OpenAI vs. Anthropic vs. Gemini)
Do the responses change? **Yes and No.**

***The "No" (The Standard)***<br>
Most major providers (Anthropic, Google, Mistral) are moving toward the **OpenAI-Compatible API format.** Because OpenAI was first, everyone else (including **AWS Bedrock** and **Gemini**) often provides an OpenAI-style SDK or wrapper so you don't have to rewrite your logic.

***The "Yes" (The Implementation)***<br>
If you use the "Native" SDKs for each, the keys and names change:
- **Anthropic (Claude):** Instead of `tool_calls`, Claude uses `stop_reason: "tool_use"`.
- **Gemini:** Uses `finish_reason: "FUNCTION_CALL"`.
- **Meta (Llama 3 via AWS):** Usually follows the OpenAI standard of `tool_calls`.

