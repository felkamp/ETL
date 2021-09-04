import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Абстрактный класс для полей даты создания и даты обновления."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedModel):
    """Модель жанра."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(_("описание"), blank=True)

    class Meta:
        verbose_name = _("жанр")
        verbose_name_plural = _("жанры")
        db_table = "genre"

    def __str__(self):
        return self.name


class Person(TimeStampedModel):
    """Модель персоны."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(_("полное имя"), max_length=150)

    class Meta:
        verbose_name = _("персона")
        verbose_name_plural = _("персоны")
        db_table = "person"

    def __str__(self):
        return self.full_name


class FilmWorkType(models.TextChoices):
    """Модель для типов кинопроизведения."""

    MOVIE = "movie", _("фильм")
    SERIAL = "serial", _("сериал")


class FilmWork(TimeStampedModel):
    """Модель для кинопроизведения."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    creation_date = models.DateField(_("дата создания фильма"), null=True)
    certificate = models.TextField(_("сертификат"), blank=True)
    file_path = models.FileField(_("файл"), upload_to="film_works/", blank=True)
    rating = models.FloatField(
        _("рейтинг"),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True,
        blank=True,
    )
    type = models.CharField(_("тип"), max_length=20, choices=FilmWorkType.choices)
    genres = models.ManyToManyField(Genre, through="GenreFilmWork", related_name="film_works")
    persons = models.ManyToManyField(Person, through="PersonFilmWork", related_name="film_works")

    class Meta:
        verbose_name = _("кинопроизведение")
        verbose_name_plural = _("кинопроизведения")
        db_table = "film_work"

    def __str__(self):
        return self.title


class Role(models.TextChoices):
    """Модель для ролей."""

    PRODUCER = "producer", _("режиссёр")
    ACTOR = "actor", _("актёр")
    SCREENWRITER = "screenwriter", _("сценарист")


class PersonFilmWork(TimeStampedModel):
    """Модель для связи персоны и кинопроизвдения."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(_("роль"), max_length=20, choices=Role.choices)

    class Meta:
        db_table = "person_film_work"


class GenreFilmWork(TimeStampedModel):
    """Модель для связи жанра и кинопроизвдения."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = "genre_film_work"
