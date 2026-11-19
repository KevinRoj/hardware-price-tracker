import re
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup


def clean_price(raw_price: str) -> Optional[float]:
    """Convierte textos como '₡145,500', '₡ 89.900,00' o '$320.50' a float."""
    if not raw_price:
        return None

    text = raw_price.strip()
    # Conserva dígitos, puntos y comas
    match = re.search(r"[\d.,]+", text)
    if not match:
        return None

    num_str = match.group(0)

    # Caso: separador de miles con coma y decimales con punto -> 1,299.99
    if "," in num_str and "." in num_str:
        if num_str.rfind(",") < num_str.rfind("."):
            num_str = num_str.replace(",", "")
        else:
            # Caso: miles con punto y decimales con coma -> 1.299,99
            num_str = num_str.replace(".", "").replace(",", ".")
    elif "," in num_str:
        # Si termina en coma seguida de 2 dígitos, asume decimal; si no, miles
        if re.search(r",\d{2}$", num_str):
            num_str = num_str.replace(",", ".")
        else:
            num_str = num_str.replace(",", "")
    elif "." in num_str:
        # Si tiene más de un punto o solo 3 dígitos tras el punto (ej. 85.000 en colones)
        parts = num_str.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            num_str = num_str.replace(".", "")

    try:
        return round(float(num_str), 2)
    except ValueError:
        return None


def _first_match(container, selectors: list[str]):
    for sel in selectors:
        found = container.select_one(sel)
        if found:
            return found
    return None


def parse_products(html: str, base_url: str) -> list[dict]:
    """Extrae productos de un catálogo HTML con selectores flexibles."""
    soup = BeautifulSoup(html, "lxml")
    items: list[dict] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    card_selectors = [
        "li.product",
        "div.product",
        "div.product-item",
        "div.product-layout",
        "article.product",
    ]
    cards = []
    for sel in card_selectors:
        cards = soup.select(sel)
        if cards:
            break

    title_selectors = [
        "h2.woocommerce-loop-product__title",
        ".product-title",
        ".product-name",
        "h2 a",
        "h3 a",
        "h4 a",
        "a[title]",
    ]
    price_selectors = [
        "span.price ins .amount",
        "span.price > .amount",
        "span.price",
        ".price",
        ".product-price",
    ]

    for card in cards:
        title_el = _first_match(card, title_selectors)
        price_el = _first_match(card, price_selectors)
        link_el = card.select_one("a[href]")

        title = title_el.get_text(" ", strip=True) if title_el else ""
        if not title and link_el and link_el.has_attr("title"):
            title = link_el["title"].strip()

        raw_price = price_el.get_text(" ", strip=True) if price_el else ""
        price = clean_price(raw_price)

        if not title or price is None:
            continue

        href = link_el["href"].strip() if (link_el and link_el.has_attr("href")) else ""
        if href.startswith("http"):
            full_link = href
        elif href:
            full_link = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
        else:
            full_link = f"{base_url.rstrip('/')}/"

        items.append({
            "producto": title,
            "precio": price,
            "precio_raw": raw_price,
            "url": full_link,
            "fecha_extraccion": timestamp,
        })

    return items