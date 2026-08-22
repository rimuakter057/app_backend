async def test_login_returns_refresh_token_and_can_be_refreshed(client):
    await client.post("/api/v1/auth/register", json={"email": "refresh@example.com", "password": "secret123"})
    login_response = await client.post(
        "/api/v1/auth/login", data={"username": "refresh@example.com", "password": "secret123"}
    )
    tokens = login_response.json()
    assert "refresh_token" in tokens

    refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # rotation: the old refresh token must no longer work
    reuse_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reuse_response.status_code == 401


async def test_refresh_with_garbage_token_fails(client):
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert response.status_code == 401


async def test_logout_revokes_refresh_token(client):
    await client.post("/api/v1/auth/register", json={"email": "logout@example.com", "password": "secret123"})
    login_response = await client.post(
        "/api/v1/auth/login", data={"username": "logout@example.com", "password": "secret123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    logout_response = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 200

    refresh_response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401
