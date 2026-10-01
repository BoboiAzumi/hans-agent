from langchain_tavily import TavilySearch

tool_call = TavilySearch(
    max_result=10,
    topic="news"
)