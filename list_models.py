import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    for model in client.models.list_models():
        print(model.name)
except Exception as e:
    print(f"ERROR: {str(e)}")
