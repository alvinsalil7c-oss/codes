import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HUME_API_KEY")

if api_key:
    print("Hume API key found!")
else:
    print("Hume API key NOT found!")