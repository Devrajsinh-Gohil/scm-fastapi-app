import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai"
)