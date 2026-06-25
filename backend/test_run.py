import os
import asyncio
import sys
from dotenv import load_dotenv

# Load env variables from parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
load_dotenv()

# Map AI_STUDIO_API to GEMINI_API_KEY for ADK 2.0
if "AI_STUDIO_API" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["AI_STUDIO_API"]

from google.adk.runners import InMemoryRunner
from google.adk.apps import App
from agent_workflow import space_workflow

async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY or AI_STUDIO_API env variable not set.")
        sys.exit(1)
        
    adk_app = App(
        name="space_education_agent",
        root_agent=space_workflow
    )
    
    async with InMemoryRunner(app=adk_app) as runner:
        query = "Tell me about Mars and its gravity"
        print(f"Running test query: '{query}'...")
        try:
            events = await runner.run_debug(query, quiet=True)
            
            print("\n--- Event Stream Log ---")
            final_response = None
            for i, event in enumerate(events):
                author = event.author if event.author else "system/node"
                print(f"[{i}] Event from '{author}':")
                
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(f"    Text Part: {part.text[:200]}...")
                            final_response = part.text
                
                msg = getattr(event, "message", None)
                if msg:
                    # Safely handle Content object or string
                    if hasattr(msg, 'parts') and msg.parts:
                        msg_text = "".join([p.text for p in msg.parts if p.text])
                    else:
                        msg_text = str(msg)
                    print(f"    Message Field: {msg_text[:200]}...")
                    final_response = msg_text
            
            print("\n--- Final Captured Response ---")
            print(final_response)
            
        except Exception as e:
            print(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
