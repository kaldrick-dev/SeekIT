import mysql.connector
from mysql.connector import Error
from config import DatabaseConfig
import os

def execute_schema():
    """Execute the schema.sql file to create database tables"""

    # First, connect without specifying database to create it
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD
        )
        cursor = connection.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DatabaseConfig.DATABASE}")
        print(f"Database '{DatabaseConfig.DATABASE}' created")

        # Switch to the database
        cursor.execute(f"USE {DatabaseConfig.DATABASE}")

        # Read and execute schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as schema_file:
            schema_sql = schema_file.read()

        # Split by semicolon and execute each statement
        statements = schema_sql.split(';')

        for statement in statements:
            statement = statement.strip()
            if statement:  # Skip empty statements
                cursor.execute(statement)

        connection.commit()
        print("Schema executed successfully!")
        print("All tables created")

    except Error as e:
        print(f"✗ Error: {e}")
        raise

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    print("Initializing SeekIT Database...")
    execute_schema()
