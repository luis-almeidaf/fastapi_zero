from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import User


@pytest.mark.asyncio
async def test_create_user(session: Session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="Luis", password="senha", email="luis@email.com"
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == "Luis"))

    assert asdict(user) == {
        "id": 1,
        "username": "Luis",
        "password": "senha",
        "email": "luis@email.com",
        "created_at": time,
        "updated_at": time,
    }
