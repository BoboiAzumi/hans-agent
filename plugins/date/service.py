from datetime import datetime
from langchain_core.tools import tool

@tool
def tool_call():
    '''
    Merupakan tool untuk mengetahui tanggal dan waktu
    format keluaran
    Tahun-Bulan-Hari Jam-Menit-Detik dan mikro detik
    '''
    x = datetime.now()
    return x