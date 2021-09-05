import json
import os
import pickle
import sched
import time

import redis
import requests
from dotenv import load_dotenv
from psycopg2 import InterfaceError, OperationalError
from requests.exceptions import ConnectionError

from database import Database
from loggers import logger
from schemas import FilmWork
from sql_queries import get_movies_query
from utils import backoff, coroutine, get_update_time

load_dotenv(".env")
schedule = sched.scheduler(time.time, time.sleep)
TIME_REPEAT = int(os.environ.get("TIME_REPEAT")) or 60


class ESLoader:
    def __init__(self, url, index_name, redis_client):
        self.url = url
        self.index_name = index_name
        self.redis_client = redis_client

    @backoff(ConnectionError)
    def bulk(self, data):
        url = self.url + "/_bulk"
        headers = {"Content-type": "application/json"}
        logger.info("Отправка данных в elastic search")
        res = requests.post(url, data=data.encode("utf-8"), headers=headers).json()
        if res.get("errors"):
            logger.error("При отправке возникли ошибки")
        else:
            logger.info("Данные загружены")

    def load_to_es(self, film_works, update_redis_data=True):
        if update_redis_data:
            self.redis_client.set("data", pickle.dumps(film_works))
        data = self._precess_data(film_works)
        self.bulk(data)
        self.update_redis_info(film_works[-1].update_time.isoformat())

    def _precess_data(self, film_works):
        data = ""
        for film_work in film_works:
            data += (
                    json.dumps({"index": {"_index": self.index_name, "_id": film_work.id}})
                    + "\n"
            )
            data += film_work.json(ensure_ascii=False, exclude={"update_time"}) + "\n"
        return data

    def update_redis_info(self, update_time):
        self.redis_client.set("data", "")
        self.redis_client.set("update_time", update_time)


class ETL:
    def __init__(
            self, db, es_loader, redis_client, postgres_limit=100, es_chunk_size=100
    ):
        self.es_loader = es_loader
        self.db = db
        self.redis_client = redis_client
        self.postgres_limit = postgres_limit
        self.es_chunk_size = es_chunk_size

    @backoff((OperationalError, InterfaceError))
    def extract(self, target):
        cur = self.db.cursor
        logger.info("Извлечение данных из базы")
        cur.execute(
            get_movies_query(),
            (get_update_time(self.redis_client), self.postgres_limit),
        )
        logger.info("Обработка данных")
        for row in cur:
            target.send(row)

    @coroutine
    def transform(self, target):
        while row := (yield):
            target.send(FilmWork(**dict(row)))

    @coroutine
    def load(self):
        buf = []
        while v := (yield):
            buf.append(v)
            if len(buf) == self.es_chunk_size:
                self.es_loader.load_to_es(buf)
                buf = []
        if buf:
            self.es_loader.load_to_es(buf)

    def __call__(self, *args, **kwargs):
        load = self.load()
        transform = self.transform(load)
        self.extract(transform)


def main(sc=None):
    redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "127.0.0.1"))
    es_loader = ESLoader(
        url=os.environ.get("ES_LOADER_URL", "http://127.0.0.1:9200"),
        index_name="movies",
        redis_client=redis_client,
    )
    db = Database(
        name=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
    )
    try:
        etl = ETL(db, es_loader, redis_client)
        if data := redis_client.get("data"):
            logger.info("Найдены не загруженные данные, начинаю загрузку")
            es_loader.load_to_es(pickle.loads(data), update_redis_data=False)
        etl()
    finally:
        db.close()
        schedule.enter(TIME_REPEAT, 1, main, (sc,))


if __name__ == "__main__":
    schedule.enter(0, 1, main, (schedule,))
    schedule.run()
