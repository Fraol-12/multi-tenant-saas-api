
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.security import get_password_hash, verify_password, create_access_token
from src.dependencies.repository import get_user_repository
from src.repositories.user import UserRepository
from src.schemas.user import UserCreate, UserRead
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository),
    session: AsyncSession = Depends(get_db),  
):
    existing = await user_repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user_in.password)

    created_user = await user_repo.create(
        email=user_in.email,
        password_hash=hashed_password,
        username=user_in.username,
    )

    await session.commit()          
    await session.refresh(created_user)

    return created_user


@router.post("/login", response_model=dict)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    OAuth2 compatible token login.
    Returns JWT access token.
    """
    user = await user_repo.get_by_email(form_data.username)  # username = email in form
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id,
        expires_delta=None,  # uses default from settings
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }