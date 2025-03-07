import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

print(os.getenv("GENAI_API_KEY"))
