import mysql.connector
from mysql.connector import Error
from app.config import settings

class Database:
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    autocommit=True
                )
                print("✅ Database connected successfully!")
            return self.connection
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return None
    
    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
            print("✅ Database connection closed")

# Global database instance
db = Database()