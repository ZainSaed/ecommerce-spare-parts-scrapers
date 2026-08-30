from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import csv
import re
import time


BASE_URL = "https://www.breville.com"

OUTPUT_FILE = "breville_all_spare_parts.csv"


# ============================================================
# BREville AU PRODUCT CATEGORIES
# ============================================================

CATEGORIES = {
    # Coffee & Espresso
    "Espresso Machines":
        "https://www.breville.com/en-au/shop/espresso",

    "Nespresso Machines":
        "https://www.breville.com/en-au/shop/nespresso",

    "Drip Coffee Machines":
        "https://www.breville.com/en-au/shop/coffee",

    "Coffee Grinders":
        "https://www.breville.com/en-au/shop/coffee-grinders",


    # Juicers & Blenders
    "Juicers":
        "https://www.breville.com/en-au/shop/juicers",

    "Bluicers":
        "https://www.breville.com/en-au/shop/bluicers",

    "Blenders":
        "https://www.breville.com/en-au/shop/blenders",


    # Ovens / Air Fryers / Microwaves
    "Ovens & Air Fryers":
        "https://www.breville.com/en-au/shop/ovens",

    "Pizza Ovens":
        "https://www.breville.com/en-au/shop/pizzaovens",

    "Microwaves":
        "https://www.breville.com/en-au/shop/microwaves",

    "Bread Makers":
        "https://www.breville.com/en-au/shop/bread-makers",


    # Grills / Presses / Toasters
    "Toasters":
        "https://www.breville.com/en-au/shop/toasters",

    "Grills & Sandwich Makers":
        "https://www.breville.com/en-au/shop/grills-sandwich-makers",

    "Waffle Makers":
        "https://www.breville.com/en-au/shop/waffle-makers",


    # Cookers
    "Multi Cookers":
        "https://www.breville.com/en-au/shop/cookers",

    "Woks Skillets Deep Fryers":
        "https://www.breville.com/en-au/shop/woks-skillets-deep-fryers",

    "Sous Vide":
        "https://www.breville.com/en-au/shop/sous-vide",

    "Induction & Hot Plates":
        "https://www.breville.com/en-au/shop/induction-hotplates",


    # Water & Tea
    "Kettles":
        "https://www.breville.com/en-au/shop/kettles",

    "Water Dispensers":
        "https://www.breville.com/en-au/shop/water-dispensers",

    "Soda & Sparkling Water Makers":
        "https://www.breville.com/en-au/shop/soda-sparkling-water-makers",


    # Food Prep
    "Food Processors":
        "https://www.breville.com/en-au/shop/food-processors",

    "Stick Mixers":
        "https://www.breville.com/en-au/shop/immersion-blenders",

    "Mixers":
        "https://www.breville.com/en-au/shop/mixers",

    "Equipment":
        "https://www.breville.com/en-au/shop/miscellaneous",


    # Air
    "Air Purifiers":
        "https://www.breville.com/en-au/shop/air-purifier",

    "Air Dehumidifiers":
        "https://www.breville.com/en-au/shop/air-dehumidifier",

    "Air Humidifiers":
        "https://www.breville.com/en-au/shop/air-humidifier",

    "Air Multi Function":
        "https://www.breville.com/en-au/shop/air-multifunction",

    "Cooling Fans":
        "https://www.breville.com/en-au/shop/cooling-fans",

    "Heaters":
        "https://www.breville.com/en-au/shop/heaters",


    # Specialty Appliances
    "Ice Cream Makers":
        "https://www.breville.com/en-au/shop/ice-cream",

    "Snack Makers":
        "https://www.breville.com/en-au/shop/snack-makers",

    "Kettle and Toaster Set":
        "https://www.breville.com/en-au/shop/kettle-and-toaster-set",

    "Water Filtration":
        "https://www.breville.com/en-au/shop/water-filtration",

    "Electric Blankets":
        "https://www.breville.com/en-au/shop/electric-blankets",
}


# ============================================================
# HELPER
# ============================================================

def get_links(page):

    links = page.locator("a")

    results = []

    for i in range(links.count()):

        try:

            link = links.nth(i)

            href = link.get_attribute("href")
            text = link.inner_text().strip()

            if not href:
                continue

            results.append({
                "url": urljoin(BASE_URL, href),
                "text": text
            })

        except:
            continue

    return results


