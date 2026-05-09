from flask import Flask, request, render_template, session
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = "scout_recommendation_secret"

API_URL = os.getenv("API_URL", "http://localhost:8006")

# Load translations
with open("../../translations.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)["recommendation"]


@app.route('/', methods=['GET', 'POST'])
def home():
    # Handle language toggle
    lang = request.args.get('lang')
    if lang in ['en', 'fr', 'ar']:
        session['lang'] = lang
    
    current_lang = session.get('lang', 'en')
    t = TRANSLATIONS[current_lang]

    result = None
    value = None
    recs = []
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            # The FastAPI RecommendationRequest expects 'user_id' not 'scout_id'
            response = requests.post(f"{API_URL}/predict", json={"user_id": int(amount)})
            if response.status_code == 200:
                data = response.json()
                result = "Success"
                value = int(amount)
                # The API returns a list of dicts: [{"activity_name": "...", ...}, ...]
                # Extract just the names for the template
                raw_recs = data["result"]["recommendations"]
                recs = [r["activity_name"] for r in raw_recs]
            else:
                result = f"Error from API: {response.text}"
        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template("index.html", result=result, value=value, recs=recs, t=t, lang=current_lang)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
