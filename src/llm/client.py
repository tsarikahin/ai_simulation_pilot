"""LLM client using the OpenAI Responses API."""

import json
from litellm import completion
from .prompts import EXPLAIN_SYSTEM_PROMPT, EXPLAIN_USER_PROMPT
from ..config.settings import Settings

class LLMClient:
    def __init__(self, settings: Settings, llm_choice: str = "groq"):
        self.settings = settings
        self.llm_choice = llm_choice
        
        # Map choices to settings
        if llm_choice == "openai":
            self.model = settings.llm_settings.openai_model
            self.api_key = settings.llm_settings.openai_api_key
        elif llm_choice == "groq":
            self.model = settings.llm_settings.groq_model
            self.api_key = settings.llm_settings.groq_api_key

    def explain(self, simulation_json: dict) -> str:
        """Return an LLM-generated explanation for the given simulation JSON using LiteLLM."""
        user_message = EXPLAIN_USER_PROMPT.format(
            simulation_json=json.dumps(simulation_json, indent=2)
        )
        messages = [
            {"role": "system", "content": EXPLAIN_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        response = completion(
            model=self.model,
            messages=messages,
            api_key=self.api_key
        )
        return response["choices"][0]["message"]["content"]

