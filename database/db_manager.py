import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from config import DatabaseConfig

class DatabaseManager:
    __connection = None

    @classmethod
    def get_connection(cls):
        """Get or create a database connection"""
        if cls.__connection is None or not cls.__connection.is_connected():
            try:
                cls.__connection = mysql.connector.connect(
                    host=DatabaseConfig.HOST,
                    port=DatabaseConfig.PORT,
                    user=DatabaseConfig.USER,
                    password=DatabaseConfig.PASSWORD,
                    database=DatabaseConfig.DATABASE
                )
                print("Database connection established")
            except Error as e:
                print(f"Error connecting to database: {e}")
                raise ConnectionError("Could not connect to database")
        return cls.__connection

    @classmethod
    def close_connection(cls):
        """Close the database connection"""
        if cls.__connection and cls.__connection.is_connected():
            cls.__connection.close()
            print("Database connection closed")

    
    @classmethod
    @contextmanager
    def get_cursor(cls,dictionary=True):
        """Context manager for database cursor"""
        connection = cls.get_connection()
        cursor = connection.cursor(dictionary=dictionary)
        try:
            yield cursor
            connection.commit()
        except Error as e:
            connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            cursor.close()