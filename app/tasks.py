import asyncio


async def analyze_vacancy(ctx, vacancy_id: int):
    # Пока имитируем долгую внешнюю обработку.
    await asyncio.sleep(2)

    print(f"Vacancy {vacancy_id} analyzed")

    return {
        "vacancy_id": vacancy_id,
        "status": "processed",
    }