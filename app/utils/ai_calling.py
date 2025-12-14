from app.models import Input_Query,Output_Response
from openai import APITimeoutError, OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()


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

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_query},
            ],
            stream=False,
            response_format={'type': 'json_object'},
            temperature=temp,
            timeout=30.0
        )
    except APITimeoutError:
        raise TimeoutError("AI Request timed out after 30 seconds.")
    content_str = response.choices[0].message.content
    content_dict = json.loads(content_str)
    
    response_class = Output_Response.model_validate(content_dict)
    return response_class

