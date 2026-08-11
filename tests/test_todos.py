from http import HTTPStatus

import factory.fuzzy
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker("text")
    description = factory.Faker("text")
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            "/todos/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Todo title",
                "description": "Todo description",
                "state": "draft",
            },
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "title": "Todo title",
        "description": "Todo description",
        "state": "draft",
        "created_at": time.isoformat(),
        "updated_at": time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_all_expected_fields(
    session: AsyncSession, client, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)

    response = client.get(
        "/todos", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.json()["todos"] == [
        {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "state": todo.state,
            "created_at": time.isoformat(),
            "updated_at": time.isoformat(),
        }
    ]


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    session: AsyncSession, client, user, token
):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    response = client.get(
        "/todos", headers={"Authorization": f"Bearer {token}"}
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session: AsyncSession, client, user, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))

    response = client.get(
        "/todos/?offset=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session: AsyncSession, client, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title="Test todo 1")
    )

    response = client.get(
        "/todos/?title=Test todo 1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session: AsyncSession, client, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description="description")
    )

    response = client.get(
        "/todos/?description=description",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session: AsyncSession, client, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    )

    response = client.get(
        "/todos/?state=draft",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session: AsyncSession, client, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title="Test todo combined",
            description="combined description",
            state=TodoState.done,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title="Other title",
            description="other description",
            state=TodoState.todo,
        )
    )

    await session.commit()

    response = client.get(
        "/todos/?title=Test todo combined&description=combined&state=done",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(response.json()["todos"]) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_min_length(client, token):
    search = "a"
    response = client.get(
        f"/todos/?title={search}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_todos_filter_max_length(client, token):
    search = "a" * 21
    response = client.get(
        f"/todos/?title={search}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f"/todos/{todo.id}",
        json={"title": "teste!"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["title"] == "teste!"


def test_patch_todo_error(client, token):
    response = client.patch(
        "/todos/10",
        json={"title": "2"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}


@pytest.mark.asyncio
async def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f"/todos/{todo.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "message": "Task has been deleted successfully."
    }


@pytest.mark.asyncio
async def test_delete_todo_erro(client, token):
    response = client.delete(
        "/todos/10",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Task not found."}
