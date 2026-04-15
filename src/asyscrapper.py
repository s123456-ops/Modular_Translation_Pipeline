import asyncio
import aiohttp
import csv
import os
from aiohttp import ClientSession, ClientTimeout

API_URL = "https://world.openfoodfacts.org/cgi/search.pl"
HEADERS = {"User-Agent": "MyAwesomeApp/1.0"}

OUTPUT_DIR = "data"

CATEGORIES = ["sugar", "bread", "milk", "champagnes", "butter"]
TARGET_COUNT = 180
PAGE_SIZE = 100
MAX_PAGES = 50

MAX_CONCURRENT_REQUESTS = 1  # One request at a time
MAX_CONCURRENT_IMAGES = 3
RETRY_ATTEMPTS = 8
RETRY_DELAY = 5  # seconds
REQUEST_DELAY = 2  # Delay between requests


# -------------------------
# Helpers
# -------------------------
def get_best_image(product):
    return (
        product.get("image_url")
        or product.get("image_front_url")
        or product.get("image_small_url")
        or product.get("image_thumb_url")
    )


def is_valid_product(product):
    required = ["_id", "product_name", "categories_tags"]
    if not all(product.get(f) for f in required):
        return False
    return bool(get_best_image(product))


def extract_product_info(product):
    return [
        product.get("_id"),
        product.get("product_name"),
        ", ".join(product.get("categories_tags", [])),
        product.get("ingredients_text", ""),
        get_best_image(product)
    ]


# -------------------------
# Async API fetch
# -------------------------
async def fetch_page(session, category, page, page_size, sem):
    params = {
        "action": "process",
        "tagtype_0": "categories",
        "tag_contains_0": "contains",
        "tag_0": category,
        "page": page,
        "page_size": page_size,
        "json": 1
    }

    async with sem:
        for attempt in range(RETRY_ATTEMPTS):
            try:
                await asyncio.sleep(REQUEST_DELAY)  # Delay between requests
                async with session.get(API_URL, params=params) as resp:
                    data = await resp.json()
                    products = data.get("products", [])
                    if page == 1:
                        print(f"  API Response - Total count: {data.get('count', 0)}, Products returned: {len(products)}")
                    return products
            except asyncio.TimeoutError:
                if attempt < RETRY_ATTEMPTS - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    print(f"⚠ Timeout page {page}, retry {attempt + 1}/{RETRY_ATTEMPTS} après {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"⚠ Erreur API page {page} après {RETRY_ATTEMPTS} tentatives")
                    return []
            except Exception as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    print(f"⚠ Erreur page {page}: {e}, retry {attempt + 1}/{RETRY_ATTEMPTS} après {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"⚠ Erreur API page {page} :", e)
                    return []


# -------------------------
# Async image download
# -------------------------
async def download_image(session, url, image_id, category, sem):
    folder = f"data/raw/images/{category}"
    if not url:
        return

    os.makedirs(folder, exist_ok=True)

    ext = url.split(".")[-1].split("?")[0]
    filename = os.path.join(folder, f"{image_id}.{ext}")

    if os.path.exists(filename):
        return

    async with sem:
        try:
            async with session.get(url) as resp:
                content = await resp.read()
                with open(filename, "wb") as f:
                    f.write(content)
        except Exception as e:
            print(f"⚠ Impossible de télécharger {url} :", e)


# -------------------------
# Main scraping logic
# -------------------------
async def scrape(category, target_count, page_size, max_pages):
    timeout = ClientTimeout(total=120)  # Increased from 60
    sem_api = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    sem_img = asyncio.Semaphore(MAX_CONCURRENT_IMAGES)

    async with ClientSession(headers=HEADERS, timeout=timeout) as session:
        valid_products = []
        image_tasks = []
        page = 1
        
        print(f"  Initialisation avec délai de 5s...")
        await asyncio.sleep(5)  # Initial delay before starting

        while len(valid_products) < target_count and page <= max_pages:
            print(f"→ Téléchargement page {page}…")

            products = await fetch_page(session, category, page, page_size, sem_api)
            if not products:
                print("Aucun produit trouvé sur cette page.")
                break

            valid_on_page = 0
            for product in products:
                if is_valid_product(product):
                    valid_on_page += 1
                    info = extract_product_info(product)
                    valid_products.append(info)

                    image_url = info[-1]
                    image_id = info[0]

                    task = asyncio.create_task(
                        download_image(session, image_url, image_id, category, sem_img)
                    )
                    image_tasks.append(task)

                    if len(valid_products) >= target_count:
                        break
            
            print(f"  Produits valides trouvés: {valid_on_page}/{len(products)}")
            page += 1

        await asyncio.gather(*image_tasks)
        return valid_products


# -------------------------
# CSV export
# -------------------------
def save_to_csv(filename, rows):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["foodId", "label", "category", "foodContentsLabel", "image"])
        writer.writerows(rows)


# -------------------------
# Entry point
# -------------------------
def main():
    for category in CATEGORIES:
        print(f"\n🔄 Scraping category: {category}")
        products = asyncio.run(scrape(category, TARGET_COUNT, PAGE_SIZE, MAX_PAGES))
        output_file = f"{OUTPUT_DIR}/metadata_{category}_{TARGET_COUNT}.csv"
        save_to_csv(output_file, products)
        print(f"✔ Fichier {output_file} créé. Produits valides collectés : {len(products)}")


if __name__ == "__main__":
    main()
