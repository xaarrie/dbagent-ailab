import os
import urllib.request

import duckdb

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
PARQUET_FILE = "yellow_tripdata_2024-01.parquet"

con = duckdb.connect("taxi.db")


def setup_database():
    """Download the parquet file and load it into DuckDB."""
    if not os.path.exists(PARQUET_FILE):
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, PARQUET_FILE)

    con.execute(f"""
        CREATE TABLE IF NOT EXISTS trips AS
        SELECT * FROM '{PARQUET_FILE}'
    """)
    count = con.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
    print(f"Loaded {count} rows")
    return count


class SQLTools:
    """
    Run queries against the shared DuckDB connection.
    """

    def get_schema(self)->str:
        """
        Return the trips table's column names and types.
        Returns:
          str: column names and their types
        """
        columns = con.execute("DESCRIBE trips").fetchall()
        return "\n".join(f"{name}: {column_type}" for name, column_type, *_ in columns)

    def run_sql(self,query:str)->str:
        """
        Execute a query and format its headers and up to 50 result rows.
        Args:
           query (str): The search query to look up in the database.
        Returns:
            str: returns results as text (column headers + datarows), limited to 50 rows
        """
        cursor = con.execute(query)
        headers = [description[0] for description in cursor.description or []]
        rows = cursor.fetchmany(50) if headers else []
        lines = ["\t".join(headers)]
        lines.extend("\t".join(str(value) for value in row) for row in rows)
        return "\n".join(lines)
