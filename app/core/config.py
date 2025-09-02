import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Crédito PME API")
API_VERSION = "0.4.0"
