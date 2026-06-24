import os
import time
import sys
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
load_dotenv()

key = os.environ.get("AI_STUDIO_API")
if not key:
    print("Error: AI_STUDIO_API key is not configured in .env file.")
    sys.exit(1)

client = genai.Client(api_key=key)

# Default to a highly responsive and available model based on connection tests
model = "gemma-4-31b-it"

print(f"==================================================")
print(f"  Cosmos Stream Terminal (Model: {model})")
print(f"==================================================")
print("Type your questions below. Enter 'exit' or 'quit' to stop.\n")

while True:
    try:
        query = input("\nAstronomy Student: ")
        if query.strip().lower() in ["exit", "quit"]:
            print("Closing connection. Clear skies!")
            break
        if not query.strip():
            continue
            
        print("Educator response: ", end="", flush=True)
        
        start_time = time.time()
        first_chunk_time = None
        
        # Stream content
        response = client.models.generate_content_stream(model=model, contents=query)
        
        for chunk in response:
            if chunk.text:
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                print(chunk.text, end="", flush=True)
                
        end_time = time.time()
        
        # Telemetry calculations
        total_duration = end_time - start_time
        print("\n" + "-"*50)
        if first_chunk_time:
            time_to_first_token = first_chunk_time - start_time
            print(f"⏱️ Time to first chunk: {time_to_first_token:.3f} seconds")
        print(f"⏱️ Total generation time: {total_duration:.3f} seconds")
        print("-"*50)
        
    except KeyboardInterrupt:
        print("\nClosing connection. Clear skies!")
        break
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
