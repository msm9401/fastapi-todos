from database.orm import ToDo


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_get_todos(client, mocker):
    # order=ASC
    mocker.patch(
        "main.get_todos",
        return_value=[
            ToDo(id=1, contents="FastAPI Section 0", is_done=True),
            ToDo(id=2, contents="FastAPI Section 1", is_done=False),
        ],
    )

    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
        ]
    }

    # order=DESC
    response = client.get("/todos?order=DESC")
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
        ]
    }


def test_get_todo(client, mocker):
    # 200
    mocker.patch(
        "main.get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )

    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}

    # 400
    mocker.patch("main.get_todo_by_todo_id", return_value=None)

    response = client.get("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}


def test_create_todo(client, mocker):
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch(
        "main.create_todo",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )

    body = {
        "contents": "test",
        "is_done": False,
    }

    response = client.post("/todos", json=body)

    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == "test"
    assert create_spy.spy_return.is_done is False

    assert response.status_code == 201
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}