from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_session
from app.infrastructure.services.otp_sender import OtpSender
from app.main import app
from app.presentation.api.deps import get_otp_sender

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class FakeOtpSender(OtpSender):
    """Captures sent OTPs so tests can read the code instead of a real inbox."""

    def __init__(self):
        self.sent: dict[str, str] = {}

    async def send(self, email: str, code: str) -> None:
        self.sent[email] = code


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    otp_sender = FakeOtpSender()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_otp_sender] = lambda: otp_sender

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.otp_sender = otp_sender
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
