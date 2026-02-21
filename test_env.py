from dotenv import load_dotenv
import os

load_dotenv()
db_name = os.getenv('DB_NAME')
print(f"RAW DB_NAME: '{db_name}'")
