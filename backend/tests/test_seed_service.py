import asyncio
import os
import sys
from pathlib import Path


def test_ensure_demo_account_creates_default_admin(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["SECRET_KEY"] = "test-secret-key"

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from app.database import Base, engine
    from app.services.seed import ensure_demo_account

    async def run_checks():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        created_first_time = await ensure_demo_account()
        created_second_time = await ensure_demo_account()

        assert created_first_time is True
        assert created_second_time is False

    asyncio.run(run_checks())
