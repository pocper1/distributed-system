import psycopg2
import os

try:
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_NAME"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )
    print("PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")