from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from src.models import Todo, User


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
        "todos": [],
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session: Session, user: User):
    todo = Todo(
        title="Test todo",
        description="Test description",
        state="draft",
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]


@pytest.mark.asyncio
async def test_create_todo(session: Session, user: User, mock_db_time):
    with mock_db_time(model=Todo) as time:
        todo = Todo(
            title="Test todo",
            description="Test description",
            state="draft",
            user_id=user.id,
        )

        session.add(todo)
        await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        "description": "Test description",
        "id": 1,
        "state": "draft",
        "title": "Test todo",
        "user_id": 1,
        "created_at": time,
        "updated_at": time,
    }


@pytest.mark.asyncio
async def test_create_todo_error(session, user: User):
    todo = Todo(
        title="Test todo",
        description="Test description",
        state="invalid",
        user_id=user.id,
    )

    session.add(todo)

    with pytest.raises(DataError):
        await session.commit()
