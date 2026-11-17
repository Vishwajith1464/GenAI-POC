from dotenv import load_dotenv
load_dotenv()
# The client automatically picks up the GEMINI_API_KEY environment variable

def import_google_sdk():
    from google import genai
    return genai
user_prompt = input("Enter your prompt: ")
client = import_google_sdk().Client()
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=user_prompt
)
print(response.text)
