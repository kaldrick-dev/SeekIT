import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    HOST = os.getenv('DB_HOST','localhost')
    PORT = int(os.getenv('DB_PORT',3306))
    USER = os.getenv('DB_USER','root')
    PASSWORD = os.getenv('DB_PASS','')
    DATABASE = os.getenv('DB_NAME','SeekIT')
    
