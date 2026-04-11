import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=["Test message"]
    )
    print("SUCCESS Gemini!")
    print(response.text)
except Exception as e:
    print(f"ERROR Gemini: {str(e)}")
