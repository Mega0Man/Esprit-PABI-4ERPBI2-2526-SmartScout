from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8006")


@app.route("/", methods=["GET", "POST"])
def index():
    result, value, recs = None, None, []

    if request.method == "POST":
        try:
            value = int(request.form["amount"])
            user_id = value

            response = requests.post(f"{API_URL}/predict", json={"user_id": user_id})
            if response.status_code == 200:
                data = response.json()
                result = "Top Recommendations"
                for rec in data["result"]["recommendations"]:
                    recs.append(f"Activity {rec['activity_id']} ({rec['activity_name']}) → {rec['score']:.2f}")
            else:
                result = "API Error"

        except Exception as e:
            result = f"Input Error: {e}"

    return render_template("index.html", result=result, value=value, recs=recs)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
