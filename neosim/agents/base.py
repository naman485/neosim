"""
Base Agent Class

All simulation agents inherit from this base.
Each agent is an LLM API call with a structured persona prompt.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import os
import httpx
import asyncio
from enum import Enum


class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    GROQ = "groq"
    TOGETHER = "together"
    OLLAMA = "ollama"

    @classmethod
    def from_string(cls, value: str) -> "LLMProvider":
        """Convert string to LLMProvider enum."""
        value = value.lower()
        for provider in cls:
            if provider.value == value:
                return provider
        raise ValueError(f"Unknown LLM provider: {value}. Supported: {[p.value for p in cls]}")


@dataclass
class AgentMemory:
    """
    Agent memory for maintaining context across cycles.

    Each agent remembers the last N interactions to inform decisions.
    """
    max_items: int = 5
    items: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, item: Dict[str, Any]) -> None:
        """Add item to memory, evicting oldest if at capacity."""
        self.items.append(item)
        if len(self.items) > self.max_items:
            self.items.pop(0)

    def get_context(self) -> str:
        """Get memory as context string for prompts."""
        if not self.items:
            return "No prior interactions."

        context_parts = []
        for i, item in enumerate(self.items, 1):
            context_parts.append(f"[Interaction {i}]: {json.dumps(item)}")
        return "\n".join(context_parts)

    def clear(self) -> None:
        """Clear all memory."""
        self.items = []


@dataclass
class AgentResponse:
    """Structured response from an agent."""
    decision: str  # Primary decision/action
    reasoning: str  # Why this decision
    confidence: float  # 0-1 confidence in decision
    metrics: Dict[str, Any] = field(default_factory=dict)  # Quantitative outputs
    signals: List[str] = field(default_factory=list)  # Qualitative signals
    raw_response: str = ""  # Full LLM response for debugging


class BaseAgent(ABC):
    """
    Base class for all simulation agents.

    Each agent type (Buyer, Competitor, Channel, Advisor) implements:
    - A persona prompt defining their perspective
    - A decision method that calls the LLM
    - Metric extraction from LLM responses
    """

    def __init__(
        self,
        agent_id: str,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        model: str = None,
        temperature: float = 0.7,
    ):
        self.agent_id = agent_id
        self.provider = provider
        self.model = model or self._default_model()
        self.temperature = temperature
        self.memory = AgentMemory()

        # API configuration
        self._api_key = self._get_api_key()
        self._client = httpx.Client(timeout=30.0)
        self._async_client = None  # Lazy init for async

    # Default models per provider
    DEFAULT_MODELS = {
        LLMProvider.ANTHROPIC: "claude-sonnet-4-20250514",
        LLMProvider.OPENAI: "gpt-4o",
        LLMProvider.GOOGLE: "gemini-1.5-pro",
        LLMProvider.GROQ: "llama-3.3-70b-versatile",
        LLMProvider.TOGETHER: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        LLMProvider.OLLAMA: "llama3.2",
    }

    # Environment variable names for API keys
    API_KEY_ENV_VARS = {
        LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
        LLMProvider.OPENAI: "OPENAI_API_KEY",
        LLMProvider.GOOGLE: "GOOGLE_API_KEY",
        LLMProvider.GROQ: "GROQ_API_KEY",
        LLMProvider.TOGETHER: "TOGETHER_API_KEY",
        LLMProvider.OLLAMA: None,  # Ollama runs locally, no API key needed
    }

    def _default_model(self) -> str:
        """Get default model for provider."""
        return self.DEFAULT_MODELS.get(self.provider, "gpt-4o")

    def _get_api_key(self) -> str:
        """Get API key from environment."""
        env_var = self.API_KEY_ENV_VARS.get(self.provider)
        if env_var is None:
            return ""  # Ollama doesn't need API key
        return os.environ.get(env_var, "")

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type identifier."""
        pass

    @abstractmethod
    def get_persona_prompt(self) -> str:
        """
        Return the persona prompt that defines this agent's perspective.

        This is the core of each agent type - it shapes how the LLM
        thinks about the simulation from this agent's viewpoint.
        """
        pass

    @abstractmethod
    def get_decision_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build the decision prompt for a specific simulation context.

        Args:
            context: Current simulation state (product, pricing, cycle, etc.)

        Returns:
            Prompt asking the agent to make a decision
        """
        pass

    @abstractmethod
    def parse_response(self, response: str) -> AgentResponse:
        """
        Parse LLM response into structured AgentResponse.

        Args:
            response: Raw LLM response text

        Returns:
            Structured AgentResponse with decision, metrics, etc.
        """
        pass

    def decide(self, context: Dict[str, Any]) -> AgentResponse:
        """
        Make a decision given the current context.

        This is the main method called during simulation cycles.

        Args:
            context: Current simulation state

        Returns:
            AgentResponse with decision and metrics
        """
        # Build full prompt
        system_prompt = self.get_persona_prompt()
        user_prompt = self.get_decision_prompt(context)

        # Add memory context
        memory_context = self.memory.get_context()
        user_prompt = f"{user_prompt}\n\n## Your Recent Memory\n{memory_context}"

        # Call LLM
        raw_response = self._call_llm(system_prompt, user_prompt)

        # Parse response
        response = self.parse_response(raw_response)
        response.raw_response = raw_response

        # Update memory
        self.memory.add({
            "cycle": context.get("cycle", 0),
            "decision": response.decision,
            "key_metrics": response.metrics,
        })

        return response

    async def decide_async(self, context: Dict[str, Any]) -> AgentResponse:
        """Async version of decide for parallel execution."""
        system_prompt = self.get_persona_prompt()
        user_prompt = self.get_decision_prompt(context)
        memory_context = self.memory.get_context()
        user_prompt = f"{user_prompt}\n\n## Your Recent Memory\n{memory_context}"

        raw_response = await self._call_llm_async(system_prompt, user_prompt)
        response = self.parse_response(raw_response)
        response.raw_response = raw_response

        self.memory.add({
            "cycle": context.get("cycle", 0),
            "decision": response.decision,
            "key_metrics": response.metrics,
        })
        return response

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the LLM API.

        Args:
            system_prompt: System/persona prompt
            user_prompt: User/decision prompt

        Returns:
            LLM response text
        """
        # Ollama doesn't need API key
        if self.provider != LLMProvider.OLLAMA and not self._api_key:
            return self._mock_response()

        if self.provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(system_prompt, user_prompt)
        elif self.provider == LLMProvider.OPENAI:
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == LLMProvider.GOOGLE:
            return self._call_google(system_prompt, user_prompt)
        elif self.provider == LLMProvider.GROQ:
            return self._call_groq(system_prompt, user_prompt)
        elif self.provider == LLMProvider.TOGETHER:
            return self._call_together(system_prompt, user_prompt)
        elif self.provider == LLMProvider.OLLAMA:
            return self._call_ollama(system_prompt, user_prompt)
        else:
            return self._call_openai(system_prompt, user_prompt)

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic Claude API."""
        response = self._client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "temperature": self.temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        response = self._client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": 1024,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_google(self, system_prompt: str, user_prompt: str) -> str:
        """Call Google Gemini API."""
        response = self._client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": self._api_key},
            json={
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": 1024,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Call Groq API (OpenAI-compatible)."""
        response = self._client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": 1024,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_together(self, system_prompt: str, user_prompt: str) -> str:
        """Call Together AI API (OpenAI-compatible)."""
        response = self._client.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": 1024,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Call local Ollama API."""
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        response = self._client.post(
            f"{ollama_host}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {"temperature": self.temperature},
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    def _mock_response(self) -> str:
        """Return mock response for testing without API."""
        return json.dumps({
            "decision": "MOCK_DECISION",
            "reasoning": "This is a mock response for testing without API key.",
            "confidence": 0.5,
            "metrics": {},
            "signals": ["mock_signal"],
        })

    async def _call_llm_async(self, system_prompt: str, user_prompt: str) -> str:
        """Async LLM API call for parallel execution."""
        # Ollama doesn't need API key
        if self.provider != LLMProvider.OLLAMA and not self._api_key:
            return self._mock_response()

        # Create a fresh client for each call to avoid connection issues in parallel
        async with httpx.AsyncClient(timeout=60.0) as client:
            if self.provider == LLMProvider.ANTHROPIC:
                return await self._call_anthropic_async(system_prompt, user_prompt, client)
            elif self.provider == LLMProvider.OPENAI:
                return await self._call_openai_async(system_prompt, user_prompt, client)
            elif self.provider == LLMProvider.GOOGLE:
                return await self._call_google_async(system_prompt, user_prompt, client)
            elif self.provider == LLMProvider.GROQ:
                return await self._call_groq_async(system_prompt, user_prompt, client)
            elif self.provider == LLMProvider.TOGETHER:
                return await self._call_together_async(system_prompt, user_prompt, client)
            elif self.provider == LLMProvider.OLLAMA:
                return await self._call_ollama_async(system_prompt, user_prompt, client)
            else:
                return await self._call_openai_async(system_prompt, user_prompt, client)

    async def _call_anthropic_async(self, system_prompt: str, user_prompt: str, client: httpx.AsyncClient) -> str:
        """Async Anthropic API call."""
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "temperature": self.temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    async def _call_openai_async(self, system_prompt: str, user_prompt: str, client: httpx.AsyncClient) -> str:
        """Async OpenAI API call."""
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": 1024,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_google_async(self, system_prompt: str, user_prompt: str, client: httpx.AsyncClient) -> str:
        """Async Google Gemini API call."""
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": self._api_key},
            json={
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": 1024,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_groq_async(self, system_prompt: str, user_prompt: str, client: httpx.AsyncClient) -> str:
        """Async Groq API call (OpenAI-compatible)."""
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": 1024,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_together_async(self, system_prompt: str, user_prompt: str, client: httpx.AsyncClient) -> str:
        """Async Together AI API call (OpenAI-compatible)."""
        response = await client.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": 1024,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_ollama_async(self, system_prompt: str, user_prompt: str, client: httpx.AsyncClient) -> str:
        """Async local Ollama API call."""
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        response = await client.post(
            f"{ollama_host}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {"temperature": self.temperature},
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    def reset(self) -> None:
        """Reset agent state for new simulation."""
        self.memory.clear()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type})"
