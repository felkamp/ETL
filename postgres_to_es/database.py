import psycopg2
from psycopg2 import InterfaceError, OperationalError
from psycopg2.extras import DictCursor

from utils import backoff


class Cursor:
    def __init__(self, connect):
        self.cursor = connect.cursor(cursor_factory=DictCursor)
        self._connection = connect

    @backoff((OperationalError, InterfaceError))
    def execute(self, *args, **kwargs):
        self.cursor.execute(*args, **kwargs)

    def fetchone(self, *args, **kwargs):
        return self.cursor.fetchone(*args, **kwargs)

    def close(self, *args, **kwargs):
        return self.cursor.close(*args, **kwargs)


class Database:
    def __init__(self, name: str, user: str, password: str, host: str, port: str):
        self.name = name
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port)
        self.connect = self.connect()
        self.cursor = Cursor(self.connect)

    @backoff(OperationalError)
    def connect(self):
        return psycopg2.connect(
            dbname=self.name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def _get_cursor(self):
        return self.connect.cursor()

    def close(self, commit=True):
        if commit:
            self.connect.commit()
        self.cursor.close()
        self.connect.close()
