async def test_duplicate_register_returns_structured_error(client):
    payload = {"email": "dup@example.com", "password": "secret123"}
    await client.post("/api/v1/auth/register", json=payload)

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "USER_ALREADY_EXISTS"
    assert "dup@example.com" in body["error"]["message"]


async def test_wrong_login_returns_structured_error(client):
    response = await client.post(
        "/api/v1/auth/login", data={"username": "nobody@example.com", "password": "whatever"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_unknown_user_returns_structured_404(client):
    response = await client.get("/api/v1/users/999999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


async def test_missing_field_returns_structured_validation_error(client):
    response = await client.post("/api/v1/auth/register", json={"email": "novalidpass@example.com"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
    assert len(body["error"]["details"]) > 0


async def test_missing_auth_token_returns_structured_401(client):
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] in {"UNAUTHORIZED", "INVALID_TOKEN"}
