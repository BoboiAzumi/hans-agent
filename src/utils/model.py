from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openrouter import ChatOpenRouter

def model_init(
    provider,
    model,
    key = "",
    base_url = ""
):
    llm = None

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

    if llm == None:
        raise

    return llm