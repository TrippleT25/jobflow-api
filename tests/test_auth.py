import pytest


@pytest.mark.asyncio
async def test_register_login_and_get_current_user(
    client,
    use_real_auth,
):
    credentials = {
        "email": "auth-user@example.com",
        "password": "SecurePass123!",
    }

    register_response = await client.post(
        "/auth/register",
        json=credentials,
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == credentials["email"]

    login_response = await client.post(
        "/auth/login",
        data={
            "username": credentials["email"],
            "password": credentials["password"],
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == credentials["email"]


@pytest.mark.asyncio
async def test_duplicate_registration_returns_conflict(
    client,
    use_real_auth,
):
    credentials = {
        "email": "duplicate@example.com",
        "password": "SecurePass123!",
    }

    first_response = await client.post(
        "/auth/register",
        json=credentials,
    )
    second_response = await client.post(
        "/auth/register",
        json=credentials,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
