async def test_forgot_verify_reset_password_flow(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "reset@example.com", "password": "OldPass123"},
    )

    forgot_response = await client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
    assert forgot_response.status_code == 200

    code = client.otp_sender.sent["reset@example.com"]

    verify_response = await client.post(
        "/api/v1/auth/verify-otp", json={"email": "reset@example.com", "code": code}
    )
    assert verify_response.status_code == 200
    reset_token = verify_response.json()["reset_token"]

    reset_response = await client.post(
        "/api/v1/auth/reset-password",
        json={"reset_token": reset_token, "new_password": "NewPass456"},
    )
    assert reset_response.status_code == 200

    old_login = await client.post(
        "/api/v1/auth/login", data={"username": "reset@example.com", "password": "OldPass123"}
    )
    assert old_login.status_code == 401

    new_login = await client.post(
        "/api/v1/auth/login", data={"username": "reset@example.com", "password": "NewPass456"}
    )
    assert new_login.status_code == 200


async def test_verify_otp_with_wrong_code_fails(client):
    await client.post(
        "/api/v1/auth/register", json={"email": "wrongcode@example.com", "password": "OldPass123"}
    )
    await client.post("/api/v1/auth/forgot-password", json={"email": "wrongcode@example.com"})

    response = await client.post(
        "/api/v1/auth/verify-otp", json={"email": "wrongcode@example.com", "code": "000000"}
    )
    assert response.status_code == 400


async def test_forgot_password_for_unknown_email_returns_generic_message(client):
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})
    assert response.status_code == 200
    assert "nobody@example.com" not in client.otp_sender.sent
