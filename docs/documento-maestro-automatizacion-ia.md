# Documento maestro — Automatización e IA (Somatec)

**Diseño inicial + portafolio de iniciativas + MVP urgente de Memorias/Cortes (anti-fraude)**

- **Fecha:** 11 Feb 2026
- **Versión:** 0.6 (riesgos mitigados + paginación mejorada)
- **Propietario:** Gerencia (Juan Granados)

## 1. Resumen ejecutivo

Este documento consolida el portafolio de automatización e IA de Somatec y define un MVP urgente para Memorias/Cortes orientado a: (1) eliminar fraude y errores, (2) mejorar trazabilidad, y (3) reducir carga operativa de residentes y directores mediante control por excepción.

**Decisiones clave:**
- Excel seguirá existiendo como captura de memorias, pero deja de ser la fuente de verdad del pago.
- Monday será la fuente de verdad para corte, aprobación y auditoría (MVP rápido y adoptable).
- Tarifario central versionado (vigencia + soporte) para precios variables por contratista/obra/ciudad/tiempo.
- Codex automatiza validación de Excel, importación, control de versiones/dedupe, motor de precios, consolidación y alertas.

## 2. Contexto y sistemas actuales

**Sistemas en uso o previstos:**
- SINCO: ERP (finanzas/operación). Integración pendiente de definir (API/Datamart).
- Monday: herramienta frecuente para gestión; se usará como core del MVP de cortes.
- Power Platform: foco para Bitácora IA y automatizaciones con gobierno.
- Airtable: evaluado para licitaciones, aún no se inicia; se prioriza simplicidad y adopción.

**Dolor crítico (riesgo económico alto):**
- Cortes basados en Excels sin auditoría ni trazabilidad permiten manipulación.
- Fraude detectado tras varios cortes; causa raíz: control manual sobre múltiples Excels.

## 3. Objetivos

**Primario (urgente):**
- Eliminar vectores de fraude y error: el pago se calcula y aprueba fuera del Excel, con trazabilidad.

**Secundarios (muy importantes):**
- Reducir carga operativa de residentes y directores (menos digitación y revisión manual).
- Trazabilidad completa (quién, cuándo, qué cambió, por qué).
- Control económico con alertas tempranas sin depender aún de SINCO.

## 4. Definiciones

- **Memoria:** captura de cantidades ejecutadas por contratista y actividad.
- **Tarifario/Contrato:** precios vigentes por unidad (contratista/obra/ciudad/vigencia).
- **Corte:** consolidación de cantidades x precio vigente, con soporte y aprobación.

## 5. Customer journey — Memorias y Cortes por contratista

**Roles:** Residente (captura), Director/Control (aprueba), Admin/Tesorería (paga), Gerencia (audita).

### 5.1 Residente — Captura (más fácil que hoy)

**Experiencia:**
1. Abre plantilla única de Memoria por Contratista (Excel) con listas de ítems/unidades.
2. Registra una fila por actividad (ítem-código, unidad, cantidad). Opcional: frente/observación.
3. Adjunta soporte mínimo según regla por ítem.
4. Sube a Monday y cambia estado a `Enviado`.

**Medidas concretas para bajar carga:**
- Copiar memoria anterior por contratista (plantilla pre-llenada).
- Menos digitación: listas y pre-llenado desde Monday (obra/ciudad/periodo).
- Sin precios en la memoria: el sistema los asigna desde tarifario.

### 5.2 Sistema — Validación, importación, versiones/dedupe y alertas

- Validador estricto: rechaza archivos con fórmulas en inputs, hojas extra, celdas combinadas u ocultas, fuentes blancas, links externos o macros.
- Importador robusto: maneja coma/punto, filas vacías y validaciones por línea con mensajes claros.
- Control de versiones: ID (contratista+obra+periodo) + hash; evita reimportación duplicada.
- Deduplicación: una sola versión activa; historial disponible para auditoría.
- Motor de precios por código + precedencia (obra > ciudad > general) y vigencia.
- Alertas mínimas (5): sin precio, sin soporte, duplicado, variación fuerte, ítem nuevo.

### 5.3 Director/Control — Revisión por excepción

- Revisa corte en Monday con panel de alertas. Si no hay alertas, aprueba rápido.
- Solicitado vs Aprobado: el pago sale SOLO de campos aprobados.
- Cambios post-envío obligan a estado `Observado`.

### 5.4 Admin/Tesorería — Pago

- Paga solo cortes en `Aprobado`.
- Reporte final generado (PDF/Excel no editable) como soporte único.

### 5.5 Gerencia — Auditoría y prevención de fraude migrado

