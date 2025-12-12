from app.models import Input_Query,Output_Response
from openai import OpenAI
import os
import json

TEMPERATURE_DICT = {
    "Coding" : 0.0,
    "Data Cleaning": 1.0,
    "Conversation": 1.3,
    "Translation" : 1.3,
    "Creative Writing": 1.5
}

def ai_request(request:Input_Query) -> Output_Response:
    temp = TEMPERATURE_DICT.get(request.type, 1.0) 

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
    
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False,
        response_format={'type': 'json_object'},
        temperature=temp
    )

    content_str = response.choices[0].message.content
    content_dict = json.loads(content_str)
    assert type(content_dict) == dict[str, any]
    
    response_class = Output_Response.model_validate(content_dict)
    return response_class

