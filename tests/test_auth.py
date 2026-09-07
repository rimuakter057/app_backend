def test_register_and_login(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "password123", "role": "buyer"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "alice@example.com"

    resp = client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "password123"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_cannot_register_as_admin(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Eve", "email": "eve@example.com", "password": "password123", "role": "admin"},
    )
    assert resp.status_code == 403


def test_login_with_wrong_password_fails(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "password123", "role": "buyer"},
    )
    resp = client.post("/api/v1/auth/login", json={"email": "bob@example.com", "password": "wrong"})
    assert resp.status_code == 401
