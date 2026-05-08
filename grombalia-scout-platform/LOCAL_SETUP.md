# Local Setup (without Docker)

Follow these steps to run the application locally.

## Prerequisites
- Python 3.10+
- Node.js 20+ & npm

---

## Step 1: Set up Backend

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd grombalia-scout-platform/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Mac/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Start the backend server:
   ```bash
   python main.py
   ```

   Backend will be available at: http://localhost:8000
   API Docs: http://localhost:8000/docs

---

## Step 2: Set up Frontend

1. Open a **new terminal** and navigate to the frontend directory:
   ```bash
   cd grombalia-scout-platform/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the frontend server:
   ```bash
   npm start
   ```

   Frontend will be available at: http://localhost:4200

---

## Demo Credentials

| Role          | Username      | Password |
|---------------|---------------|----------|
| Group Leader  | group_leader  | password |
| Treasurer     | treasurer     | password |
| Unit Leader   | unit_leader   | password |

---

## Optional: MLflow, Prometheus, Grafana

To run MLflow, Prometheus, and Grafana, you can install them locally or use Docker for just those services.
