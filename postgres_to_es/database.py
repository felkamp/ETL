import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor

from utils import backoff


class Database:
    def __init__(self, name: str, user: str, password: str, host: str, port: str):
        self.name = name
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port)
        self.connect = self.connect()
        self.cursor = self.connect.cursor(cursor_factory=DictCursor)

    @backoff(OperationalError)
    def connect(self):
        return psycopg2.connect(
            dbname=self.name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def close(self, commit=True):
        if commit:
            self.connect.commit()
        self.cursor.close()
        self.connect.close()
