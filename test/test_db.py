from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import User


def test_create_user(session: Session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username="Luis", password="senha", email="luis@email.com"
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == "Luis"))

    assert asdict(user) == {
        "id": 1,
        "username": "Luis",
        "password": "senha",
        "email": "luis@email.com",
        "created_at": time,
    }
