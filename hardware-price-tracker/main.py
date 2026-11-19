import asyncio
import logging
from scraper.fetcher import fetch_html
from scraper.parser import parse_products
from scraper.exporter import export_reports

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

BASE_URL = "https://www.intelec.co.cr/componentes"


def build_page_url(base_url: str, page: int) -> str:
    clean_base = base_url.rstrip("/")
    if page <= 1:
        return f"{clean_base}/"
    return f"{clean_base}/page/{page}"


async def run_pipeline(
    pages: int = 3,
    output_dir: str = "output",
    prefix: str = "intelec_componentes",
) -> None:
    """Extrae componentes de Intelec y genera los reportes."""
    all_products: list[dict] = []

    for page in range(1, pages + 1):
        url = build_page_url(BASE_URL, page)
        html = await fetch_html(url)
        if html:
            products = parse_products(html, BASE_URL)
            logging.info(f"Página {page}: {len(products)} productos extraídos.")
            all_products.extend(products)

    if not all_products:
        logging.warning(
            "No se extrajeron productos. Revisa si los selectores CSS de 'parser.py' "
            "coinciden con el HTML de Intelec o si el sitio bloquea peticiones sin navegador."
        )
        return

    prices = [item["precio"] for item in all_products]
    avg_price = sum(prices) / len(prices)

    logging.info(f"Total de productos extraídos: {len(all_products)}")
    logging.info(
        f"Precio mínimo: {min(prices):,.2f} | "
        f"Precio máximo: {max(prices):,.2f} | "
        f"Precio promedio: {avg_price:,.2f}"
    )

    export_reports(all_products, output_dir=output_dir, prefix=prefix)


if __name__ == "__main__":
    asyncio.run(run_pipeline(pages=3))