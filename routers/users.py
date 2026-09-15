from typing import Annotated

from fastapi import APIRouter , Depends , HTTPException , status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostResponse , UserCreate , UserResponse , UserUpdate

router = APIRouter()


# API GET - Retrieve a single user by ID
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")


# API GET - Retrieve all posts by a specific user
@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_post(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    result = await db.execute(
        select(models.Post).options(selectinload(models.Post.author)).where(models.Post.user_id == user_id).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return posts


# API POST - Create a new user in the database
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)] ):
    result = await db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already exists",
        )

    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email already exists",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

# API PATCH - Partially update an existing user by ID
@router.patch("{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    if user_update.username is not None and user_update.username != user.username:
        result = await db.execute(select(models.User).where(models.User.username == user_update.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists")

    if user_update.email is not None and user_update.email != user.email:
        result = await db.execute(select(models.User).where(models.User.email == user_update.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already registered")

    updated_data = user_update.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


# API DELETE - Delete an existing user by ID
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")

    await db.delete(user)
    await db.commit()
