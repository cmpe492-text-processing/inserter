import os
from dotenv import load_dotenv
import json
import psycopg2


class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.connection = None
        self.create_connection()

    def create_connection(self):
        try:
            connection = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
            self.connection = connection
            print("Connection to PostgreSQL DB successful")
        except Exception as e:
            print(f"The error '{e}' occurred")

    def insert_corpuses(self, corpuses):
        if self.connection is not None:
            cursor = self.connection.cursor()

            query = """
            INSERT INTO corpuses (platform, entry_id, data)
            VALUES (%s, %s, %s::jsonb);
            """

            for corpus in corpuses:
                json_data = json.dumps(corpus, indent=0)
                values = (corpus["platform"], corpus["id"], json_data)
                try:
                    cursor.execute(query, values)
                    print("Query executed successfully")
                except Exception as e:
                    print(f"The error '{e}' occurred")

            self.connection.commit()
            cursor.close()

    def close_connection(self, debug=True):
        if self.connection is not None:
            self.connection.close()
            if debug:
                print("Database connection closed.")
