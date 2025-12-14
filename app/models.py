# app/core/models.py

from typing import Literal
from pydantic import BaseModel

class Chapter(BaseModel):
    file_name: int
    title: str
    chapter_number: str
    content: str

class Raw_Chapter(Chapter):
    url: str
    type: str = "raw"

class Translated_Chapter(Chapter):
    raw_path: list[str]
    type: str = "translated"

class Input_Query(BaseModel):
    type: Literal["Coding", "Data Cleaning", "Conversation", "Translation", "Creative Writing"]
    system_prompt: str
    user_query: str

class Output_Response(BaseModel):
    response: str
    error: bool = False
    error_message: str = ""
