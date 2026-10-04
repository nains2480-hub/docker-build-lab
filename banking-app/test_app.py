from app import app


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"MyBank" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data