from typing import Literal, Optional
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

class SupervisorState(MessagesState):
    mode: Optional[str]
    summary: Optional[str]
    important: Optional[str]
    target_agent: Optional[str]
    task: Optional[str]
    consult_result: Optional[str]
    consulted_agent: list[str]
    hop_count: int

class SupervisorDecision(BaseModel):
    """Gunakan tool ini HANYA saat perlu delegate atau consult ke sub-agent.
    Kalau ingin menjawab langsung (answer), TIDAK perlu memanggil tool ini —
    cukup tulis jawaban langsung sebagai teks biasa."""
    mode: Literal[
        #"answer", 
        "delegate", 
        "consult"
    ] = Field(
        description=#"answer = jawab sendiri jika memungkinkan, \n"
                    "delegate = serahkan ke agent lain, \n"
                    "consult = minta pendapat agent lain"
    )
    answer_text: Optional[str] = Field(
        default=None,
        description="WAJIB diisi kalau mode='answer', ini jawaban final yang akan dikirim ke user."
    )
    target_agent: Optional[str] = Field(default=None, description="Nama sub-agent kalau delegate/consult")
    task: Optional[str] = Field(
        default=None,
        description="Pesan/tugas yang akan dikirim ke sub-agent. "
                    "Wajib diisi saat mode delegate atau consult."
    )

class Summarization(BaseModel):
    summary: str = Field(description="Ringkasan informasi")
    important: str = Field(description="Informasi penting yang harus dicatat")