import os
import sys
import requests
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load env variables (NASA_API)
load_dotenv()
NASA_API = os.getenv("NASA_API", "DEMO_KEY")

# Create FastMCP server
mcp = FastMCP("NASA Data Server")

@mcp.tool()
def get_astronomy_picture() -> str:
    """Fetch NASA's Astronomy Picture of the Day (APOD) metadata.
    Includes the title, date, description, and high-quality image/video URL.
    """
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return (
                f"Title: {data.get('title')}\n"
                f"Date: {data.get('date')}\n"
                f"URL: {data.get('url')}\n"
                f"Explanation: {data.get('explanation')}"
            )
        return f"Error: Received status code {resp.status_code} from NASA APOD API"
    except Exception as e:
        return f"Error fetching APOD: {str(e)}"

@mcp.tool()
def get_near_earth_objects(date_str: str = None) -> str:
    """Fetch near-Earth objects (asteroids) close approach data.
    Specify date_str in YYYY-MM-DD format. If omitted, uses today's date.
    Returns details on size, velocity, and distance of passing asteroids.
    """
    if not date_str:
        date_str = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={date_str}&end_date={date_str}&api_key={NASA_API}"
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            neo_count = data.get("element_count", 0)
            neos_for_day = data.get("near_earth_objects", {}).get(date_str, [])
            
            output = f"Date: {date_str}\nTotal NeoWs Asteroids Detected: {neo_count}\n\n"
            for i, neo in enumerate(neos_for_day[:5]): # limit to top 5 for brevity
                name = neo.get("name")
                is_hazard = neo.get("is_potentially_hazardous_asteroid")
                diameter_min = neo.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_min", 0)
                diameter_max = neo.get("estimated_diameter", {}).get("meters", {}).get("estimated_diameter_max", 0)
                
                close_approach = neo.get("close_approach_data", [{}])[0]
                velocity = close_approach.get("relative_velocity", {}).get("kilometers_per_hour", "N/A")
                miss_distance = close_approach.get("miss_distance", {}).get("kilometers", "N/A")
                
                output += (
                    f"{i+1}. Asteroid: {name}\n"
                    f"   Potentially Hazardous: {is_hazard}\n"
                    f"   Estimated Diameter: {diameter_min:.1f}m - {diameter_max:.1f}m\n"
                    f"   Relative Velocity: {float(velocity):,.1f} km/h\n"
                    f"   Miss Distance: {float(miss_distance):,.1f} km\n\n"
                )
            return output
        return f"Error: Received status code {resp.status_code} from NASA NeoWs API"
    except Exception as e:
        return f"Error fetching NeoWs: {str(e)}"

@mcp.tool()
def get_space_weather_alerts(event_type: str = "FLR") -> str:
    """Fetch space weather event alerts from NASA DONKI (Space Weather Database).
    Accepts event_type of 'FLR' (Solar Flares) or 'CME' (Coronal Mass Ejections).
    Returns recent events with startTime, activity class, and coordinates.
    """
    if event_type not in ["FLR", "CME"]:
        return "Error: event_type must be either 'FLR' or 'CME'."
    
    url = f"https://api.nasa.gov/DONKI/{event_type}?api_key={NASA_API}"
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            if not data:
                return f"No recent space weather events of type {event_type} found."
            
            output = f"Recent Space Weather Events ({event_type}):\n\n"
            for i, event in enumerate(data[:5]): # Top 5 events
                if event_type == "FLR":
                    flr_id = event.get("flrID")
                    start_time = event.get("beginTime")
                    peak_time = event.get("peakTime")
                    class_type = event.get("classType")
                    region = event.get("activeRegionNum")
                    output += (
                        f"{i+1}. Solar Flare ID: {flr_id}\n"
                        f"   Begin Time: {start_time}\n"
                        f"   Peak Time: {peak_time}\n"
                        f"   Class: {class_type} (Energy scale)\n"
                        f"   Active Region: {region}\n\n"
                    )
                else:
                    cme_id = event.get("activityID")
                    start_time = event.get("startTime")
                    instruments = [inst.get("displayName") for inst in event.get("instruments", [])]
                    output += (
                        f"{i+1}. Coronal Mass Ejection ID: {cme_id}\n"
                        f"   Start Time: {start_time}\n"
                        f"   Instruments: {', '.join(instruments)}\n\n"
                    )
            return output
        return f"Error: Received status code {resp.status_code} from NASA DONKI API"
    except Exception as e:
        return f"Error fetching DONKI: {str(e)}"

