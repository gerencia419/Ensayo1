"""Generate base CSV assets for the Memorias/Cortes MVP template.

This fallback generator avoids third-party dependencies in restricted environments.
It creates ready-to-load catalogs for Step 1 (pilot scope):
- 1 obra
- 2 contratistas
- closed activity catalog with measurement types and factors
"""

from __future__ import annotations

import csv
from pathlib import Path

BASE_DIR = Path("templates")

INPUT_HEADERS = [
    "ID Registro",
    "Fecha",
    "Obra",
    "Contratista",
    "Frente",
    "Código actividad",
    "Actividad",
    "Tipo medición",
    "Unidad",
    "Largo (m)",
    "Ancho (m)",
    "Alto (m)",
    "Cantidad base",
    "Factor",
    "Cantidad conmutada",
    "Soporte (SI/NO)",
    "URL/Referencia soporte",
    "Observación",
    "Estado validación",
]

# Pilot closed catalog created for Somatec's first execution cycle.
ACTIVIDADES = [
    ["PREL-001", "Replanteo y trazado", "AREA_2D", "m2", "1.00"],
    ["PREL-002", "Demolición de piso", "AREA_2D", "m2", "1.00"],
    ["EXCA-010", "Excavación manual", "VOLUMEN_3D", "m3", "1.00"],
    ["EXCA-011", "Excavación mecánica", "VOLUMEN_3D", "m3", "1.00"],
    ["RELL-020", "Relleno compactado", "VOLUMEN_3D", "m3", "1.08"],
    ["CONC-030", "Concreto de limpieza", "VOLUMEN_3D", "m3", "1.00"],
    ["CONC-031", "Concreto estructural", "VOLUMEN_3D", "m3", "1.00"],
    ["ACER-040", "Acero de refuerzo instalado", "CONTEO", "kg", "1.00"],
    ["MAMP-050", "Mampostería en bloque", "AREA_2D", "m2", "1.00"],
    ["PAÑE-060", "Pañete de muros", "AREA_2D", "m2", "1.05"],
    ["ENCH-070", "Enchape de muro cerámico", "AREA_2D", "m2", "1.03"],
    ["PISO-071", "Enchape de piso porcelanato", "AREA_2D", "m2", "1.05"],
    ["PINT-080", "Pintura vinilo en muros", "AREA_2D", "m2", "1.00"],
    ["YESO-081", "Cielo raso en drywall", "AREA_2D", "m2", "1.00"],
    ["IMPE-090", "Impermeabilización de placa", "AREA_2D", "m2", "1.00"],
    ["TUBH-100", "Tubería hidráulica", "LINEAL_1D", "ml", "1.00"],
    ["TUBS-101", "Tubería sanitaria", "LINEAL_1D", "ml", "1.00"],
    ["CABL-110", "Cableado eléctrico", "LINEAL_1D", "ml", "1.00"],
    ["DUCT-111", "Ductería EMT/PVC", "LINEAL_1D", "ml", "1.00"],
    ["APAR-120", "Instalación de aparato sanitario", "CONTEO", "und", "1.00"],
    ["PTEE-121", "Punto eléctrico", "CONTEO", "und", "1.00"],
    ["LUMI-122", "Luminaria instalada", "CONTEO", "und", "1.00"],
    ["PUE-130", "Puerta instalada", "CONTEO", "und", "1.00"],
    ["VENT-131", "Ventana instalada", "CONTEO", "und", "1.00"],
    ["GUAR-140", "Guardaescoba / zócalo", "LINEAL_1D", "ml", "1.00"],
]

OBRAS = [["obra"], ["OBRA PILOTO TORRE 1"]]
CONTRATISTAS = [["contratista"], ["CONTRATISTA ALFA SAS"], ["CONTRATISTA BETA SAS"]]


def write_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerows(rows)


def main() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    write_csv(BASE_DIR / "plantilla_memorias_input.csv", [INPUT_HEADERS])
    write_csv(
        BASE_DIR / "catalogo_actividades.csv",
        [["codigo", "actividad", "tipo_medicion", "unidad", "factor"]] + ACTIVIDADES,
    )
    write_csv(BASE_DIR / "catalogo_obras.csv", OBRAS)
    write_csv(BASE_DIR / "catalogo_contratistas.csv", CONTRATISTAS)

    print("Generated CSV assets in templates/")
    print(f"- Actividades: {len(ACTIVIDADES)}")
    print(f"- Obras: {len(OBRAS) - 1}")
    print(f"- Contratistas: {len(CONTRATISTAS) - 1}")


if __name__ == "__main__":
    main()
