import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.adapters.storage_client import SignedUploadData
from app.api.deps import get_db
from app.core.db import Base
from app.main import app


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


class FakeStorageClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, str | bool]] = []

    def create_signed_upload_url(
        self,
        file_key: str,
        content_type: str,
        upsert: bool = True,
    ) -> SignedUploadData:
        self.calls.append(
            {
                "file_key": file_key,
                "content_type": content_type,
                "upsert": upsert,
            },
        )
        return SignedUploadData(
            file_key=file_key,
            upload_url=f"https://upload.example.com/{file_key}?token=test-token",
            public_url=f"https://cdn.example.com/{file_key}",
        )


@pytest.fixture()
def fake_storage_client() -> FakeStorageClient:
    return FakeStorageClient()
