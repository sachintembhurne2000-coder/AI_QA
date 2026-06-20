"""
LLM Service — unified interface for Claude, OpenAI, and Ollama
"""
import streamlit as st
import json
import re
from typing import Optional


def get_llm_config() -> dict:
    """Pull current provider/key/model from Streamlit session state."""
    return {
        "provider": st.session_state.get("llm_provider", "Claude (Anthropic)"),
        "api_key": st.session_state.get("api_key", ""),
        "model": st.session_state.get("model", "claude-sonnet-4-6"),
    }


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """
    Single unified call to the configured LLM.
    Returns the assistant text response.
    Raises ValueError on missing API key or network errors.
    """
    cfg = get_llm_config()
    provider = cfg["provider"]
    api_key = cfg["api_key"]
    model = cfg["model"]

    if provider == "Claude (Anthropic)":
        return _call_anthropic(api_key, model, system_prompt, user_prompt, max_tokens)
    elif provider == "OpenAI GPT-4":
        return _call_openai(api_key, model, system_prompt, user_prompt, max_tokens)
    else:
        return _call_ollama(model, system_prompt, user_prompt, max_tokens)


def _call_anthropic(api_key: str, model: str, system: str, user: str, max_tokens: int) -> str:
    if not api_key:
        raise ValueError("Anthropic API key is missing. Enter it in the sidebar.")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text
    except ImportError:
        raise ValueError("anthropic package not installed. Run: pip install anthropic")
    except Exception as e:
        raise ValueError(f"Anthropic API error: {e}")


def _call_openai(api_key: str, model: str, system: str, user: str, max_tokens: int) -> str:
    if not api_key:
        raise ValueError("OpenAI API key is missing. Enter it in the sidebar.")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content
    except ImportError:
        raise ValueError("openai package not installed. Run: pip install openai")
    except Exception as e:
        raise ValueError(f"OpenAI API error: {e}")


def _call_ollama(model: str, system: str, user: str, max_tokens: int) -> str:
    import requests
    try:
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as e:
        raise ValueError(f"Ollama error (is it running?): {e}")


def extract_json(text: str) -> any:
    """
    Extract the first JSON object or array from an LLM response.
    Strips markdown code fences if present.
    """
    # Remove markdown code fences
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find first [ or { and extract
    for start_char, end_char in [("[", "]"), ("{", "}")]:
        start = text.find(start_char)
        if start != -1:
            # Find matching close
            depth = 0
            for i, ch in enumerate(text[start:], start):
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[start:i+1])
                        except json.JSONDecodeError:
                            break

    raise ValueError(f"Could not extract JSON from LLM response:\n{text[:500]}")
