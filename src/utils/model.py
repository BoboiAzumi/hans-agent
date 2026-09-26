import os

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openrouter import ChatOpenRouter


def _custom_env_active():
    return any(
        os.getenv(name)
        for name in ("CUSTOM_MODEL", "CUSTOM_API_KEY", "CUSTOM_BASE_URL")
    )


def model_init(
    provider,
    model,
    key = "",
    base_url = ""
):
    llm = None

    if _custom_env_active():
        provider = "custom"

    match provider:
        case "openai":
            llm = ChatOpenAI(
                model=model,
                api_key=key,
                streaming=False
            )
        case "google-gen-ai":
            llm = ChatGoogleGenerativeAI(
                model=model,
                api_key=key,
                streaming=False,
                thinking_level="minimal"
            )
        case "nvidia":
            llm = ChatNVIDIA(
                model=model,
                api_key=key,
                timeout=6000,
                max_tokens=50000,
            )
        case "openrouter":
            llm = ChatOpenRouter(
                model=model,
                api_key=key,
                base_url=base_url,
                max_tokens=8000,
            )
        case "custom":
            api_type = os.getenv("CUSTOM_API_TYPE", "openai").lower()
            model = os.getenv("CUSTOM_MODEL") or model
            key = os.getenv("CUSTOM_API_KEY") or key
            base_url = os.getenv("CUSTOM_BASE_URL") or base_url
            max_tokens = int(os.getenv("CUSTOM_MAX_TOKENS", "8000"))
            timeout = int(os.getenv("CUSTOM_TIMEOUT", "6000"))

            if api_type == "anthropic":
                llm = ChatAnthropic(
                    model=model,
                    api_key=key or None,
                    base_url=base_url or None,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
            else:
                llm = ChatOpenAI(
                    model=model,
                    api_key=key or None,
                    base_url=base_url or None,
                    max_tokens=max_tokens,
                    timeout=timeout,
                    streaming=False,
                )

    if llm == None:
        raise ValueError(f"Unsupported provider: {provider}")

    return llm
