import os
import sys
import json
import re
from pydantic import BaseModel, Field
from google.adk import Agent, Workflow, Event
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# ---------------------------------------------------------
# Helper: Clean Markdown JSON wrapper
# ---------------------------------------------------------
def clean_json_string(s: str) -> str:
    s = s.strip()
    # Remove any markdown code block wrappers if present
    if s.startswith("```"):
        nl = s.find("\n")
        if nl != -1:
            s = s[nl:].strip()
        s = s.rstrip("`").strip()
        
    # Find all indices of '{'
    braces = [i for i, char in enumerate(s) if char == '{']
    if not braces:
        return s
        
    end = s.rfind('}')
    if end == -1:
        return s
        
    # Try parsing starting from each '{' index
    for start in braces:
        if start >= end:
            break
        substring = s[start:end+1]
        try:
            # Import json locally to ensure it is available
            import json
            json.loads(substring)
            return substring
        except json.JSONDecodeError:
            continue
            
    # Fallback to the original simple extraction if nothing parses
    start = s.find('{')
    if start != -1 and end > start:
        return s[start:end+1]
    return s

# ---------------------------------------------------------
# 1. Define Structured Schemas
# ---------------------------------------------------------

class ClassificationOutput(BaseModel):
    query: str
    is_astronomy_related: bool = Field(
        description="Is this query related to astronomy, space science, planets, spacecraft, stars, or space missions?"
    )
    detected_planet_or_spacecraft: str | None = Field(
        None,
        description="The name of the specific planet, moon, or spacecraft mentioned (e.g., Mars, Saturn, Voyager 1, Cassini, Webb), if any."
    )

class TextContentInput(BaseModel):
    text: str = Field(
        description="Text content containing the user query and fetched NASA data."
    )

class SpaceEducationOutput(BaseModel):
    educational_response: str = Field(
        description="An engaging, educational response for the student explaining the answer using the fetched NASA data."
    )
    is_space_related: bool = Field(
        True,
        description="Always true if related, false if unrelated."
    )
    simulation_target: str | None = Field(
        None,
        description="The exact NASA eyes simulation key for the planet or spacecraft (e.g., 'mars', 'sc_voyager_1'), or null if not applicable."
    )
    simulation_url: str | None = Field(
        None,
        description="The exact URL to embed in the iframe (e.g. 'https://eyes.nasa.gov/apps/solar-system/#/mars'), or null if not applicable."
    )

# ---------------------------------------------------------
# 2. Configure MCP Toolset for NASA API Server
# ---------------------------------------------------------

def get_nasa_mcp_toolset():
    # Use sys.executable to ensure it runs within the virtual environment Python
    mcp_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "nasa_mcp_server.py"))
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=["-u", mcp_script]
            )
        )
    )

nasa_toolset = get_nasa_mcp_toolset()

# ---------------------------------------------------------
# 3. Create Workflow Nodes (Agents and Functions)
# ---------------------------------------------------------

# Classifier Node: determines if query is space-related (Outputs raw text to avoid ADK validation errors)
classifier_agent = Agent(
    name="classifier_agent",
    model=Gemini(model="gemma-4-31b-it"),
    instruction="""Determine if the user query is related to astronomy, planetary science, stars, asteroids, spacecraft, space missions, or space weather.
    If it is, set is_astronomy_related to true and extract the target planet, moon, or spacecraft (if any).
    If it is not related to astronomy (e.g., questions about web design, recipes, or general knowledge), set is_astronomy_related to false.
    
    You must output a valid JSON object matching this schema:
    {{
      "query": "the original user query string",
      "is_astronomy_related": true or false,
      "detected_planet_or_spacecraft": "name of planet or spacecraft or null"
    }}
    
    CRITICAL: Output ONLY the raw JSON. Do not wrap in markdown code blocks (do not use triple backticks ``` or ```json).""",
    mode="single_turn"
)

# Robust parsing node for classifier output
def parse_classification_node(node_input: str):
    """Safely cleans and parses the classifier's text output into a ClassificationOutput model."""
    cleaned = clean_json_string(node_input)
    try:
        data = json.loads(cleaned)
        output = ClassificationOutput(
            query=data.get("query", ""),
            is_astronomy_related=bool(data.get("is_astronomy_related", True)),
            detected_planet_or_spacecraft=data.get("detected_planet_or_spacecraft")
        )
    except Exception as e:
        # Robust fallback
        is_astro = "true" in cleaned.lower() or "astronomy" in cleaned.lower() or "planet" in cleaned.lower()
        match = re.search(r'"detected_planet_or_spacecraft"\s*:\s*"([^"]+)"', cleaned)
        target = match.group(1) if match else None
        output = ClassificationOutput(
            query="",
            is_astronomy_related=is_astro,
            detected_planet_or_spacecraft=target
        )
    return Event(output=output)

