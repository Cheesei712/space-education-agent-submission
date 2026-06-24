import os
import dotenv
from google import genai

# Load environment
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
dotenv.load_dotenv()

key = os.environ.get("AI_STUDIO_API")
if not key:
    print("Error: AI_STUDIO_API key is not configured.")
    exit(1)

client = genai.Client(api_key=key)

candidate_models = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",
    "gemini-flash-latest",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro"
]

print("Testing model connections...")
for model in candidate_models:
    try:
        response = client.models.generate_content_stream(model=model, contents="Hi")
        text_chunks = [chunk.text for chunk in response if chunk.text]
        full_text = "".join(text_chunks)
        print(f"[{model}] -> SUCCESS: {full_text.strip()}")
    except Exception as e:
        # Extract status code if available
        err_msg = str(e).split("\n")[0]
        print(f"[{model}] -> FAILED: {err_msg}")
