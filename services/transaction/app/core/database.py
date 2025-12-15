from sqlmodel import SQLModel, create_engine, Session
from .config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,
)


def get_session():
    with Session(engine) as session:
        yield session
