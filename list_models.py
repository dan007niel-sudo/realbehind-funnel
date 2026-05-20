import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def main():
    if not GOOGLE_API_KEY:
        raise SystemExit("GOOGLE_API_KEY must be set to list Gemini models.")

    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        for model in client.models.list_models():
            print(model.name)
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()
