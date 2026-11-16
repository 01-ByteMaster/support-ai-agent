
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
    connect_args={
        "connect_timeout": 10,
    },
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def init_db():
    # Import models before create_all so SQLAlchemy
    # knows about all registered tables.
    from app.models import KnowledgeChunk

    Base.metadata.create_all(bind=engine)
