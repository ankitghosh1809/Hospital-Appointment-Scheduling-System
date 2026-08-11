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

# The app has no per-user timezone concept - one hospital, one local clock.
# India doesn't observe DST, so a fixed UTC+5:30 offset is exact (and needs
# no system tzdata, unlike zoneinfo - important since the server/serverless
# runtime this runs on is typically UTC, not IST).
import datetime
HOSPITAL_TZ = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
