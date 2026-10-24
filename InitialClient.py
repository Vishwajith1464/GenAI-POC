from google import genai
from dotenv import load_dotenv

load_dotenv()
# The client automatically picks up the GEMINI_API_KEY environment variable
client = genai.Client()
user_prompt = input("Enter your prompt: ")
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=user_prompt
)
print(response.text)
