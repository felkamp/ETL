from django.contrib.auth.models import User
from factory import Faker, Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyFloat

from movies.models import FilmWork, FilmWorkType, Genre, Person


class UserFactory(DjangoModelFactory):
    """Фабрика для модели пользователь."""

    first_name = Faker("first_name", locale="ru_RU")
    last_name = Faker("last_name", locale="ru_RU")
    email = Sequence(lambda n: "user{}@example.com".format(n))
    username = Sequence(lambda n: "username{}".format(n))

    class Meta:
        model = User


class GenreFactory(DjangoModelFactory):
    """Фабрика для модели жанр."""

    name = Faker("word", locale="ru_RU")

    class Meta:
        model = Genre


class FilmWorkFactory(DjangoModelFactory):
    """Фабрика для модели кинопроизведения."""

    title = Faker("text", max_nb_chars=20, locale="ru_RU")
    creation_date = Faker("date_time")
    description = Faker("paragraph", locale="ru_RU")
    rating = FuzzyFloat(1.0, 10.0, precision=2)
    type = FilmWorkType.MOVIE

    class Meta:
        model = FilmWork


class PersonFactory(DjangoModelFactory):
    """Фабрика для модели персоны."""

    full_name = Faker("name", locale="ru_RU")

    class Meta:
        model = Person
