import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DB_CONFIG = DATABASE_URL

EMAIL_CONFIG = {
    "host": os.getenv("EMAIL_HOST", "smtp.gmail.com"),
    "port": int(os.getenv("EMAIL_PORT", 587)),
    "user": os.getenv("EMAIL_USER", ""),
    "password": os.getenv("EMAIL_PASSWORD", ""),
}

DEFAULT_FEE = float(os.getenv("DEFAULT_FEE", 500))
