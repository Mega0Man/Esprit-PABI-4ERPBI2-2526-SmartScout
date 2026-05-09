# app.py - Flask Web App integrated with FastAPI
from flask import Flask, render_template, request, jsonify, session
import os
import requests
import json

app = Flask(__name__)
app.secret_key = "scout_secret_key"

API_URL = os.getenv("API_URL", "http://localhost:8001")

# Load translations
with open("../../translations.json", "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)["scout_forecast"]

def _normalize_result(result):
    if not isinstance(result, dict):
        return {}
    normalized = dict(result)
    if "arima_forecast" not in normalized and "forecast" in normalized:
        normalized["arima_forecast"] = normalized["forecast"]
    if "arima_delta" not in normalized and "delta_percent" in normalized:
        normalized["arima_delta"] = normalized["delta_percent"]
    if "best_order" not in normalized and "best_arima_order" in normalized:
        normalized["best_order"] = normalized["best_arima_order"]
    return normalized

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    
    # Handle language toggle
    lang = request.args.get('lang')
    if lang in ['en', 'fr', 'ar']:
        session['lang'] = lang
    
    current_lang = session.get('lang', 'en')
    t = TRANSLATIONS[current_lang]

    if request.method == 'POST':
        unit_id = request.form.get('unit_id') or None
        try:
            unit_id_int = int(unit_id) if unit_id else None
            api_response = requests.post(
                f"{API_URL}/predict/participation",
                json={"unit_id": unit_id_int},
                timeout=60
            )
            if api_response.status_code == 200:
                data = api_response.json()
                result = _normalize_result(data.get("result", {}))
            else:
                error = f"API Error: {api_response.status_code}"
        except requests.exceptions.ConnectionError:
            error = f"Could not connect to API at {API_URL}. Make sure the API is running."
        except Exception as e:
            error = str(e)

    return render_template('index.html', result=result, error=error, t=t, lang=current_lang)

@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    try:
        data = request.get_json()
        unit_id = data.get('unit_id')

        api_response = requests.post(
            f"{API_URL}/predict/participation",
            json={"unit_id": unit_id},
            timeout=60
        )

        if api_response.status_code == 200:
            return jsonify(api_response.json())
        else:
            return jsonify({"status": "error", "message": f"API returned {api_response.status_code}"}), 502

    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "message": "API not available"}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(host=host, port=port, debug=debug)
