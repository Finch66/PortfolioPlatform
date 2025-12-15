from pydantic import BaseModel
import os


class Settings(BaseModel):
    database_url: str


def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL")
    )
