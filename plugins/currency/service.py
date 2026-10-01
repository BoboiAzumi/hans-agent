import requests
from langchain_core.tools import tool

@tool
def tool_call(c_from_symbol: str, c_to_symbol: str, amount: float = 0.0):
    '''
        Tool untuk mencari tahu rate konversi mata uang,
        Arguments:
            c_from_symbol: simbol mata uang asal, misalnya idr untuk rupiah
            c_to_symbol: simbol mata uang tujuan, misalnya usd untuk us dollar
            amount (opsional): nilai asal mata uang

            misalnya
            c_from_symbol = "idr"
            c_to_symbol = "usd"
            amount = 15000

            berarti konversi 15000 rupiah menjadi usd, (nanti ada key converted, itu hasil konversinya)

            tapi jika amount = 0, maka hanya mencari tahu rate nilai tukar saja
    '''
    result = requests.get(f"https://api.frankfurter.dev/v2/rate/{c_from_symbol.lower()}/{c_to_symbol.lower()}")
    result.raise_for_status()

    result = result.json()

    if amount > 0:
        result["amount"] = amount
        result["converted"] = result["amount"] * float(result["rate"])

    return result