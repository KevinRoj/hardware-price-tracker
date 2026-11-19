# Hardware Price Tracker

Rastreador modular de precios de componentes y hardware construido en Python con enfoque ETL (`fetcher.py`, `parser.py`, `exporter.py` y `main.py`).

## Características
- Descarga asíncrona con reintentos y manejo de errores usando `httpx`.
- Extracción, limpieza y normalización de precios con `BeautifulSoup4` y `lxml`.
- Cálculo de precio mínimo, máximo y promedio.
- Exportación automática de reportes a **JSON**, **CSV** y **XLSX** (`pandas` + `openpyxl`).
