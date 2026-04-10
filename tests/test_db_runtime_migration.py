from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

from app.core.db import initialize_database


def test_initialize_database_adds_missing_relationship_base_score_column():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE users (
                    id VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    nickname VARCHAR(50) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    profile_image_url VARCHAR(500)
                )
                """,
            ),
        )
        connection.execute(
            text(
                """
                CREATE TABLE relationships (
                    id VARCHAR(36) PRIMARY KEY,
                    requester_user_id VARCHAR(36) NOT NULL,
                    target_user_id VARCHAR(36) NOT NULL,
                    relationship_type VARCHAR(20) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    created_at DATETIME
                )
                """,
            ),
        )

    initialize_database(target_engine=engine)

    inspector = inspect(engine)
    relationship_columns = {
        column["name"]
        for column in inspector.get_columns("relationships")
    }
    assert "base_score" in relationship_columns
    assert inspector.has_table("daily_compatibilities") is True
    assert inspector.has_table("relationship_activities") is True
