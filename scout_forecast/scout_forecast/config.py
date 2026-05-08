# config.py
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:12345678@127.0.0.1:5432/New_DWw")