from bs4 import BeautifulSoup

from backend.app.services.http_connector import fetch_url


def scrape_page(url, timeout=30):
    response = fetch_url(
        url=url,
        timeout=timeout,
    )

    soup = BeautifulSoup(
        response["text"],
        "html.parser",
    )

    title = ""

    if soup.title:
        title = soup.title.get_text(
            strip=True
        )

    text = soup.get_text(
        " ",
        strip=True,
    )

    links = []

    for link in soup.find_all("a"):
        href = link.get("href")

        if href:
            links.append({
                "text": link.get_text(
                    " ",
                    strip=True,
                ),
                "href": href,
            })

    return {
        "url": response["url"],
        "status_code": response["status_code"],
        "title": title,
        "text": text,
        "links": links,
    }
