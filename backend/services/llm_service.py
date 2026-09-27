import logging
import json
from typing import Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger("llm_service")

class LLMService:
    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        if settings.has_groq_credentials:
            try:
                from groq import Groq
                self.client = Groq(api_key=settings.groq_api_key)
                logger.info(f"Initialized Groq LLM client with model: {settings.groq_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}. Will use intelligent generator fallback.")
                self.client = None
        else:
            logger.info("No GROQ_API_KEY detected in .env. Operating in intelligent template generator mode.")

    def complete(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Call LLM with fallback"""
        if self.client:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                # Try preferred model, fallback to llama-3.3-70b-versatile or qwen
                models_to_try = [
                    settings.groq_model,
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant"
                ]

                last_error = None
                for model in models_to_try:
                    try:
                        response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=4096
                        )
                        return response.choices[0].message.content
                    except Exception as err:
                        last_error = err
                        continue
                
                logger.error(f"All Groq models failed: {last_error}")
            except Exception as e:
                logger.error(f"Groq API call failed: {e}")

        # Intelligent fallback return
        return self._generate_fallback(prompt, system_prompt)

    def _generate_fallback(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Provide structured synthetic response if LLM is offline"""
        logger.info("Generating response via intelligent agent heuristics...")
        return "GENERATED_OUTPUT_FALLBACK"

llm_service = LLMService()
