import pytest


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_vacancy(
    client,
    act_as_user,
):
    create_response = await client.post(
        "/vacancies",
        json={
            "title": "Private Python Vacancy",
            "company": "Owner One",
        },
    )
    vacancy_id = create_response.json()["id"]

    register_response = await client.post(
        "/auth/register",
        json={
            "email": "second-owner@example.com",
            "password": "SecurePass123!",
        },
    )
    second_user = register_response.json()
    act_as_user(second_user["id"], second_user["email"])

    list_response = await client.get("/vacancies")
    get_response = await client.get(f"/vacancies/{vacancy_id}")
    patch_response = await client.patch(
        f"/vacancies/{vacancy_id}",
        json={"title": "Stolen Vacancy"},
    )
    delete_response = await client.delete(
        f"/vacancies/{vacancy_id}"
    )

    assert list_response.status_code == 200
    assert list_response.json()["items"] == []
    assert list_response.json()["total"] == 0
    assert get_response.status_code == 404
    assert patch_response.status_code == 404
    assert delete_response.status_code == 404