# A comprehensive fact sheet database for simulation bodies.
FACT_SHEET = {
    # Planets
    "mercury": {
        "name": "Mercury",
        "type": "Planet",
        "description": "The smallest planet in our solar system and nearest to the Sun. Mercury is only slightly larger than Earth's Moon.",
        "orbit_period": "88 Earth days",
        "distance_from_sun": "0.39 AU (57.9 million km)",
        "gravity": "3.7 m/s²",
        "moons": "None",
        "nasa_eyes_key": "mercury"
    },
    "venus": {
        "name": "Venus",
        "type": "Planet",
        "description": "Venus is the second planet from the Sun and our closest planetary neighbor. Its thick atmosphere traps heat in a runaway greenhouse effect.",
        "orbit_period": "225 Earth days",
        "distance_from_sun": "0.72 AU (108.2 million km)",
        "gravity": "8.87 m/s²",
        "moons": "None",
        "nasa_eyes_key": "venus"
    },
    "earth": {
        "name": "Earth",
        "type": "Planet",
        "description": "Our home planet is the third planet from the Sun, and the only place we know of so far that’s inhabited by living things.",
        "orbit_period": "365.25 days",
        "distance_from_sun": "1.00 AU (149.6 million km)",
        "gravity": "9.81 m/s²",
        "moons": "1 (The Moon)",
        "nasa_eyes_key": "earth"
    },
    "mars": {
        "name": "Mars",
        "type": "Planet",
        "description": "Mars is a dusty, cold, desert world with a very thin atmosphere. There is strong evidence Mars was—billions of years ago—wetter and warmer.",
        "orbit_period": "687 Earth days",
        "distance_from_sun": "1.52 AU (227.9 million km)",
        "gravity": "3.71 m/s²",
        "moons": "2 (Phobos, Deimos)",
        "nasa_eyes_key": "mars"
    },
    "jupiter": {
        "name": "Jupiter",
        "type": "Planet",
        "description": "Jupiter is more than twice as massive than the other planets of our solar system combined. The giant planet's Great Red Spot is a centuries-old storm.",
        "orbit_period": "12 Earth years",
        "distance_from_sun": "5.20 AU (778.5 million km)",
        "gravity": "24.79 m/s²",
        "moons": "95 confirmed moons",
        "nasa_eyes_key": "jupiter"
    },
    "saturn": {
        "name": "Saturn",
        "type": "Planet",
        "description": "Adorned with a dazzling, complex system of icy rings, Saturn is unique in our solar system. The other giant planets have rings, but none are as spectacular as Saturn's.",
        "orbit_period": "29 Earth years",
        "distance_from_sun": "9.58 AU (1.4 billion km)",
        "gravity": "10.44 m/s²",
        "moons": "146 confirmed moons",
        "nasa_eyes_key": "saturn"
    },
    "uranus": {
        "name": "Uranus",
        "type": "Planet",
        "description": "Uranus is the seventh planet from the Sun. Its unique tilt causes it to rotate on its side, nearly pointing its poles at the Sun.",
        "orbit_period": "84 Earth years",
        "distance_from_sun": "19.22 AU (2.9 billion km)",
        "gravity": "8.69 m/s²",
        "moons": "28 confirmed moons",
        "nasa_eyes_key": "uranus"
    },
    "neptune": {
        "name": "Neptune",
        "type": "Planet",
        "description": "Neptune, the eighth and most distant major planet orbiting our Sun, is dark, cold, and whipped by supersonic winds.",
        "orbit_period": "165 Earth years",
        "distance_from_sun": "30.05 AU (4.5 billion km)",
        "gravity": "11.15 m/s²",
        "moons": "16 confirmed moons",
        "nasa_eyes_key": "neptune"
    },
    "pluto": {
        "name": "Pluto",
        "type": "Dwarf Planet",
        "description": "Pluto is a complex world of ice mountains and blue skies. It was reclassified as a dwarf planet in 2006 by the IAU.",
        "orbit_period": "248 Earth years",
        "distance_from_sun": "39.48 AU (5.9 billion km)",
        "gravity": "0.62 m/s²",
        "moons": "5 (Charon, Styx, Nix, Kerberos, Hydra)",
        "nasa_eyes_key": "pluto"
    },
    # Spacecrafts
    "voyager 1": {
        "name": "Voyager 1",
        "type": "Spacecraft",
        "description": "Launched in 1977, Voyager 1 is the first human-made object to enter interstellar space. It is currently the most distant spacecraft from Earth.",
        "launch_date": "September 5, 1977",
        "mission_status": "Active (Interstellar Mission)",
        "notable_discoveries": "Discovered active volcanoes on Jupiter's moon Io and the complex structure of Saturn's rings.",
        "nasa_eyes_key": "sc_voyager_1"
    },
    "voyager 2": {
        "name": "Voyager 2",
        "type": "Spacecraft",
        "description": "Voyager 2 is the only spacecraft to study all four giant planets of our outer solar system (Jupiter, Saturn, Uranus, Neptune) up close.",
        "launch_date": "August 20, 1977",
        "mission_status": "Active (Interstellar Mission)",
        "notable_discoveries": "Only probe to visit Uranus and Neptune; discovered the rings of Neptune and moons of Uranus.",
        "nasa_eyes_key": "sc_voyager_2"
    },
    "cassini": {
        "name": "Cassini",
        "type": "Spacecraft",
        "description": "Cassini orbited Saturn for 13 years, gathering detailed data on the planet, its rings, and its moons before a planned plunge into Saturn's atmosphere in 2017.",
        "launch_date": "October 15, 1997",
        "mission_status": "Completed (Plunged into Saturn in 2017)",
        "notable_discoveries": "Discovered liquid hydrocarbon seas on Titan and geysers of water vapor erupting from Enceladus.",
        "nasa_eyes_key": "sc_cassini"
    },
    "new horizons": {
        "name": "New Horizons",
        "type": "Spacecraft",
        "description": "New Horizons conducted the first close-up flyby of Pluto in 2015 and later explored Kuiper Belt Object Arrokoth in 2019.",
        "launch_date": "January 19, 2006",
        "mission_status": "Active (Kuiper Belt Exploration)",
        "notable_discoveries": "Captured high-res images of Pluto's heart-shaped nitrogen ice plain (Tombaugh Regio).",
        "nasa_eyes_key": "sc_new_horizons"
    },
    "perseverance": {
        "name": "Perseverance",
        "type": "Spacecraft",
        "description": "NASA's Mars 2020 rover exploring Jezero Crater on Mars to search for signs of ancient life and collect rock and soil samples.",
        "launch_date": "July 30, 2020",
        "mission_status": "Active (Exploring Mars)",
        "notable_discoveries": "Successfully deployed the Ingenuity helicopter; confirmed ancient lakebed deposits in Jezero Crater.",
        "nasa_eyes_key": "sc_perseverance"
    },
    "curiosity": {
        "name": "Curiosity",
        "type": "Spacecraft",
        "description": "A car-sized Mars rover designed to explore Gale Crater as part of NASA's Mars Science Laboratory mission.",
        "launch_date": "November 26, 2011",
        "mission_status": "Active (Exploring Mars)",
        "notable_discoveries": "Found evidence of ancient liquid water in Gale Crater; detected seasonal variation in atmospheric methane.",
        "nasa_eyes_key": "sc_curiosity"
    },
    "hubble": {
        "name": "Hubble",
        "type": "Spacecraft",
        "description": "The Hubble Space Telescope is a large, space-based observatory that has revolutionized astronomy since its launch in 1990.",
        "launch_date": "April 24, 1990",
        "mission_status": "Active (Low Earth Orbit)",
        "notable_discoveries": "Helped pin down the age of the universe; verified the expansion rate of the universe is accelerating.",
        "nasa_eyes_key": "sc_hubble"
    },
    "james webb": {
        "name": "James Webb Space Telescope",
        "type": "Spacecraft",
        "description": "NASA's premier infrared space observatory, designed to peer back over 13.5 billion years to see the first stars and galaxies forming.",
        "launch_date": "December 25, 2021",
        "mission_status": "Active (L2 Orbit)",
        "notable_discoveries": "Captured the deepest and sharpest infrared images of the early universe; analyzed atmospheres of exoplanets.",
        "nasa_eyes_key": "sc_jwst"
    }
}

