# Diseño experto de plantilla de Memorias y generación de Corte (MVP)

## Objetivo
Diseñar una plantilla de memoria que capture mediciones reales en obra y convierta esas mediciones en cantidades consolidadas por actividad para corte, con trazabilidad y controles anti-fraude.

## 1) Estructura funcional de la plantilla

Se recomienda usar 3 hojas en Excel:

1. `INPUT`: captura de mediciones por línea.
2. `CATALOGOS`: actividades, unidades, tipos de medición, obras y contratistas.
3. `RESUMEN_CORTE`: consolidado por código de actividad (solo líneas válidas).

## 2) Modelo de datos en INPUT

Columnas:

- ID Registro (autogenerado)
- Fecha
- Obra
- Contratista
- Frente
- Código actividad
- Actividad (autocompletada por catálogo)
- Tipo medición (autocompletada)
- Unidad (autocompletada)
- Largo (m)
- Ancho (m)
- Alto (m)
- Cantidad base
- Factor
- Cantidad conmutada (calculada)
- Soporte (SI/NO)
- URL/Referencia soporte
- Observación
- Estado validación (calculado)

## 3) Reglas de conmutación de cantidades

- `AREA_2D`: Cantidad conmutada = Largo × Ancho × Factor
- `VOLUMEN_3D`: Cantidad conmutada = Largo × Ancho × Alto × Factor
- `LINEAL_1D`: Cantidad conmutada = Largo × Factor
- `CONTEO`: Cantidad conmutada = Cantidad base × Factor

Todas las cantidades deben redondearse a 4 decimales.

## 4) Reglas de validación anti-fraude

Una fila solo cuenta para corte cuando `Estado validación = OK`.

Bloqueos mínimos:

- Código actividad no existe en catálogo → `ERROR_CODIGO`.
- Faltan cabeceras obligatorias (fecha/obra/contratista) → `ERROR_CABECERA`.
- Dimensiones <= 0 en mediciones geométricas → `ERROR_DIMENSION`.
- Conteo <= 0 en actividades tipo CONTEO → `ERROR_CANTIDAD`.
- Soporte = NO → `BLOQUEADO_SIN_SOPORTE`.

## 5) Cómo se conecta a la visual de cantidades conmutadas

### Vista de residente (operativa)
- Captura por línea en `INPUT`.
- Ve cantidad conmutada por cada medición.

### Vista de director/control (excepción)
- Revisa `RESUMEN_CORTE` por actividad:
  - Código
  - Actividad
  - Unidad
  - Cantidad de corte (suma de líneas OK)
- Filtra alertas por `Estado validación` diferente de OK.

### Vista de tesorería
- Consume solo corte aprobado (no filas con errores o bloqueos).

## 6) Integración hacia Monday

Propuesta de mapeo:

- Item principal Monday: `Corte_Obra_Contratista_Periodo`.
- Subitems Monday: cada línea válida de medición.
- Columnas clave en Monday:
  - Código actividad
  - Cantidad conmutada
  - Estado validación
  - Soporte
  - Aprobado (director/control)

Regla obligatoria:
- Si existe al menos una alerta crítica (`ERROR_*` o `BLOQUEADO_*`), el estado del corte no puede pasar a `Aprobado`.

## 7) Recomendación de implementación

1. Arrancar con 1 obra y 2 contratistas.
2. Catálogo cerrado (sin edición por residentes).
3. Hoja INPUT protegida (solo celdas de captura desbloqueadas).
4. Activar bitácora de versiones de archivo + hash al importar.

## 8) Archivos base incluidos en el repositorio

Se incluyen CSV base para acelerar construcción de la plantilla:

- `templates/plantilla_memorias_input.csv`
- `templates/catalogo_actividades.csv`
- `templates/catalogo_obras.csv`
- `templates/catalogo_contratistas.csv`

También se incluye script de generación:

- `tools/create_memorias_template.py`

> Nota: en este entorno no fue posible instalar librerías para producir `.xlsx` protegido automáticamente. Los CSV incluidos son el insumo directo para montar y proteger la plantilla en Excel corporativo.

## 9) Ejecución del Paso 1 (catálogo piloto cargado)

Se ejecutó el Paso 1 con catálogo creado para piloto inicial:

- 1 obra: `OBRA PILOTO TORRE 1`.
- 2 contratistas: `CONTRATISTA ALFA SAS`, `CONTRATISTA BETA SAS`.
- 25 actividades de obra con códigos, tipo de medición, unidad y factor.

### ¿Era necesario investigar antes?

Sí, pero en nivel práctico de arranque (no estudio largo):

- Se requiere validar que cada actividad tenga una unidad de pago única y un tipo de medición consistente.
- Se requiere evitar catálogos abiertos para reducir reproceso y fraude operativo.
- Para el piloto, es suficiente iniciar con catálogo experto base y ajustar en ciclo 1 con residentes/director.

El catálogo generado en `templates/catalogo_actividades.csv` cubre actividades típicas de estructura, acabados, hidrosanitario y eléctrico para iniciar pruebas reales de memorias/cortes.

## 10) Ejecución del Paso 2: Excel corporativo creado

Se generó el archivo Excel corporativo para piloto en:

- `templates/plantilla_memorias_corporativa.xlsx`

### Qué incluye este Excel

- Hoja `INPUT` con estructura de captura de memorias.
- Hoja `CATALOGOS` cargada desde los CSV de Paso 1 (obra, contratistas, actividades).
- Hoja `INSTRUCTIVO` con reglas de uso.
- Fórmulas de conmutación por tipo de medición (`AREA_2D`, `VOLUMEN_3D`, `LINEAL_1D`, `CONTEO`).
- Estado de validación por línea para bloquear errores de captura.
- Resumen de corte que suma únicamente filas con estado `OK`.
- Protección de hoja con contraseña inicial `somatec` (cambiar en operación).

### Implementación técnica

La construcción del `.xlsx` se realiza con `tools/create_corporate_excel.py` generando paquete OOXML sin dependencias externas (útil en entornos restringidos).
