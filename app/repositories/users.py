from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    statement = select(User).where(
        User.email == email
    )

    result = await db.scalar(statement)

    return result


async def create_user(
    db: AsyncSession,
    data: UserCreate,
) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user