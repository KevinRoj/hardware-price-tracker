import json
import logging
from pathlib import Path
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment

logger = logging.getLogger(__name__)

def export_reports(data: list[dict], output_dir: str = "output", prefix: str = "precios_reporte") -> None:
    """Exporta los datos normalizados a CSV, JSON y Excel formateado."""
    if not data:
        logger.warning("No hay datos para exportar.")
        return

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(data)
    # Ordenar del precio más bajo al más alto
    df = df.sort_values(by="precio", ascending=True).reset_index(drop=True)

    # 1. Exportar JSON
    json_file = out_path / f"{prefix}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

    # 2. Exportar CSV
    csv_file = out_path / f"{prefix}.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")

    # 3. Exportar Excel (.xlsx) con estilo
    xlsx_file = out_path / f"{prefix}.xlsx"
    with pd.ExcelWriter(xlsx_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Precios")
        ws = writer.sheets["Precios"]

        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        # Formato de moneda en la columna de precio (columna B)
        for row in range(2, len(df) + 2):
            ws[f"B{row}"].number_format = "$#,##0.00"

        # Autoajustar ancho de columnas
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 55)

    logger.info(f"Reportes generados en '{output_dir}/': JSON, CSV y XLSX.")