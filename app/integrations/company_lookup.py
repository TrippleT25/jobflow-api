import httpx


class CompanyLookupError(Exception):
    pass


async def fetch_company_website_info(
    url: str,
) -> dict:
    timeout = httpx.Timeout(15.0)

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)

        response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise CompanyLookupError(
            "Company website request timed out"
        ) from exc

    except httpx.HTTPError as exc:
        raise CompanyLookupError(
            "Failed to fetch company website"
        ) from exc

    return {
        "url": str(response.url),
        "status_code": response.status_code,
        "server": response.headers.get("server"),
        "content_type": response.headers.get("content-type"),
    }
