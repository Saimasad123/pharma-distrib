import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

try:
    from jose import JWTError, jwt
except ModuleNotFoundError:  # pragma: no cover - fallback for Debian/Ubuntu package environments
    import jwt as _jwt

    class JWTError(Exception):
        pass

    jwt = _jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models import (
    Organization,
    OrganizationMember,
    Role,
    User,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

security = HTTPBearer()


def create_slug(company_name: str) -> str:
    """Create a unique URL-friendly organization slug."""

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
    # Check if email already exists
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

    # Create organization
    organization = Organization(
        name=data.company_name,
        slug=create_slug(data.company_name),
    )

    db.add(organization)

    await db.flush()

    # Create user
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )

    db.add(user)

    await db.flush()

    # Find Admin role
    result = await db.execute(
        select(Role).where(
            Role.name == "Admin"
        )
    )

    admin_role = result.scalar_one_or_none()

    # Create Admin role if it doesn't exist
    if not admin_role:
        admin_role = Role(
            name="Admin",
            description="Full access to the organization.",
        )

        db.add(admin_role)

        await db.flush()

    # Create organization membership
    membership = OrganizationMember(
        organization_id=organization.id,
        user_id=user.id,
        role_id=admin_role.id,
    )

    db.add(membership)

    # Commit transaction
    await db.commit()

    # Generate JWT
    token = create_access_token(
        subject=str(user.id),
    )

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


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    # Find user by email
    result = await db.execute(
        select(User).where(
            User.email == data.email
        )
    )

    user = result.scalar_one_or_none()

    # Don't reveal whether the email exists
    if not user or not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # Generate access token
    token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token.",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # Find authenticated user
    result = await db.execute(
        select(User).where(
            User.id == uuid.UUID(user_id)
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return user


async def get_current_user_context(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the currently authenticated user and
    their organization ID.
    """

    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id
            == current_user.id
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization membership not found.",
        )

    return current_user, membership.organization_id


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):
    # Get user's organization membership
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id
            == current_user.id
        )
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization membership not found.",
        )

    # Get role
    result = await db.execute(
        select(Role).where(
            Role.id == membership.role_id
        )
    )

    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User role not found.",
        )

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        organization_id=membership.organization_id,
        role=role.name,
    )