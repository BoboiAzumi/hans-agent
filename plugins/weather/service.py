import requests
from langchain_core.tools import tool

@tool
def tool_call(city: str):
    '''
    Cek Informasi Cuaca di sebuah kota
    arguments:
        city: nama kota
    '''

    response = requests.get(
        f"https://wttr.in/{city}",
        params={"format": "j1"}
    )

    return response.json()