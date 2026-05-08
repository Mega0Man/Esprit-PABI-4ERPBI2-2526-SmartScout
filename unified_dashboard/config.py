import os
from dotenv import load_dotenv
load_dotenv()

# API URLs for each project
API_URLS = {
    "scout_forecast": os.getenv("SCOUT_FORECAST_API_URL", "http://localhost:8001"),
    "annomalie": os.getenv("ANNOMALIE_API_URL", "http://localhost:8004"),
    "classification": os.getenv("CLASSIFICATION_API_URL", "http://localhost:8005"),
    "recommandation": os.getenv("RECOMMANDATION_API_URL", "http://localhost:8006")
}
