import os
from pydantic import BaseModel, Field
from typing import Optional
import requests
import json


class PerplexityResult(BaseModel):
    """
    Represents the result from the Perplexity API.

    Attributes:
        result: The text result from Perplexity.
        error: An error message, if any.
    """
    result: Optional[str] = Field(None, description="The text result from Perplexity.")
    error: Optional[str] = Field(None, description="Error message if retrieval failed.")


def get_tool_implementation_ideas(tool_description: str) -> dict:
    """
    Uses Perplexity's Sonar model to generate ideas for implementing a tool.

    Args:
        tool_description (str): A description of the tool's desired functionality (e.g., "crawl a website").

    Returns:
        dict: A dictionary containing either the 'result' or an 'error' message.

    Raises:
        ValueError: If the PERPLEXITY_API_KEY environment variable is not set.
    """
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    if not perplexity_api_key:
        return {"error": "PERPLEXITY_API_KEY environment variable not set."}

    api_url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {perplexity_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides guidance on how to implement software tools, given a description of the tool's desired functionality."
            },
            {
                "role": "user",
                "content": f"I want to create a tool that can {tool_description}. How can I achieve this? Please provide code snippets and explain the steps."
            }
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        json_response = response.json()
        result = json_response["choices"][0]["message"]["content"]
        return {"result": result}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error during Perplexity API request: {e}"}
    except (KeyError, IndexError) as e:
        return {"error": f"Error parsing Perplexity API response: {e}"}
