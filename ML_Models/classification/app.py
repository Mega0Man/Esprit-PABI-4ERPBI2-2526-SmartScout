from flask import Flask, request, render_template, session
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = "scout_retention_secret"

API_URL = os.getenv("API_URL", "http://localhost:8005")

# Load translations
with open("../../translations.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)["retention"]


@app.route('/')
def home():
    # Handle language toggle
    lang = request.args.get('lang')
    if lang in ['en', 'fr', 'ar']:
        session['lang'] = lang
    
    current_lang = session.get('lang', 'en')
    t = TRANSLATIONS[current_lang]
    return render_template("index.html", t=t, lang=current_lang)


@app.route('/predict', methods=['POST'])
def predict():
    current_lang = session.get('lang', 'en')
    t = TRANSLATIONS[current_lang]
    try:
        nb_members = float(request.form['nb_members'])
        nb_leaders = float(request.form['nb_leaders'])
        taux_evolution = float(request.form['taux_evolution'])

        response = requests.post(f"{API_URL}/predict", json={
            "nb_members": nb_members,
            "nb_leaders": nb_leaders,
            "taux_evolution": taux_evolution
        })
        
        if response.status_code == 200:
            data = response.json()
            return render_template(
                "index.html",
                prediction=data["result"]["prediction"],
                confidence=data["result"]["confidence"],
                pred_class=data["result"]["prediction_class"],
                t=t,
                lang=current_lang
            )
        else:
            return render_template(
                "index.html",
                prediction="API Error",
                t=t,
                lang=current_lang
            )

    except Exception as e:
        return render_template(
            "index.html",
            prediction=f"Error: {str(e)}",
            t=t,
            lang=current_lang
        )


if __name__ == "__main__":
    app.run(debug=True, port=5002)