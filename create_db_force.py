import MySQLdb

try:
    # Connect as root to create DB
    db = MySQLdb.connect(host='mysql.railway.internal', user='root', passwd='TnrmYuHKRLkiCNEXvDguSSGfQyOHRTRq', port=3306)
    cursor = db.cursor()
    
    # Force creation with backticks
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS `digital lib system` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("Database 'Digital Lib System' created.")
    except Exception as e:
        print(f"Creation error: {e}")
        
    # Verify
    cursor.execute("SHOW DATABASES")
    dbs = cursor.fetchall()
    print("Databases:", dbs)
    
    # Grant rights again just in case
    cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'sneha'@'localhost' WITH GRANT OPTION")
    cursor.execute("FLUSH PRIVILEGES")
    
    db.close()
except Exception as e:
    print(f"Error: {e}")
