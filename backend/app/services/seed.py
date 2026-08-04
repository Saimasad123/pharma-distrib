import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database import AsyncSessionLocal, Base, engine
from app.models import Organization, OrganizationMember, Role, User


async def ensure_demo_account() -> bool:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "admin@pharmadistrib.com"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return False

        organization = Organization(name="Demo Pharma", slug="demo-pharma")
        session.add(organization)
        await session.flush()

        role = await session.scalar(select(Role).where(Role.name == "Admin"))
        if role is None:
            role = Role(name="Admin", description="Full access to the organization.")
            session.add(role)
            await session.flush()

        user = User(
            id=uuid.uuid4(),
            email="admin@pharmadistrib.com",
            hashed_password=hash_password("admin123"),
            full_name="Demo Admin",
            is_verified=True,
        )
        session.add(user)
        await session.flush()

        session.add(
            OrganizationMember(
                organization_id=organization.id,
                user_id=user.id,
                role_id=role.id,
            )
        )

        await session.commit()
        return True
