import os
import requests
import json
from pydantic import BaseModel, Field
from typing import Optional, Annotated


class PerplexitySearchResult(BaseModel):
    """
    Represents the raw search result from Perplexity API.

    Attributes:
        result: The JSON string representing the raw API response.
        error: Optional error message if the API call fails.
    """
    result: str = Field(..., description="Raw JSON string of the Perplexity API response.")
    error: Optional[str] = Field(None, description="Error message, if any.")


def search_perplexity(query: str) -> PerplexitySearchResult:
    """
    Searches Perplexity AI to find the current state-of-the-art way to implement things.
    Use this tool when you need to know the best, most up-to-date practices for a particular task,
    as your own knowledge might be outdated. Searching Perplexity is the recommended way to stay informed.

    Args:
        query (str): The search query string describing what you want to implement, for example 'I want to summarize a text using gpt-4o'.

    Returns:
        PerplexitySearchResult: A PerplexitySearchResult object containing the raw JSON response from the API as a string, or an error message if the API call fails.

    Raises:
        ValueError: If the PERPLEXITY_API_KEY environment variable is not set.
        Exception: If the Perplexity API request fails.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return PerplexitySearchResult(result="", error="PERPLEXITY_API_KEY environment variable not set.")

    # Use the chat completions endpoint
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Construct payload based on reference, using a generic system prompt
    payload = {
        "model": "sonar",  # Or choose another appropriate model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant providing information based on the user query. Do not include information about fonts or typography in your response."},
            {"role": "user", "content": query}
        ],
        "temperature": 0.3, # Optional: Adjust temperature for creativity vs. factuality
        "max_tokens": 1024 # Optional: Adjust token limit as needed
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        # Return the raw JSON response as a string
        return PerplexitySearchResult(result=json.dumps(response.json()))

    except requests.exceptions.RequestException as e:
        request_data_str = json.dumps(payload) if 'payload' in locals() else 'Payload not constructed'
        response_text = response.text if 'response' in locals() and hasattr(response, 'text') else 'No response'
        error_message = f"Perplexity API request failed: {str(e)}, Request: {request_data_str}, Response: {response_text}"
        return PerplexitySearchResult(result="", error=error_message)
    except Exception as e:
        # Catch potential JSON decoding errors or other issues
        return PerplexitySearchResult(result="", error=f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    print(search_perplexity("How to implement a tool in a web app?"))