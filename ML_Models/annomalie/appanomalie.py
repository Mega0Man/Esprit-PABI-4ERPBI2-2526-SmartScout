from flask import Flask, render_template, request, session
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = "scout_anomaly_secret"

API_URL = os.getenv("API_URL", "http://localhost:8004")

# Load translations
with open("../../translations.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)["anomaly"]


@app.route("/", methods=["GET", "POST"])
def index():
    # Handle language toggle
    lang = request.args.get('lang')
    if lang in ['en', 'fr', 'ar']:
        session['lang'] = lang
    
    current_lang = session.get('lang', 'en')
    t = TRANSLATIONS[current_lang]

    result = None
    value = None
    lower = None
    upper = None

    if request.method == "POST":
        try:
            value = float(request.form["amount"])
            response = requests.post(f"{API_URL}/predict", json={"amount": value})
            if response.status_code == 200:
                data = response.json()
                result = data["result"]["classification"]
                lower = data["result"]["lower_bound"]
                upper = data["result"]["upper_bound"]
            else:
                result = "API Error"
        except Exception as e:
            result = f"Error: {str(e)}"

    return render_template("index.html", result=result, value=value, lower=lower, upper=upper, t=t, lang=current_lang)


if __name__ == "__main__":
    app.run(debug=True, port=5004)