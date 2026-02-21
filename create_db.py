import MySQLdb
import os
from dotenv import load_dotenv

load_dotenv()

try:
    db = MySQLdb.connect(
        host=os.getenv('DB_HOST', 'mysql.railway.internal'),
        user=os.getenv('DB_USER', 'root'),
        passwd=os.getenv('DB_PASSWORD', 'TnrmYuHKRLkiCNEXvDguSSGfQyOHRTRq'),
        port=int(os.getenv('DB_PORT', 3306))
    )

    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS `digital lib system` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Database 'Digital Lib System' created successfully.")
    db.close()
except Exception as e:
    print(f"Error creating database: {e}")
