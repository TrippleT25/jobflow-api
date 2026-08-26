import pytest


async def create_vacancy(client) -> int:
    response = await client.post(
        "/vacancies",
        json={
            "title": "Python Backend Developer",
            "company": "Example Tech",
        },
    )

    return response.json()["id"]


@pytest.mark.asyncio
async def test_create_application(client):
    vacancy_id = await create_vacancy(client)

    response = await client.post(
        "/applications",
        json={
            "vacancy_id": vacancy_id,
            "notes": "Applied through careers page",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "NEW"


@pytest.mark.asyncio
async def test_application_status_transition(client):
    vacancy_id = await create_vacancy(client)

    create_response = await client.post(
        "/applications",
        json={
            "vacancy_id": vacancy_id,
        },
    )

    application_id = create_response.json()["id"]

    response = await client.patch(
        f"/applications/{application_id}/status",
        json={
            "status": "APPLIED",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPLIED"


@pytest.mark.asyncio
async def test_invalid_application_transition(client):
    vacancy_id = await create_vacancy(client)

    create_response = await client.post(
        "/applications",
        json={
            "vacancy_id": vacancy_id,
        },
    )

    application_id = create_response.json()["id"]

    response = await client.patch(
        f"/applications/{application_id}/status",
        json={
            "status": "OFFER",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_full_application_pipeline(client):
    vacancy_id = await create_vacancy(client)

    response = await client.post(
        "/applications",
        json={
            "vacancy_id": vacancy_id,
        },
    )

    application_id = response.json()["id"]

    transitions = [
        "APPLIED",
        "HR_SCREEN",
        "TECH_INTERVIEW",
        "FINAL_INTERVIEW",
        "OFFER",
    ]

    for new_status in transitions:
        response = await client.patch(
            f"/applications/{application_id}/status",
            json={
                "status": new_status,
            },
        )

        assert response.status_code == 200
        assert response.json()["status"] == new_status


@pytest.mark.asyncio
async def test_offer_is_terminal_status(client):
    vacancy_id = await create_vacancy(client)

    create_response = await client.post(
        "/applications",
        json={
            "vacancy_id": vacancy_id,
        },
    )

    application_id = create_response.json()["id"]

    for new_status in [
        "APPLIED",
        "HR_SCREEN",
        "TECH_INTERVIEW",
        "OFFER",
    ]:
        response = await client.patch(
            f"/applications/{application_id}/status",
            json={
                "status": new_status,
            },
        )

        assert response.status_code == 200

    response = await client.patch(
        f"/applications/{application_id}/status",
        json={
            "status": "REJECTED",
        },
    )

    assert response.status_code == 409
