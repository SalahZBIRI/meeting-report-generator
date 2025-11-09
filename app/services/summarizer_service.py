import os
import time
import requests
from app.core.config import settings


# Load the Groq API key and base URL from configuration
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# PROMPTS for summarization
SYSTEM_PROMPT = """You are an expert meeting summarization assistant. You ALWAYS preserve speaker identities ([SPEAKER_00], [SPEAKER_01], etc.).

CRITICAL: Respond in the SAME LANGUAGE as the input transcription."""


# Prompt template for partial (chunk-level) summaries
CHUNK_PROMPT = """Here is a meeting transcription with identified speakers:

{chunk}

Participants: {participants}
Detected language: {language}

Create a structured summary PRESERVING speakers (e.g., "SPEAKER_00 proposed..."):

KEY INTERVENTIONS
- SPEAKER_XX: (what they said)

TOPICS DISCUSSED
- Topic X (discussed by whom)

DECISIONS MADE
- Decision X (proposed by whom)

ACTION ITEMS
- Action X (assigned to whom if mentioned)

IMPORTANT: Respond in {language}. Use simple, professional language without emojis, bold text or special characters."""


# Prompt template for merging multiple partial summaries into one final report
MERGE_PROMPT = """You received several partial summaries of the same meeting.

Participants: {participants}
Language: {language}

Partial summaries:
{parts}

Merge them into a final coherent professional report.

CRITICAL INSTRUCTIONS:
1. Preserve speaker mentions ([SPEAKER_00], [SPEAKER_01], etc.)
2. ELIMINATE ALL REDUNDANCIES - never repeat the same information
3. Merge similar points into one sentence
4. Be concise but comprehensive
5. Professional business tone
6. NO emojis, NO bold text (), NO special characters
7. Use clean section headers with numbers only
8. Respond in {language}"""


#Function to call the Groq model
def llama_summarize(prompt: str, max_retries: int = 3) -> str:
    """Appelle le modèle Groq avec retry automatique + gestion d’erreurs."""
    if not GROQ_API_KEY:
        return " Error: Missing GROQ API key."
    if not prompt:
        return "Error: Empty prompt."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",  # Groq model (llama) used for summarization
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1000, # Limit response length
    }
    # Try sending the request multiple times
    for attempt in range(max_retries):
        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=25)
        except requests.exceptions.Timeout:
            # Handle timeout and retry after short wait
            print(f"Request timeout (attempt {attempt+1}/{max_retries})", flush=True)
            time.sleep(3)
            continue
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}", flush=True)
            time.sleep(2)
            continue
        # Handle rate limiting (HTTP 429)
        if response.status_code == 429:
            try:
                 # Try to extract wait time from the API message
                wait_time = float(response.json()["error"]["message"].split("try again in ")[1].split("s")[0])
            except Exception:
                wait_time = 5 # Default wait time
            print(f"Rate limit reached, waiting {wait_time:.1f}s... (tentative {attempt+1}/{max_retries})", flush=True)
            time.sleep(wait_time + 1)
            continue
        # Success: valid response
        if response.status_code == 200:
            data = response.json()
            if "choices" not in data or not data["choices"]:
                return "Empty response from Groq model."
            return data["choices"][0]["message"]["content"]
        
        print(f"HTTP Error {response.status_code}, retry dans 2s...", flush=True)
        time.sleep(2)
    # All retries failed
    return "Groq error after multiple attempts."
