from openai import OpenAI
from dotenv import load_dotenv
from assignment_chat.prompts import return_prompt_instructions
import json
import requests
from utils.logger import get_logger
import os
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import requests


_logs = get_logger(__name__)

load_dotenv(".env")
load_dotenv(".secrets")

client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

open_ai_model = os.getenv("OPENAI_MODEL", "gpt-4")

"""Service 1: Give the client a random quote about health to start their session."""

def get_random_quote() -> str:
    url = "https://thequoteshub.com/api"
    params = {"tags": "inspirational"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json() 

        content = data.get("text", "")
        author = data.get("author", "")
        if content:
            return f"“{content}” — {author}".strip()

        return "Take care of your mind and body — small steps still count."

    except Exception as e:
        _logs.error(f"Quote API error: {e}")
        return "Take care of your mind and body — small steps still count."

"""Service 2: Inital preliminary intake form to assess clients mental health similarity score with a structured output. 9 questions will be asked to client based on depression dataset ."""

def get_prelim_assessment(name: str) -> dict:
    return {
        "greeting": f"Hi {name} — welcome. Before we start, I’ll ask a quick 9-question check-in.",
        "instructions": "Answer as best you can. This is not a medical diagnosis; it’s a brief screening to guide our conversation.",
        "assessment": [
            "1) What is your gender identity (optional)?",
            "2) What is your occupation or main daily activity? Describe.",
            "3) Do you have any family history of mental health challenges? Describe.",
            "4) In the past month, about how many days have you spent mostly indoors? Describe.",
            "5) Have you previously been diagnosed with a mental health condition? Describe.",
            "6) Do you experience mood swings? Describe.",
            "7) How interested do you feel in your work/school lately? Describe.",
            "8) Do you feel social situations are difficult for you? Describe.",
            "9) Do you have any questions for me regarding depression and mental health?"
        ]
    }

"""Service 2: Get response from client for the intake form and use cosine similarity semantic search to query the Depression dataset for a mental health similarity score."""

def search_dataset(user_text: str) -> dict:

    dep_dataset = pd.read_csv("assignment_chat/depression_dataset.csv")

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(dep_dataset["content"].astype(str))

    q_vec = vectorizer.transform([user_text])
    sims = cosine_similarity(q_vec, X).flatten()
    top_i = int(np.argmax(sims))

    return {
        "top_index": top_i,
        "score": float(sims[top_i]),
        "matched_text": str(dep_dataset.iloc[top_i]["content"])
    }

def sanitize_history(history: list[dict]) -> list[dict]:
    clean_history = []
    for msg in history:
        clean_history.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
    return clean_history

"""Service 3: Function calling"""

tools = [
    {
        "type": "function",
        "name": "get_random_quote",
        "description": "Get a random health-related inspirational quote to start the therapy session.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "get_prelim_assessment",
        "description": "Ask user for their name and generate an initial 9-question preliminary intake assessment.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Client full name."},
            },
            "required": ["name"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "search_dataset",
        "description": "Search depression dataset using cosine similarity and return best match and similairty score.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "user_text": {"type": "string", "description": "Client's response to the 9 assessment questions"}
            },
            "required": ["user_text"],
            "additionalProperties": False
        }
    }
]

def therapy_chat(message: str, history: Optional[list[dict]] = None) -> str:
    if history is None:
        history = []

    _logs.info(f"User message: {message}")

    instructions = return_prompt_instructions() 

    user_msg = {"role": "user", "content": message}
    conversation_input = sanitize_history(history) + [user_msg]

    while True:
        response = client.responses.create(
            model=open_ai_model,
            instructions=instructions,
            input=conversation_input,
            tools=tools
        )

        # add the model output items to the conversation
        conversation_input += response.output

        tool_calls = [item for item in response.output if getattr(item, "type", None) == "function_call"]
        if not tool_calls:
            return response.output_text

        # execute each tool call and append outputs
        for call in tool_calls:
            name = call.name
            args = json.loads(call.arguments or "{}")
            _logs.info(f"Tool call: {name} args={args}")

            if name == "get_random_quote":
                result = get_random_quote()
                tool_payload = {"quote": result}

            elif name == "get_prelim_assessment":
                result = get_prelim_assessment(**args)  
                tool_payload = result

            elif name == "search_dataset":
                result = search_dataset(**args)
                tool_payload = result

            else:
                tool_payload = {"error": f"Unknown tool: {name}"}

            conversation_input.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(tool_payload)
            })