import MySQLdb

try:
    # Connect as root
    db = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
    cursor = db.cursor()
    
    # Create user if not exists and set password
    try:
        cursor.execute("CREATE USER IF NOT EXISTS 'sneha'@'localhost' IDENTIFIED BY 'Admin@2008'")
    except Exception as e:
        print(f"User creation warning: {e}")

    # Set password explicitly
    cursor.execute("ALTER USER 'sneha'@'localhost' IDENTIFIED BY 'Admin@2008'")
        
    # Grant privileges
    cursor.execute("GRANT ALL PRIVILEGES ON `digital lib system`.* TO 'sneha'@'localhost'")
    cursor.execute("FLUSH PRIVILEGES")
    
    print("User 'sneha' password reset and privileges granted.")
    db.close()
    
except Exception as e:
    print(f"Error: {e}")
