from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator

from utils import get_value_by_key


class FilmWork(BaseModel):
    id: str
    title: str
    description: Optional[str]
    rating: Optional[float]
    genres: Optional[List[dict]]
    actors: Optional[List[dict]]
    directors: Optional[List[dict]]
    writers: Optional[List[dict]]
    update_time: datetime
    writers_names: Optional[str]
    actors_names: Optional[str]
    directors_names: Optional[str]
    genres_names: Optional[str]

    @validator("writers_names", always=True)
    def get_writers_names(cls, v, values):
        return v or get_value_by_key("full_name", values["writers"])

    @validator("actors_names", always=True)
    def get_actors_names(cls, v, values):
        return v or get_value_by_key("full_name", values["actors"])

    @validator("directors_names", always=True)
    def get_directors_names(cls, v, values):
        return v or get_value_by_key("full_name", values["directors"])

    @validator("genres_names", always=True)
    def get_genres_names(cls, v, values):
        return v or get_value_by_key("name", values["genres"])
