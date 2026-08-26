import pytest


async def create_application(client, vacancy_id: int) -> int:
    response = await client.post(
        "/applications",
        json={"vacancy_id": vacancy_id},
    )

    assert response.status_code == 201
    return response.json()["id"]


async def transition_application(
    client,
    application_id: int,
    statuses: list[str],
) -> None:
    for application_status in statuses:
        response = await client.patch(
            f"/applications/{application_id}/status",
            json={"status": application_status},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_statistics(client):
    vacancy_ids = []

    for index in range(2):
        response = await client.post(
            "/vacancies",
            json={
                "title": f"Vacancy {index}",
                "company": "Dashboard Corp",
            },
        )
        assert response.status_code == 201
        vacancy_ids.append(response.json()["id"])

    interview_application = await create_application(
        client,
        vacancy_ids[0],
    )
    await transition_application(
        client,
        interview_application,
        ["APPLIED", "HR_SCREEN"],
    )

    offer_application = await create_application(
        client,
        vacancy_ids[0],
    )
    await transition_application(
        client,
        offer_application,
        ["APPLIED", "HR_SCREEN", "TECH_INTERVIEW", "OFFER"],
    )

    rejected_application = await create_application(
        client,
        vacancy_ids[1],
    )
    await transition_application(
        client,
        rejected_application,
        ["APPLIED", "REJECTED"],
    )

    response = await client.get("/dashboard/statistics")

    assert response.status_code == 200
    assert response.json() == {
        "total_vacancies": 2,
        "total_applications": 3,
        "offers": 1,
        "rejections": 1,
        "interviews": 1,
        "by_status": {
            "NEW": 0,
            "APPLIED": 0,
            "HR_SCREEN": 1,
            "TECH_INTERVIEW": 0,
            "FINAL_INTERVIEW": 0,
            "OFFER": 1,
            "REJECTED": 1,
        },
    }


@pytest.mark.asyncio
async def test_dashboard_only_counts_owned_vacancies(
    client,
    act_as_user,
):
    await client.post(
        "/vacancies",
        json={
            "title": "First Owner Vacancy",
            "company": "Owner One",
        },
    )

    register_response = await client.post(
        "/auth/register",
        json={
            "email": "dashboard-owner@example.com",
            "password": "SecurePass123!",
        },
    )
    second_user = register_response.json()
    act_as_user(second_user["id"], second_user["email"])

    response = await client.get("/dashboard/statistics")

    assert response.status_code == 200
    assert response.json()["total_vacancies"] == 0
    assert response.json()["total_applications"] == 0
