import os
import requests
import json
from pydantic import BaseModel, Field
from typing import Optional


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
        query (str): The search query string describing the implementation goal.

    Returns:
        PerplexitySearchResult: A PerplexitySearchResult object containing the raw JSON response from the API as a string, or an error message if the API call fails.

    Raises:
        ValueError: If the PERPLEXITY_API_KEY environment variable is not set.
        Exception: If the Perplexity API request fails.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return PerplexitySearchResult(result="", error="PERPLEXITY_API_KEY environment variable not set.")

    url = "https://api.perplexity.ai/v1/answer"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = {
        "model": "sonar",
        "messages": [{"role": "user", "content": query}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return PerplexitySearchResult(result=json.dumps(response.json()))
    except requests.exceptions.RequestException as e:
        request_data_str = json.dumps(data) if 'data' in locals() else 'Data not constructed'
        response_text = response.text if 'response' in locals() and hasattr(response, 'text') else 'No response'
        error_message = f"Perplexity API request failed: {str(e)}, Request: {request_data_str}, Response: {response_text}"
        return PerplexitySearchResult(result="", error=error_message)
    except Exception as e:
        return PerplexitySearchResult(result="", error=f"An unexpected error occurred: {e}")
