from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8004")


@app.route("/", methods=["GET", "POST"])
def index():
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

    return render_template("index.html", result=result, value=value, lower=lower, upper=upper)


if __name__ == "__main__":
    app.run(debug=True, port=5004)