# Routing function based on classifier output
def router_node(node_input: ClassificationOutput):
    """Routes the workflow based on query relevance."""
    if node_input.is_astronomy_related:
        return Event(route="ASTRONOMY", output=node_input)
    return Event(route="UNRELATED", output=node_input)

# NASA Data Node: executes MCP tools to fetch live stats (No structured output schema to prevent conflict with tools)
nasa_data_agent = Agent(
    name="nasa_data_agent",
    model=Gemini(model="gemini-2.5-flash"),
    input_schema=ClassificationOutput,
    instruction="""You are the NASA Data Retrieval Agent.
    Your goal is to fetch live, real-time details from NASA APIs using the tools available to you.
    
    The user's query is: "{ClassificationOutput.query}"
    The detected target is: "{ClassificationOutput.detected_planet_or_spacecraft}"
    
    Guidelines:
    - If the user asks about the Astronomy Picture of the Day, call `get_astronomy_picture`.
    - If they ask about asteroids, close approaches, or hazards, call `get_near_earth_objects`.
    - If they ask about space weather, solar flares, or CMEs, call `get_space_weather_alerts`.
    - If they ask about a specific planet or spacecraft, call `get_planetary_details` with the planet/spacecraft name.
    
    Execute the tool that best fits the query. Return the results as plain text.
    Your response must include:
    Original Query: {ClassificationOutput.query}
    NASA Data: [The exact raw text returned from calling your tool]
    """,
    tools=[nasa_toolset],
    mode="single_turn"
)

# Text wrapper helper node
def wrap_text_node(node_input: str):
    """Wraps string output from previous node into a TextContentInput pydantic model."""
    return Event(output=TextContentInput(text=node_input))

# Pedagogical Node: translates details into student-friendly explanations
pedagogical_agent = Agent(
    name="pedagogical_agent",
    model=Gemini(model="gemma-4-31b-it"),
    input_schema=TextContentInput,
    instruction="""You are an enthusiastic, expert Astronomy and Space Science Educator.
    Your goal is to explain astronomical concepts to students in an engaging, inspiring, and clear way.
    
    You are given a text containing the original student query and the raw NASA data:
    "{TextContentInput.text}"
    
    Guidelines:
    - Identify the student's query and the NASA data.
    - Explain the concepts clearly. Include interesting facts from the NASA data.
    - If a specific planet or spacecraft is active in the data and a 'NASA Eyes Simulation Key' is present (e.g., 'mars', 'sc_voyager_1'), set `simulation_target` to that key and populate `simulation_url` by appending the target key to the base URL 'https://eyes.nasa.gov/apps/solar-system/#/'. For example, if target is 'mars', the URL is 'https://eyes.nasa.gov/apps/solar-system/#/mars'.
    - If no planet/spacecraft is applicable or target is not in the data, set `simulation_target` and `simulation_url` to null.
    
    You must output a valid JSON object matching this schema:
    {{
      "educational_response": "your engaging explanation",
      "is_space_related": true,
      "simulation_target": "mars" (or another target key, or null),
      "simulation_url": "https://eyes.nasa.gov/apps/solar-system/#/mars" (or null)
    }}
    
    CRITICAL: Output ONLY the raw JSON. Do not wrap in markdown code blocks (do not use triple backticks ``` or ```json).""",
    mode="single_turn"
)

# Polite Decline Node: handles unrelated queries
def decline_node(node_input: ClassificationOutput):
    """Politely declines to answer non-astronomy queries."""
    decline_data = SpaceEducationOutput(
        educational_response=(
            "I'm sorry, but I am an Astronomy and Space Science Educator! "
            "I can only help you explore planets, stars, asteroids, space weather, and space missions. "
            "Ask me something about the cosmos, and I'd love to explain it to you!"
        ),
        is_space_related=False,
        simulation_target=None,
        simulation_url=None
    )
    return Event(
        message=decline_data.model_dump_json()
    )

# ---------------------------------------------------------
# 4. Construct the Workflow Graph
# ---------------------------------------------------------

space_workflow = Workflow(
    name="space_education_workflow",
    edges=[
        ("START", classifier_agent, parse_classification_node),
        (parse_classification_node, router_node),
        (router_node, {
            "ASTRONOMY": nasa_data_agent,
            "UNRELATED": decline_node
        }),
        (nasa_data_agent, wrap_text_node, pedagogical_agent)
    ]
)
