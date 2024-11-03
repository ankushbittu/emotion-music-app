import openai
import os
from dotenv import load_dotenv
load_dotenv()   

openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key
prompt = "What is the capital of France?"

try:
    response = openai.Completion.create(
        model="",
        prompt=prompt,
        max_tokens=50,
        temperature=0.7
    )
    print(response.choices[0].text.strip())
except Exception as e:
    print(f"Error: {e}")
