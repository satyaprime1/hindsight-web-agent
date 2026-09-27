import os
from typing import Dict, Any
import httpx

from backend.config import settings

class GroqService:
    """Simple wrapper around Groq LLM to fetch business data from a user prompt."""

    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=15.0) if self.api_key else None

    async def get_business_profile(self, prompt: str) -> Dict[str, Any]:
        """Ask Groq to generate a structured JSON with business details.
        The prompt should ask for fields: name, category, location, phone, whatsapp,
        assets (logo_url, photos, video_url, brochure_url, pricing_tiers).
        Returns a dict parsed from the LLM response.
        """
        if not self.client:
            raise RuntimeError("Groq API key not configured")
        system_prompt = (
            "You are an expert JSON generator. Given a user description, output a JSON object "
            "with the following keys: name (string), category (string), location (string), "
            "phone (string), whatsapp (string, may be same as phone), assets (object) containing "
            "logo_url (string, optional), photos (list of objects with url, title, desc), "
            "video_url (string, optional), brochure_url (string, optional), pricing_tiers "
            "(list of objects with name, price, period, badge, features)."
            "Only output the JSON without any surrounding text."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = await self.client.post(self.base_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Extract the first assistant message content
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            # The LLM should return pure JSON; parse it safely.
            import json
            business_data = json.loads(content)
        except Exception as e:
            raise ValueError(f"Failed to parse Groq JSON response: {e}\nRaw content: {content}")
        return business_data
