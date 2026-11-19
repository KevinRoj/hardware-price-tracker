import asyncio
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


async def fetch_html(url: str, retries: int = 3, timeout: float = 10.0) -> Optional[str]:
    """Descarga el HTML de una URL con manejo de errores y reintentos."""
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(
                headers=DEFAULT_HEADERS,
                timeout=timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                logger.info(f"Página descargada correctamente: {url}")
                return response.text
        except httpx.HTTPStatusError as exc:
            logger.warning(
                f"Error HTTP {exc.response.status_code} en {url} (Intento {attempt}/{retries})"
            )
        except httpx.RequestError as exc:
            logger.warning(
                f"Error de red al conectar con {url}: {exc} (Intento {attempt}/{retries})"
            )

        if attempt < retries:
            await asyncio.sleep(1.5 * attempt)

    logger.error(f"No se pudo obtener {url} tras {retries} intentos.")
    return None