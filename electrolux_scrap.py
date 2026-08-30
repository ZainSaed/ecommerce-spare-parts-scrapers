from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

BASE_URL = "https://shop.electrolux.com.au/"
URL = BASE_URL

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=120000
    )

    page.wait_for_timeout(8000)

    links = page.locator("a")

    print("TITLE:", page.title())
    print("URL:", page.url)
    print("TOTAL LINKS:", links.count())

    print("\n")
    print("=" * 80)
    print("PART / ACCESSORY LINKS")
    print("=" * 80)

    seen = set()

    count = 0

    for i in range(links.count()):

        try:

            link = links.nth(i)

            text = link.inner_text().strip()
            href = link.get_attribute("href")

            if not href:
                continue

            full_url = urljoin(BASE_URL, href)

            key = full_url

            if key in seen:
                continue

            seen.add(key)

            if (
                "part" in full_url.lower()
                or "part" in text.lower()
                or "accessor" in full_url.lower()
                or "accessor" in text.lower()
            ):

                count += 1

                print(f"\n[{count}]")
                print("TEXT :", text)
                print("URL  :", full_url)

        except Exception:
            continue

    print("\n")
    print("=" * 80)
    print("UNIQUE PART / ACCESSORY LINKS:", count)
    print("=" * 80)

    input("\nPress ENTER to close...")

    browser.close()