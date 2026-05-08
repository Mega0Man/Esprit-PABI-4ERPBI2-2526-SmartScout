from flask import Flask, request, render_template
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8005")


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
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
                pred_class=data["result"]["prediction_class"]
            )
        else:
            return render_template(
                "index.html",
                prediction="API Error"
            )

    except Exception as e:
        return render_template(
            "index.html",
            prediction=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    app.run(debug=True, port=5002)