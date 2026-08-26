import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_vacancy(client):
    response = await client.post(
        "/vacancies",
        json={
            "title": "Python Backend Developer",
            "company": "Example Tech",
            "salary_from": 2000,
            "salary_to": 3000,
            "currency": "EUR",
            "location": "Remote",
            "work_format": "remote",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Python Backend Developer"
    assert data["company"] == "Example Tech"
    assert data["salary_from"] == 2000
    assert data["salary_to"] == 3000


@pytest.mark.asyncio
async def test_invalid_salary_range(client):
    response = await client.post(
        "/vacancies",
        json={
            "title": "Python Developer",
            "company": "Example",
            "salary_from": 4000,
            "salary_to": 2000,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "salary_from cannot be greater than salary_to"
    )


@pytest.mark.asyncio
async def test_get_vacancy(client):
    create_response = await client.post(
        "/vacancies",
        json={
            "title": "Python Developer",
            "company": "Example",
        },
    )

    vacancy_id = create_response.json()["id"]

    response = await client.get(
        f"/vacancies/{vacancy_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == vacancy_id


@pytest.mark.asyncio
async def test_update_vacancy(client):
    create_response = await client.post(
        "/vacancies",
        json={
            "title": "Python Developer",
            "company": "Example",
        },
    )

    vacancy_id = create_response.json()["id"]

    response = await client.patch(
        f"/vacancies/{vacancy_id}",
        json={
            "title": "Senior Python Developer",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Senior Python Developer"


@pytest.mark.asyncio
async def test_delete_vacancy(client):
    create_response = await client.post(
        "/vacancies",
        json={
            "title": "Python Developer",
            "company": "Example",
        },
    )

    vacancy_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/vacancies/{vacancy_id}"
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/vacancies/{vacancy_id}"
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_vacancy_search(client):
    await client.post(
        "/vacancies",
        json={
            "title": "Python Backend Developer",
            "company": "Backend Corp",
        },
    )

    await client.post(
        "/vacancies",
        json={
            "title": "Java Developer",
            "company": "Java Corp",
        },
    )

    response = await client.get(
        "/vacancies?search=python"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert (
        data["items"][0]["title"]
        == "Python Backend Developer"
    )


@pytest.mark.asyncio
async def test_vacancy_pagination(client):
    for index in range(5):
        response = await client.post(
            "/vacancies",
            json={
                "title": f"Python Developer {index}",
                "company": "Example",
            },
        )

        assert response.status_code == 201

    response = await client.get(
        "/vacancies?limit=2&offset=0"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_vacancy_limit_validation(client):
    response = await client.get(
        "/vacancies?limit=500"
    )

    assert response.status_code == 422
