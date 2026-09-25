import time
import requests


def fetch_http(
    url,
    method="GET",
    headers=None,
    params=None,
    timeout=30,
    retries=3,
):
    headers = headers or {}
    params = params or {}

    last_error = None

    for attempt in range(
        1,
        retries + 1,
    ):
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                timeout=timeout,
            )

            response.raise_for_status()

            content_type = (
                response.headers
                .get(
                    "content-type",
                    "",
                )
                .lower()
            )

            data = None

            if (
                "application/json"
                in content_type
            ):
                try:
                    data = response.json()
                except Exception:
                    data = None

            return {
                "success": True,
                "url": response.url,
                "status_code": response.status_code,
                "headers": dict(
                    response.headers
                ),
                "text": response.text,
                "data": data,
                "attempt": attempt,
            }

        except Exception as exc:
            last_error = exc

            if attempt < retries:
                time.sleep(
                    2 ** (attempt - 1)
                )

    raise RuntimeError(
        f"HTTP connector failed after "
        f"{retries} attempts: "
        f"{last_error}"
    )