- Tablero de anomalías + KPIs y seguimiento de excepciones.
- Muestreo en campo (aleatorio) para evitar fraude por inflación de cantidades o soportes reciclados.
- Separación de funciones: quien captura no aprueba ni paga.

## 6. Manejo de precios (Tarifario versionado)

**Estructura mínima del tarifario:**

| Campo | Regla |
|---|---|
| Contratista | Obligatorio |
| Ciudad/Zona | Opcional |
| Obra/Proyecto | Opcional |
| Ítem (código) | Obligatorio (matching) |
| Unidad | Obligatoria |
| Precio | Obligatorio |
| Vigencia desde/hasta | Obligatoria |
| Soporte | Obligatorio (contrato/OC/acta/cotización) |
| Estado | Propuesto/Aprobado/Reemplazado (versionado) |

**Precedencia de precio:**
1. Contratista + Obra + Ítem + Vigencia.
2. Contratista + Ciudad/Zona + Ítem + Vigencia.
3. Contratista + Ítem + Vigencia (general).
4. Sin precio: bloqueo y tarea `Definir precio con soporte`.

- Gobierno: no se edita un precio vigente; se crea nueva versión con nueva vigencia.
- SLA: precios faltantes se resuelven en 24-48h (responsable definido).

## 7. Diseño del MVP (Monday + Excel controlado + Codex)

### 7.1 Gobernanza (anti-falla)

- Owners: solo Control/Gerencia (2-3). Residentes nunca owners.
- Permisos por columna: residente (captura), director/control (aprobado), tesorería (pagado).
- Automatizaciones/columnas solo por owners; auditoría de cambios activada.

### 7.2 Plantilla Excel (anti-falla de importación)

- Una hoja INPUT, una tabla, sin celdas combinadas ni hojas extra.
- Sin fórmulas en inputs, sin totales, sin macros/links externos.
- Validación: rechazo con mensaje línea/causa.

### 7.3 Estados y bloqueos (anti-bypass)

- Bloqueos: sin soporte, sin precio, duplicados, variación fuerte, ítem nuevo.
- Regla: Tesorería paga solo estado Aprobado.

## 8. Componentes Codex (con controles)

- Validador: estricto + reporte de errores; log persistente por archivo.
- Importador: soporta `parcial` vs `estricto` según piloto; siempre marca lo inválido.
- Versiones/dedupe: ID + hash; una versión activa; histórico auditado.
- Motor de precios: matching por código; precedencia; tablero `faltan precios`.
- Reporte: PDF/Excel no editable con sello de aprobación (fecha + aprobador).
- Seguridad: cuenta de servicio; secretos seguros; rotación; permisos mínimos; log de ejecuciones.

## 9. Registro de riesgos y mitigaciones

| Riesgo | Qué pasa | Mitigación |
|---|---|---|
| Permisos/owners | Manipulación del proceso | Owners limitados; permisos por columna; auditoría. |
| Catálogo abierto | No hay match / datos sucios | Catálogo por código; dueño; cambios controlados. |
| Tarifario caótico | Peleas / precios manipulables | Versionado+vigencia+soporte; SLA precios. |
| Excel fuera del estándar | Importación falla | Plantilla única; validador; rechazo explicativo. |
| Reimportación | Duplicados y sobrepago | ID+hash; versión activa; dedupe automático. |
| Sin match de precio | Bloqueo y fricción | Códigos; precedencia; tablero `faltan precios`. |
| Board pesado | Abandono de usuarios | Evidencia mínima; subitems; límites adjuntos. |
| Tokens/secretos | Riesgo de seguridad | Cuenta servicio; secretos seguros; rotación; logs. |
| Alertas mal calibradas | Nadie revisa / no detecta | Solo 5 alertas; calibrar 2-3 ciclos. |
| Bypass (WhatsApp/Excel) | Se paga por fuera | Política: solo Aprobado; reporte único; control tesorería. |
| Fraude migra | Cantidades/soportes falsos | Soporte por ítem; muestreo; histórico; separación. |

## 10. No negociables

1. Excel no calcula pago: solo captura cantidades.
2. Monday es la fuente de verdad (corte/aprobación/auditoría).
3. Residentes nunca owners; owners limitados (2-3).
4. Catálogo cerrado por código; unidad normalizada.
5. Tarifario versionado con vigencia y soporte.
6. Sin precio: bloqueo (no aprobado).
7. Sin soporte mínimo: no avanza.
8. Validación estricta + log de errores.
9. Versiones y dedupe antes de consolidar/pagar.
10. Tesorería paga solo en Aprobado.

## 11. Plan de acción (0 a 2 semanas)

### Semana 0 (ya)
- Congelar Excels actuales como evidencia (copias + PDF).
- Publicar plantilla única + regla de soporte mínimo por ítem.
- Nombrar dueños: catálogo, tarifario, administración Monday.