# ============================================================
# MAIN
# ============================================================

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.set_default_timeout(120000)


    # ========================================================
    # STEP 1
    # FIND /PARTS CATEGORY PAGES
    # ========================================================

    parts_categories = {}

    print()
    print("=" * 70)
    print("STEP 1 - FINDING PARTS CATEGORY PAGES")
    print("=" * 70)

    for category_name, category_url in CATEGORIES.items():

        parts_url = category_url.rstrip("/") + "/parts"

        print()
        print(f"{category_name}")
        print(f"  {parts_url}")

        try:

            response = page.goto(
                parts_url,
                wait_until="domcontentloaded",
                timeout=120000
            )

            page.wait_for_timeout(5000)

            # Check HTTP status
            status = response.status if response else None

            if status and status >= 400:

                print(
                    f"  FAILED - HTTP {status}"
                )

                continue

            # Make sure page actually exists
            title = page.title()

            if not title:

                print("  FAILED - no page title")

                continue

            parts_categories[category_name] = parts_url

            print(
                f"  OK - {title}"
            )

        except Exception as e:

            print(
                f"  FAILED - {type(e).__name__}: {e}"
            )


    print()
    print(
        f"Parts category pages found: "
        f"{len(parts_categories)}"
    )


    # ========================================================
    # STEP 2
    # DISCOVER MODEL PARTS PAGES
    # ========================================================

    model_pages = {}

    print()
    print("=" * 70)
    print("STEP 2 - DISCOVERING MODEL PARTS PAGES")
    print("=" * 70)

    for category_name, parts_url in parts_categories.items():

        print()
        print(f"[{category_name}]")

        try:

            page.goto(
                parts_url,
                wait_until="domcontentloaded",
                timeout=120000
            )

            page.wait_for_timeout(6000)

            links = get_links(page)

            category_models = 0

            for link in links:

                url = link["url"]

                # Expected:
                #
                # /en-au/shop/espresso/parts/bes985
                #
                # /en-au/shop/coffee/parts/bdc650
                #
                # etc.

                match = re.search(
                    r"/en-au/shop/([^/]+)/parts/([^/?#]+)",
                    url,
                    re.IGNORECASE
                )

                if not match:
                    continue

                shop_category = match.group(1).lower()

                model = match.group(2).upper()

                key = (
                    f"{shop_category}|"
                    f"{model}"
                )

                if key in model_pages:
                    continue

                model_pages[key] = {
                    "category": category_name,
                    "shop_category": shop_category,
                    "machine_model": model,
                    "model_url": url
                }

                category_models += 1


            print(
                f"  Models found: "
                f"{category_models}"
            )

        except Exception as e:

            print(
                f"  ERROR: "
                f"{type(e).__name__}: {e}"
            )


    print()
    print("=" * 70)
    print(
        f"TOTAL MODEL PAGES: "
        f"{len(model_pages)}"
    )
    print("=" * 70)


    # ========================================================
    # STEP 3
    # SCRAPE SPARE PARTS
    # ========================================================

    all_parts = {}

    part_relationships = []

    failed_models = []

    zero_part_models = []

    print()
    print("=" * 70)
    print("STEP 3 - SCRAPING SPARE PARTS")
    print("=" * 70)


    total_models = len(model_pages)


    for index, data in enumerate(
        model_pages.values(),
        start=1
    ):

        category = data["category"]

        model = data["machine_model"]

        model_url = data["model_url"]

        print()
        print(
            f"[{index}/{total_models}] "
            f"{category} -> {model}"
        )

        try:

            page.goto(
                model_url,
                wait_until="domcontentloaded",
                timeout=120000
            )

            page.wait_for_timeout(6000)


            # ------------------------------------------------
            # Get all product links
            # ------------------------------------------------

            links = page.locator(
                'a[href*="/product/"]'
            )

            raw_product_links = links.count()

            model_skus = set()


            for i in range(raw_product_links):

                try:

                    link = links.nth(i)

                    href = link.get_attribute(
                        "href"
                    )

                    if not href:
                        continue


                    # ------------------------------------------------
                    # ONLY SPARE PART SKU
                    #
                    # Example:
                    #
                    # ?sku=SP0109865
                    # ------------------------------------------------

                    match = re.search(
                        r"[?&]sku=(SP[A-Z0-9]+)",
                        href,
                        re.IGNORECASE
                    )

                    if not match:
                        continue


                    sku = match.group(1).upper()

                    part_url = urljoin(
                        BASE_URL,
                        href
                    )

                    model_skus.add(sku)


                    # ------------------------------------------------
                    # Global unique part
                    # ------------------------------------------------

                    if sku not in all_parts:

                        all_parts[sku] = {
                            "part_sku": sku,
                            "first_category": category,
                            "first_machine_model": model,
                            "part_url": part_url
                        }


                    # ------------------------------------------------
                    # Machine -> part relationship
                    # ------------------------------------------------

                    relationship_key = (
                        category,
                        model,
                        sku
                    )

                    if relationship_key not in [
                        (
                            x["category"],
                            x["machine_model"],
                            x["part_sku"]
                        )
                        for x in part_relationships
                    ]:

                        part_relationships.append({
                            "category": category,
                            "machine_model": model,
                            "part_sku": sku,
                            "part_url": part_url
                        })


                except:
                    continue


            print(
                f"  Product links: "
                f"{raw_product_links}"
            )

            print(
                f"  Spare-part SKUs: "
                f"{len(model_skus)}"
            )


            if len(model_skus) == 0:

                zero_part_models.append({
                    "category": category,
                    "machine_model": model,
                    "model_url": model_url
                })


        except Exception as e:

            print(
                f"  FAILED: "
                f"{type(e).__name__}: {e}"
            )

            failed_models.append({
                "category": category,
                "machine_model": model,
                "model_url": model_url,
                "error": str(e)
            })


        time.sleep(1)


    browser.close()