@mcp.tool()
def get_planetary_details(planet_name: str) -> str:
    """Get astronomical details, physical metrics, mission status, and orbital specifications
    for planets (e.g., Earth, Mars, Jupiter) or spacecraft (e.g., Voyager 1, Cassini, Perseverance, James Webb).
    Returns data containing a 'nasa_eyes_key' used to sync the 3D solar system simulation.
    """
    key = planet_name.lower().strip()
    # Check for approximate match
    match_key = None
    for k in FACT_SHEET.keys():
        if k in key or key in k:
            match_key = k
            break
            
    if not match_key:
        return (
            f"Could not find planetary details or spacecraft named '{planet_name}'. "
            f"Available targets: {', '.join(FACT_SHEET.keys())}."
        )
        
    details = FACT_SHEET[match_key]
    output = f"Target Name: {details['name']}\nType: {details['type']}\nDescription: {details['description']}\n"
    if details['type'] == "Spacecraft":
        output += (
            f"Launch Date: {details.get('launch_date')}\n"
            f"Mission Status: {details.get('mission_status')}\n"
            f"Notable Discoveries: {details.get('notable_discoveries')}\n"
        )
    else:
        output += (
            f"Orbital Period: {details.get('orbit_period')}\n"
            f"Distance from Sun: {details.get('distance_from_sun')}\n"
            f"Gravity: {details.get('gravity')}\n"
            f"Moons: {details.get('moons')}\n"
        )
    output += f"NASA Eyes Simulation Key: {details['nasa_eyes_key']}"
    return output

if __name__ == "__main__":
    mcp.run()