### Semana 1 (MVP)
- Crear Boards + permisos + estados + bloqueos mínimos.
- Piloto 1 obra + 2 contratistas. Medir tiempos (residente/director).
- Definir política de adjuntos (evidencia mínima).

### Semana 2 (Codex)
- Validador + importador + versiones/dedupe.
- Motor de precios + tablero `faltan precios`.
- Reporte final no editable + sello de aprobación.
- 5 alertas mínimas + calibración con 2 ciclos reales.

## 12. Indicadores (económico y carga)

- Ahorro: ajustes solicitado vs aprobado + anomalías detectadas antes de pagar.
- Tiempo residente: minutos para preparar y enviar memoria.
- Tiempo director: minutos para aprobar (meta: control por excepción).
- Reproceso: % memorias devueltas por errores/soporte.
- Riesgo: # alertas críticas por corte + resolución en 48h.

## 13. Portafolio (vista ejecutiva)

| Título del proyecto | Prioridad | Impacto_$ | Esfuerzo | Fuente_$ | Stack recomendado |
|---|---|---|---|---|---|
| Licitaciones IA (radar + scoring + lector de pliegos) | P2 | $$$$ | Medio | Mayor margen/ingresos | Monday (MVP) / Airtable + LLM |
| Pools (proveedores/contratistas) con trazabilidad y scoring | P1 | $$$$$ | Alto | Ahorro directo + evitar sobrepagos | SINCO + Monday + BI |
| Bitácora IA (reuniones/actas/evidencia/compromisos buscables) | P2 | $$$$ | Medio | Recuperar cambios + evitar reclamaciones | Power Platform |
| CxP extremo a extremo (factura→retenciones→radicación→alertas) | P2 | $$$$ | Alto | Evitar errores + reproceso + flujo caja | SINCO + Power Automate + OCR |
| IA para mejorar textos del técnico y sugerir soluciones | P2 | $$$ | Bajo | Ahorro de horas | ChatGPT/Copilot |
| Causación de facturas (DIAN + plantilla + IA + memoria de impuestos) | P2 | $$$$ | Medio | Ahorro de horas + menos errores | SINCO + Power Automate + OCR |
| Memorias de obra IA (voz+fotos+plano) + evita pagar dos veces | P2 | $$$$$ | Muy alto | Evitar sobrepagos + control | Power Apps móvil + IA |
| Informes/charlas SST automáticos (post-ATS) | P2 | $$$ | Bajo | Ahorro de horas | Power Apps + IA |


## 14. Costos estimados antes de empezar (preinicio)

> Estimación inicial para decidir arranque del MVP. Valores en **COP** y con IVA/extras no incluidos salvo que se indique. Se recomienda actualizar con cotizaciones reales antes de contratar.

### 14.1 Supuestos usados para el cálculo

- Alcance del piloto: **1 obra + 2 contratistas**.
- Duración del preinicio: **2 semanas** (diseño operativo, configuración y alistamiento técnico).
- Equipo mínimo: líder funcional (Control), administrador Monday y apoyo técnico de automatización.
- Se usan tus no negociables: Monday como fuente de verdad, validación estricta y bloqueo por precio/soporte.

### 14.2 Costos únicos de preinicio (one-off)

| Rubro | Base de cálculo | Costo estimado (COP) |
|---|---|---:|
| Descubrimiento y diseño detallado (8 sesiones) | 8 sesiones x 2 h x $300.000/h | 4.800.000 |
| Configuración Monday (boards, permisos, estados, automatizaciones base) | Bolsa cerrada | 5.500.000 |
| Diseño de plantilla Excel única + reglas por ítem | Bolsa cerrada | 1.800.000 |
| Desarrollo MVP backend (validador, importador, dedupe, precios, alertas) | 80 h x $220.000/h | 17.600.000 |
| QA + pruebas de fraude/error (casos de prueba + hardening) | 24 h x $180.000/h | 4.320.000 |
| Capacitación y manual operativo (residente/director/tesorería) | 3 sesiones x 2 h x $350.000/h | 2.100.000 |
| Gestión de proyecto y seguimiento (2 semanas) | 12 h x $200.000/h | 2.400.000 |
| **Subtotal costos únicos** |  | **38.520.000** |
| Contingencia 15% (riesgos de ajuste) | 15% del subtotal | 5.778.000 |
| **Total estimado preinicio (único)** |  | **44.298.000** |

### 14.3 Costos mensuales de operación desde el arranque