# ============================================================
# STEP 4
# SAVE UNIQUE PARTS
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "part_sku",
            "first_category",
            "first_machine_model",
            "part_url"
        ]
    )

    writer.writeheader()

    for part in all_parts.values():

        writer.writerow(part)


# ============================================================
# SAVE MACHINE/PART RELATIONSHIPS
# ============================================================

RELATIONSHIP_FILE = (
    "breville_machine_part_relationships.csv"
)


with open(
    RELATIONSHIP_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "category",
            "machine_model",
            "part_sku",
            "part_url"
        ]
    )

    writer.writeheader()

    writer.writerows(
        part_relationships
    )


# ============================================================
# SAVE FAILED MODELS
# ============================================================

FAILED_FILE = (
    "breville_failed_models.csv"
)


with open(
    FAILED_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "category",
            "machine_model",
            "model_url",
            "error"
        ]
    )

    writer.writeheader()

    writer.writerows(
        failed_models
    )


# ============================================================
# SAVE ZERO-PART MODELS
# ============================================================

ZERO_FILE = (
    "breville_zero_part_models.csv"
)


with open(
    ZERO_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "category",
            "machine_model",
            "model_url"
        ]
    )

    writer.writeheader()

    writer.writerows(
        zero_part_models
    )


# ============================================================
# FINAL REPORT
# ============================================================

print()
print()
print("=" * 70)
print("BREVILLE AU SPARE PARTS AUDIT COMPLETE")
print("=" * 70)

print(
    f"Parts categories found:       "
    f"{len(parts_categories)}"
)

print(
    f"Model pages discovered:       "
    f"{len(model_pages)}"
)

print(
    f"Successfully failed models:   "
    f"{len(failed_models)}"
)

print(
    f"Models with zero parts:        "
    f"{len(zero_part_models)}"
)

print(
    f"Machine/part relationships:    "
    f"{len(part_relationships)}"
)

print(
    f"UNIQUE SPARE-PART SKUs:        "
    f"{len(all_parts)}"
)

print()
print(
    f"Unique parts CSV:              "
    f"{OUTPUT_FILE}"
)

print(
    f"Relationship CSV:              "
    f"{RELATIONSHIP_FILE}"
)

print(
    f"Failed models CSV:             "
    f"{FAILED_FILE}"
)

print(
    f"Zero-part models CSV:          "
    f"{ZERO_FILE}"
)

print("=" * 70)