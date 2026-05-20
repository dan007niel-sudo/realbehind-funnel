import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def main():
    if not GOOGLE_API_KEY:
        raise SystemExit("GOOGLE_API_KEY must be set to run this live check.")

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

if __name__ == "__main__":
    main()
