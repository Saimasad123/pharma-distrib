import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password
from app.database import get_db
from app.models import (
    Organization,
    OrganizationMember,
    Role,
    User,
)
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def create_slug(company_name: str) -> str:
    """Create a URL-friendly organization slug."""

    slug = company_name.lower().strip()

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        slug,
    )

    slug = slug.strip("-")

    return f"{slug}-{uuid.uuid4().hex[:8]}"


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. Check if email already exists
    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # 2. Create organization
    organization = Organization(
        name=data.company_name,
        slug=create_slug(data.company_name),
    )

    db.add(organization)

    # Flush so organization.id is generated
    await db.flush()

    # 3. Create user
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )

    db.add(user)

    await db.flush()

    # 4. Find or create Admin role
    result = await db.execute(
        select(Role).where(
            Role.name == "Admin"
        )
    )

    admin_role = result.scalar_one_or_none()

    if not admin_role:
        admin_role = Role(
            name="Admin",
            description="Full access to the organization.",
        )

        db.add(admin_role)

        await db.flush()

    # 5. Add user to organization
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role_id=admin_role.id,
    )

    db.add(membership)

    # 6. Commit everything
    await db.commit()

    # 7. Generate JWT
    token = create_access_token(
        subject=str(user.id),
    )

    # 8. Return response
    return RegisterResponse(
        message="Organization and admin account created successfully.",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization_id=organization.id,
            role=admin_role.name,
        ),
        access_token=token,
        token_type="bearer",
    )