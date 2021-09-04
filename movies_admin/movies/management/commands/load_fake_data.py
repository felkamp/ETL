import logging
from math import ceil
from random import choice, randint, sample

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from progress.bar import IncrementalBar

from movies.factories import (FilmWorkFactory, GenreFactory, PersonFactory,
                              UserFactory)
from movies.models import FilmWork, FilmWorkType, Genre, Person, Role

USERS_COUNT = 1000
PERSONS_COUNT = 10000
GENRES_COUNT = 10000
MOVIES_COUNT = 1000000
SERIALS_COUNT = 300000
CHUNK_SIZE = 10000
MAX_GENRES_NUMBER = 4
MAX_PERSONS_NUMBER = 10

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_users() -> None:
    """Генерация пользователей."""
    logger.info("start generate users...")
    User.objects.bulk_create(UserFactory.build_batch(USERS_COUNT))
    logger.info("completed")


def generate_genres() -> list:
    """Генерация жанров."""

    logger.info("start generate genres...")
    genres = GenreFactory.build_batch(GENRES_COUNT)
    Genre.objects.bulk_create(genres)
    logger.info("completed")
    return genres


def generate_persons() -> list:
    """Генерация персон."""

    logger.info("start generate persons...")
    persons = PersonFactory.build_batch(PERSONS_COUNT)
    Person.objects.bulk_create(persons)
    logger.info("completed")
    return persons


def generate_film_works(genres: list, persons: list, type: FilmWorkType) -> None:
    """Генерация кинопроизведений."""

    film_works_count = MOVIES_COUNT if type == FilmWorkType.MOVIE else SERIALS_COUNT
    iterations_number = ceil(film_works_count / CHUNK_SIZE)
    roles = list(Role)
    bar = IncrementalBar("processing", max=iterations_number, suffix="%(percent)d%%")
    logger.info("start generate film works (type: %s)...", type)
    for _ in range(iterations_number):
        film_works = FilmWorkFactory.build_batch(CHUNK_SIZE, type=type)
        FilmWork.objects.bulk_create(film_works)
        genres_objects = []
        persons_objects = []
        for film_work in film_works:
            film_work_genres = sample(genres, randint(1, MAX_GENRES_NUMBER))
            film_work_persons = sample(persons, randint(1, MAX_PERSONS_NUMBER))
            genres_objects.extend(
                [
                    FilmWork.genres.through(genre_id=genre.id, film_work_id=film_work.id)
                    for genre in film_work_genres
                ]
            )
            persons_objects.extend(
                [
                    FilmWork.persons.through(
                        person_id=person.id,
                        film_work_id=film_work.id,
                        role=choice(roles),
                    )
                    for person in film_work_persons
                ]
            )
        FilmWork.genres.through.objects.bulk_create(genres_objects)
        FilmWork.persons.through.objects.bulk_create(persons_objects)
        bar.next()


class Command(BaseCommand):
    help = "Generate and save data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        generate_users()
        genres = generate_genres()
        persons = generate_persons()
        generate_film_works(genres, persons, FilmWorkType.SERIAL)
        generate_film_works(genres, persons, FilmWorkType.MOVIE)
        logger.info("saving...")