| Rubro | Base de cálculo | Costo estimado mensual (COP) |
|---|---|---:|
| Licencias Monday (10 usuarios de trabajo) | $120.000/usuario/mes (referencial) | 1.200.000 |
| Hosting backend + base de datos + backups | Nube básica productiva | 900.000 |
| Monitoreo/logs/alertamiento técnico | Stack ligero | 350.000 |
| Soporte evolutivo y correctivo | 20 h/mes x $200.000/h | 4.000.000 |
| **Total mensual estimado** |  | **6.450.000** |

### 14.4 Escenarios de presupuesto para decidir

| Escenario | Costo único (COP) | Costo mensual (COP) | Cuándo elegirlo |
|---|---:|---:|---|
| Conservador | 35.000.000 | 5.000.000 | Si buscan arrancar con mínimo técnico y procesos muy manuales de soporte |
| Recomendado | 44.298.000 | 6.450.000 | Balance entre control anti-fraude, velocidad de salida y sostenibilidad |
| Robusto | 58.000.000 | 9.000.000 | Si quieren más automatización, tableros avanzados y gobierno fuerte desde día 1 |

### 14.5 Punto de equilibrio (regla rápida)

Para justificar económicamente el proyecto:

- Si el sistema evita/reduce errores y sobrepagos por al menos **$6.450.000/mes**, se paga su operación mensual.
- Si además evita una pérdida única superior a **$44.298.000**, recupera el costo inicial del preinicio.

### 14.6 Recomendación de aprobación financiera

- Aprobar presupuesto inicial por **$45M COP** (tope redondeado) para arrancar el MVP en 2 semanas.
- Asegurar una bolsa operativa de **$6.5M COP/mes** por 3 meses de estabilización.
- Revisar KPIs de ahorro y reproceso en el mes 2 para decidir escalamiento a más obras.


### 14.7 Ajuste solicitado: si Monday ya está pagado y existe infraestructura interna

Sí: si ya pagan Monday, **normalmente solo deben crear un usuario técnico para Codex** (cuenta de servicio) con permisos mínimos y trazabilidad separada del usuario humano.

#### Impacto en costos si Monday ya está cubierto

- Si la licencia adicional de ese usuario ya está incluida en su plan actual: costo incremental de Monday = **$0 COP/mes**.
- Si requiere un asiento adicional: costo incremental = valor de 1 usuario según su plan corporativo.

#### Hosting: opciones recomendadas usando recursos existentes

| Opción | Cuándo aplica | Costo mensual estimado (COP) | Comentario |
|---|---|---:|---|
| Reusar servidor/VM interno existente | TI tiene capacidad y backups corporativos | 0 a 400.000 | Puede haber costo interno de operación/backup aunque no haya factura nueva |
| Reusar tenant cloud corporativo | La empresa ya opera en Azure/AWS/GCP | 300.000 a 1.200.000 | Recomendado por gobierno, seguridad y continuidad |
| Nuevo hosting dedicado MVP | No hay infraestructura disponible | 900.000 a 2.000.000 | Mayor autonomía, mayor costo directo |

#### Desglose pedido: monitoreo, logs y alertamiento

| Componente | Qué incluye | Rango mensual estimado (COP) |
|---|---|---:|
| Monitoreo de disponibilidad | health checks, uptime, latencia básica | 100.000 a 250.000 |
| Logs centralizados | retención de logs, búsqueda y auditoría técnica | 120.000 a 400.000 |
| Alertamiento operativo | notificaciones por fallo de importación/proceso | 80.000 a 250.000 |
| **Total monitoreo+logs+alertamiento** |  | **300.000 a 900.000** |

#### Desglose pedido: soporte evolutivo y correctivo

| Modalidad | Cobertura | Horas/mes | Tarifa ref. (COP/h) | Costo mensual (COP) |
|---|---|---:|---:|---:|
| Correctivo mínimo | incidentes + ajustes menores | 10 | 180.000 | 1.800.000 |
| Recomendado (mixto) | correctivo + mejoras continuas del flujo | 20 | 200.000 | 4.000.000 |
| Intensivo | escalamiento rápido + nuevas automatizaciones | 40 | 220.000 | 8.800.000 |

#### Escenario recomendado actualizado (con Monday ya pago)

- **Costo único preinicio:** se mantiene en **$44.298.000 COP** (no depende de la mensualidad de Monday).
- **Costo mensual esperado (objetivo):**
  - Monday incremental: **$0 COP** (si asiento ya cubierto).
  - Hosting (reuso corporativo): **$300.000 a $1.200.000 COP**.
  - Monitoreo/logs/alertamiento: **$300.000 a $900.000 COP**.
  - Soporte evolutivo/correctivo recomendado: **$4.000.000 COP**.
  - **Total mensual recomendado actualizado:** **$4.600.000 a $6.100.000 COP**.
