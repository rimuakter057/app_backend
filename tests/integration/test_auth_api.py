async def test_register_login_and_read_current_user(client):
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "secret123", "full_name": "Test User"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "user@example.com"

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"


async def test_login_with_wrong_password_fails(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "user2@example.com", "password": "secret123"},
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "user2@example.com", "password": "wrong-password"},
    )
    assert login_response.status_code == 401
