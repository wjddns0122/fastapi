from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def initialize_database(target_engine: Engine | None = None) -> None:
    current_engine = target_engine or engine
    Base.metadata.create_all(bind=current_engine)
    apply_runtime_migrations(target_engine=current_engine)


def apply_runtime_migrations(target_engine: Engine | None = None) -> None:
    current_engine = target_engine or engine

    # inspector를 각 마이그레이션 직전에 새로 생성하여 stale 스냅샷 문제 방지
    _ensure_column_exists(
        target_engine=current_engine,
        inspector=inspect(current_engine),
        table_name="relationships",
        column_name="base_score",
        column_sql="INTEGER",
    )


def _ensure_column_exists(
    target_engine: Engine,
    inspector,
    table_name: str,
    column_name: str,
    column_sql: str,
) -> None:
    if not inspector.has_table(table_name):
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }
    if column_name in existing_columns:
        return

    with target_engine.begin() as connection:
        connection.execute(
            text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"),
        )
