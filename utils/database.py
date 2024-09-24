import psycopg2
import configparser

CONFIG_FILE_PATH = 'src/config.ini'  # Path to your config file

class SFNEIpmDatabase:
    def __init__(self):
        self.config = self.load_config()
        self.connection = None
        self.cursor = None

    @staticmethod
    def load_config():
        """Load database configuration from a file."""
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        return config

    def connect(self):
        """Connect to the database using the configuration settings."""
        try:
            self.connection = psycopg2.connect(
                host=self.config['DATABASE']['host'],
                database=self.config['DATABASE']['database'],
                user=self.config['DATABASE']['user'],
                password=self.config['DATABASE']['password']
            )
            self.cursor = self.connection.cursor()
            print("Database connection successful.")
        except psycopg2.DatabaseError as e:
            print(f"Failed to connect to the database: {e}")
            raise

    def commit(self):
        """Commit the current transaction."""
        try:
            if self.connection:
                self.connection.commit()
                print("Transaction committed.")
        except psycopg2.DatabaseError as e:
            print(f"Failed to commit the transaction: {e}")
            raise

    def disconnect(self):
        """Close the cursor and the connection."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                print("Database connection closed.")
        except psycopg2.DatabaseError as e:
            print(f"Failed to disconnect from the database: {e}")
            raise

    # CRUD support methods
    def fetch_all(self, table_name):
        """Fetch all records from a specific table."""
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        except psycopg2.DatabaseError as e:
            print(f"Failed to fetch data from {table_name}: {e}")
            raise

    def insert(self, table_name, columns, values):
        """Insert a new record into a table."""
        try:
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(values))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            self.cursor.execute(query, values)
            self.commit()
            print(f"Record inserted into {table_name}.")
        except psycopg2.DatabaseError as e:
            print(f"Failed to insert data into {table_name}: {e}")
            raise

    def update(self, table_name, update_columns, update_values, where_clause):
        """Update records in a table with a where clause."""
        try:
            set_clause = ", ".join([f"{col} = %s" for col in update_columns])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            self.cursor.execute(query, update_values)
            self.commit()
            print(f"Record(s) updated in {table_name}.")
        except psycopg2.DatabaseError as e:
            print(f"Failed to update data in {table_name}: {e}")
            raise

    def delete(self, table_name, where_clause):
        """Delete records from a table with a where clause."""
        try:
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            self.cursor.execute(query)
            self.commit()
            print(f"Record(s) deleted from {table_name}.")
        except psycopg2.DatabaseError as e:
            print(f"Failed to delete data from {table_name}: {e}")
            raise
