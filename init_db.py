import os
import sys
from dotenv import load_dotenv

# Add the api directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from database import create_tables

def init_database():
    """
    Initialize the database by creating all tables
    """
    print("Initializing database...")
    create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    load_dotenv()
    init_database()