import pytest
from app import app, db, Restaurant


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
    client = app.test_client()
    yield client
    with app.app_context():
        db.drop_all()


def test_restaurant_flow(client):
    res = client.post(
        "/restaurants",
        json={"name": "Cafe", "cuisine": "Turkish", "location": "Center"},
    )
    assert res.status_code == 201
    rid = res.get_json()["id"]

    res = client.get("/restaurants")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1

    res = client.get("/restaurants?cuisine=Turkish")
    assert res.status_code == 200
    assert len(res.get_json()) == 1

    res = client.get("/restaurants?cuisine=Italian")
    assert res.status_code == 200
    assert res.get_json() == []

    res = client.post(
        f"/restaurants/{rid}/comments", json={"author": "John", "content": "Nice!"}
    )
    assert res.status_code == 201

    res = client.get(f"/restaurants/{rid}/comments")
    assert res.status_code == 200
    comments = res.get_json()
    assert len(comments) == 1
    assert comments[0]["author"] == "John"
