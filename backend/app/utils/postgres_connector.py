import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs


class PostgresConnector:
    def __init__(
        self,
        database_url: Optional[str] = None,
        connection_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the PostgresConnector with a DATABASE_URL or connection parameters.

        Args:
            database_url (Optional[str]): The full database URL (e.g., 'postgresql://user:password@host:port/dbname').
            connection_params (Optional[Dict[str, Any]]): A dictionary containing individual connection parameters.
        """
        if not database_url and not connection_params:
            raise ValueError(
                "Either 'database_url' or 'connection_params' must be provided."
            )

        self.database_url = database_url
        self.connection_params = connection_params

    def connect(self):
        """
        Establish a connection to the PostgreSQL database.

        Returns:
            psycopg2.extensions.connection: The database connection object.
        """
        try:
            if self.database_url:
                connection = psycopg2.connect(self.database_url)
            elif self.connection_params:
                connection = psycopg2.connect(**self.connection_params)
            else:
                raise ValueError("No connection method provided.")
            return connection
        except psycopg2.Error as e:
            raise Exception(f"Error connecting to PostgreSQL: {str(e)}")

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return the results as a list of dictionaries.

        Args:
            query (str): The SQL query to execute.
            params (Optional[tuple]): Optional tuple of parameters to pass with the query.

        Returns:
            List[Dict[str, Any]]: The query results as a list of dictionaries.
        """
        try:
            with self.connect() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    if cursor.description:
                        return cursor.fetchall()
                    return []
        except psycopg2.Error as e:
            raise Exception(f"Error executing query: {str(e)}")

    def execute_update(self, query: str, params: Optional[tuple] = None) -> None:
        """
        Execute an update/insert/delete query.

        Args:
            query (str): The SQL query to execute.
            params (Optional[tuple]): Optional tuple of parameters to pass with the query.
        """
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
        except psycopg2.Error as e:
            raise Exception(f"Error executing update: {str(e)}")
