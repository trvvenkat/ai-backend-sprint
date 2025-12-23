# Day 1
We’re going to skip the "Chatbot UI" and go straight to building an AI-Powered Logic Layer.

Your goal for Day 1 is to use an LLM to transform unstructured, messy user input into structured JSON that a database could actually use. This is the most common "Day 1" task for AI in the industry.

## The Goal
Create a script that takes a messy user "Voice Note" (text) about a meeting and extracts:
- Participants (as a list)
- Date/Time (as an ISO string)
- Action Items (as an array of objects)

### 1. The Architecture
In a traditional backend, you’d need complex Regex or Natural Language Processing (NLP) libraries like SpaCy to do this. With an LLM, it’s a single API call.

### 2. Prerequisites
Python installed.

An API Key (OpenAI is easiest to start with, but you can use Anthropic or even Groq/Together AI for free tiers).

Install the libraries from `requirements.txt`