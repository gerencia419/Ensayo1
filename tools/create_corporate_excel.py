from __future__ import annotations

import csv
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

BASE = Path('.')
TEMPLATES = BASE / 'templates'
OUTPUT = TEMPLATES / 'plantilla_memorias_corporativa.xlsx'

NS_MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
NS_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS_PKG_REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS_CT = 'http://schemas.openxmlformats.org/package/2006/content-types'

ET.register_namespace('', NS_MAIN)
ET.register_namespace('r', NS_REL)


def excel_password_hash(password: str) -> str:
    password = password[:15]
    hash_val = 0
    for i, ch in enumerate(reversed(password), start=1):
        c = ord(ch)
        shifted = ((c << i) | (c >> (15 - i))) & 0x7FFF
        hash_val ^= shifted
    hash_val ^= len(password)
    hash_val ^= 0xCE4B
    return f"{hash_val:04X}"


def col(n: int) -> str:
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def sub(el, tag, attrib=None, text=None):
    node = ET.SubElement(el, f"{{{NS_MAIN}}}{tag}", attrib or {})
    if text is not None:
        node.text = text
    return node


def make_cell(row_el, ref: str, value: str = '', t: str = 'inlineStr', formula: str | None = None):
    c = sub(row_el, 'c', {'r': ref})
    if formula is not None:
        sub(c, 'f', text=formula)
        return c
    if t == 'inlineStr':
        c.set('t', 'inlineStr')
        is_el = sub(c, 'is')
        sub(is_el, 't', text=value)
    elif t == 'n':
        sub(c, 'v', text=value)
    return c


def read_csv(path: Path):
    with path.open(encoding='utf-8') as f:
        return list(csv.reader(f))


def build_sheet_input(activities_count: int):
    ws = ET.Element(f"{{{NS_MAIN}}}worksheet")
    sheet_views = sub(ws, 'sheetViews')
    view = sub(sheet_views, 'sheetView', {'workbookViewId': '0'})
    sub(view, 'pane', {'ySplit': '4', 'topLeftCell': 'A5', 'activePane': 'bottomLeft', 'state': 'frozen'})

    cols = sub(ws, 'cols')
    widths = [14,12,20,24,18,18,28,14,10,11,11,11,14,10,16,14,30,28,18]
    for i, w in enumerate(widths, start=1):
        sub(cols, 'col', {'min': str(i), 'max': str(i), 'width': str(w), 'customWidth': '1'})

    sheet_data = sub(ws, 'sheetData')

    # Row 1-2 title
    r1 = sub(sheet_data, 'row', {'r': '1'})
    make_cell(r1, 'A1', 'Plantilla de Memorias Somatec (MVP corporativo)')
    r2 = sub(sheet_data, 'row', {'r': '2'})
    make_cell(r2, 'A2', 'Diligenciar solo celdas de captura. No alterar fórmulas ni estructura.')

    headers = read_csv(TEMPLATES / 'plantilla_memorias_input.csv')[0]
    r4 = sub(sheet_data, 'row', {'r': '4'})
    for i, h in enumerate(headers, start=1):
        make_cell(r4, f"{col(i)}4", h)

    for rr in range(5, 505):
        row = sub(sheet_data, 'row', {'r': str(rr)})
        # user editable placeholders mostly blank
        for cc in [2,3,4,5,6,10,11,12,13,16,17,18]:
            make_cell(row, f"{col(cc)}{rr}", '')

        make_cell(row, f"A{rr}", '', formula=f'IF(F{rr}="","",TEXT(B{rr},"yyyymmdd")&"-"&LEFT(C{rr},4)&"-"&LEFT(D{rr},4)&"-"&F{rr}&"-{rr}")')
        make_cell(row, f"G{rr}", '', formula=f'IF(F{rr}="","",IFERROR(XLOOKUP(F{rr},CATALOGOS!$A$2:$A$500,CATALOGOS!$B$2:$B$500,"CODIGO_INVALIDO"),"CODIGO_INVALIDO"))')
        make_cell(row, f"H{rr}", '', formula=f'IF(F{rr}="","",IFERROR(XLOOKUP(F{rr},CATALOGOS!$A$2:$A$500,CATALOGOS!$C$2:$C$500,""),""))')
        make_cell(row, f"I{rr}", '', formula=f'IF(F{rr}="","",IFERROR(XLOOKUP(F{rr},CATALOGOS!$A$2:$A$500,CATALOGOS!$D$2:$D$500,""),""))')
        make_cell(row, f"N{rr}", '', formula=f'IF(F{rr}="","",IFERROR(XLOOKUP(F{rr},CATALOGOS!$A$2:$A$500,CATALOGOS!$E$2:$E$500,1),1))')
        make_cell(row, f"O{rr}", '', formula=(
            f'IF(F{rr}="","",IF(H{rr}="AREA_2D",ROUND(J{rr}*K{rr}*N{rr},4),'
            f'IF(H{rr}="VOLUMEN_3D",ROUND(J{rr}*K{rr}*L{rr}*N{rr},4),'
            f'IF(H{rr}="LINEAL_1D",ROUND(J{rr}*N{rr},4),'
            f'IF(H{rr}="CONTEO",ROUND(M{rr}*N{rr},4),"TIPO_INVALIDO")))))'
        ))
        make_cell(row, f"S{rr}", '', formula=(
            f'IF(F{rr}="","",IF(OR(C{rr}="",D{rr}="",B{rr}=""),"ERROR_CABECERA",'
            f'IF(G{rr}="CODIGO_INVALIDO","ERROR_CODIGO",IF(P{rr}="NO","BLOQUEADO_SIN_SOPORTE",'
            f'IF(AND(H{rr}="AREA_2D",OR(J{rr}<=0,K{rr}<=0)),"ERROR_DIMENSION",'
            f'IF(AND(H{rr}="VOLUMEN_3D",OR(J{rr}<=0,K{rr}<=0,L{rr}<=0)),"ERROR_DIMENSION",'
            f'IF(AND(H{rr}="LINEAL_1D",J{rr}<=0),"ERROR_DIMENSION",'
            f'IF(AND(H{rr}="CONTEO",M{rr}<=0),"ERROR_CANTIDAD","OK"))))))))'
        ))

    # summary
    r507 = sub(sheet_data, 'row', {'r': '507'})
    make_cell(r507, 'A507', 'RESUMEN DE CORTE (solo filas OK)')
    r508 = sub(sheet_data, 'row', {'r': '508'})
    for i, h in enumerate(['Código','Actividad','Unidad','Cantidad corte'], start=1):
        make_cell(r508, f"{col(i)}508", h)

    for i in range(activities_count):
        rr = 509 + i
        row = sub(sheet_data, 'row', {'r': str(rr)})
        make_cell(row, f"A{rr}", '', formula=f'IF(CATALOGOS!A{i+2}="","",CATALOGOS!A{i+2})')
        make_cell(row, f"B{rr}", '', formula=f'IF(A{rr}="","",XLOOKUP(A{rr},CATALOGOS!$A$2:$A$500,CATALOGOS!$B$2:$B$500,""))')
        make_cell(row, f"C{rr}", '', formula=f'IF(A{rr}="","",XLOOKUP(A{rr},CATALOGOS!$A$2:$A$500,CATALOGOS!$D$2:$D$500,""))')
        make_cell(row, f"D{rr}", '', formula=f'IF(A{rr}="","",SUMIFS($O$5:$O$504,$F$5:$F$504,A{rr},$S$5:$S$504,"OK"))')

    # protect sheet (password: somatec)
    sub(ws, 'sheetProtection', {
        'sheet':'1','objects':'1','scenarios':'1','formatCells':'0','formatColumns':'0','formatRows':'0',
        'insertColumns':'0','insertRows':'0','insertHyperlinks':'0','deleteColumns':'0','deleteRows':'0',
        'selectLockedCells':'1','sort':'0','autoFilter':'0','pivotTables':'0','password':excel_password_hash('somatec')
    })

    merge = sub(ws, 'mergeCells', {'count':'2'})
    sub(merge, 'mergeCell', {'ref':'A1:S1'})
    sub(merge, 'mergeCell', {'ref':'A2:S2'})

    # validations (formula1/formula2 as child nodes, and placed after mergeCells)
    dvs = sub(ws, 'dataValidations', {'count': '8'})
    dv = sub(dvs, 'dataValidation', {'type':'date','sqref':'B5:B504','allowBlank':'1','operator':'between'})
    sub(dv, 'formula1', text='DATE(2024,1,1)')
    sub(dv, 'formula2', text='DATE(2035,12,31)')

    dv = sub(dvs, 'dataValidation', {'type':'list','sqref':'C5:C504','allowBlank':'0'})
    sub(dv, 'formula1', text='=CATALOGOS!$G$2:$G$500')
    dv = sub(dvs, 'dataValidation', {'type':'list','sqref':'D5:D504','allowBlank':'0'})
    sub(dv, 'formula1', text='=CATALOGOS!$H$2:$H$500')
    dv = sub(dvs, 'dataValidation', {'type':'list','sqref':'F5:F504','allowBlank':'0'})
    sub(dv, 'formula1', text='=CATALOGOS!$A$2:$A$500')
    dv = sub(dvs, 'dataValidation', {'type':'decimal','sqref':'J5:N504','allowBlank':'1','operator':'greaterThanOrEqual'})
    sub(dv, 'formula1', text='0')
    dv = sub(dvs, 'dataValidation', {'type':'list','sqref':'P5:P504','allowBlank':'0'})
    sub(dv, 'formula1', text='"SI,NO"')
    dv = sub(dvs, 'dataValidation', {'type':'textLength','sqref':'Q5:Q504','allowBlank':'1','operator':'lessThanOrEqual'})
    sub(dv, 'formula1', text='255')
    dv = sub(dvs, 'dataValidation', {'type':'textLength','sqref':'R5:R504','allowBlank':'1','operator':'lessThanOrEqual'})
    sub(dv, 'formula1', text='255')
    return ET.tostring(ws, encoding='utf-8', xml_declaration=True)


def build_sheet_catalogs():
    ws = ET.Element(f"{{{NS_MAIN}}}worksheet")
    sheet_data = sub(ws, 'sheetData')

    activities = read_csv(TEMPLATES / 'catalogo_actividades.csv')
    obras = read_csv(TEMPLATES / 'catalogo_obras.csv')
    contratistas = read_csv(TEMPLATES / 'catalogo_contratistas.csv')

    rows: dict[int, ET.Element] = {}

    def get_row(r: int) -> ET.Element:
        if r not in rows:
            rows[r] = sub(sheet_data, 'row', {'r': str(r)})
        return rows[r]

    for r, row_values in enumerate(activities, start=1):
        row = get_row(r)
        for c, val in enumerate(row_values, start=1):
            make_cell(row, f"{col(c)}{r}", val)

    # additional lists in G/H columns (same physical rows, no duplicates)
    row = get_row(1)
    make_cell(row, 'G1', 'obras')
    make_cell(row, 'H1', 'contratistas')

    for i, vals in enumerate(obras[1:], start=2):
        row = get_row(i)
        make_cell(row, f'G{i}', vals[0])

    for i, vals in enumerate(contratistas[1:], start=2):
        row = get_row(i)
        make_cell(row, f'H{i}', vals[0])

    sub(ws, 'sheetProtection', {'sheet':'1','objects':'1','scenarios':'1','password':excel_password_hash('somatec')})
    return ET.tostring(ws, encoding='utf-8', xml_declaration=True)


def build_sheet_instructivo():
    ws = ET.Element(f"{{{NS_MAIN}}}worksheet")
    sheet_data = sub(ws, 'sheetData')
    lines = [
        'INSTRUCTIVO DE USO - Plantilla corporativa',
        '1) Diligencie solo celdas de captura en INPUT (B,C,D,E,F,J,K,L,M,P,Q,R).',
        '2) No modifique formulas, encabezados ni estructura de hojas.',
        '3) Seleccione Código actividad desde lista; actividad/tipo/unidad se autocompletan.',
        '4) Cantidad conmutada se calcula por tipo: AREA_2D, VOLUMEN_3D, LINEAL_1D, CONTEO.',
        '5) Solo filas con Estado validación = OK entran al RESUMEN DE CORTE.',
        '6) Si Soporte = NO la fila queda bloqueada para aprobación.',
        '7) Contraseña de protección inicial: somatec (cambiar en operación).',
    ]
    for i, txt in enumerate(lines, start=1):
        row = sub(sheet_data, 'row', {'r': str(i)})
        make_cell(row, f'A{i}', txt)
    sub(ws, 'sheetProtection', {'sheet':'1','objects':'1','scenarios':'1','password':excel_password_hash('somatec')})
    return ET.tostring(ws, encoding='utf-8', xml_declaration=True)


def workbook_xml():
    root = ET.Element(f"{{{NS_MAIN}}}workbook")
    book_views = sub(root, 'bookViews')
    sub(book_views, 'workbookView', {'xWindow':'0','yWindow':'0','windowWidth':'24000','windowHeight':'12000'})
    sheets = sub(root, 'sheets')
    ET.SubElement(sheets, f"{{{NS_MAIN}}}sheet", {'name':'INPUT','sheetId':'1',f'{{{NS_REL}}}id':'rId1'})
    ET.SubElement(sheets, f"{{{NS_MAIN}}}sheet", {'name':'CATALOGOS','sheetId':'2',f'{{{NS_REL}}}id':'rId2'})
    ET.SubElement(sheets, f"{{{NS_MAIN}}}sheet", {'name':'INSTRUCTIVO','sheetId':'3',f'{{{NS_REL}}}id':'rId3'})
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def styles_xml():
    return b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border/></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''


def write_static(zipf: ZipFile, name: str, data: bytes):
    zipf.writestr(name, data)


def build_xlsx() -> None:
    activities_count = len(read_csv(TEMPLATES / 'catalogo_actividades.csv')) - 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(OUTPUT, 'w', ZIP_DEFLATED) as z:
        write_static(z, '[Content_Types].xml', b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>''')

        write_static(z, '_rels/.rels', b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>''')

        write_static(z, 'xl/workbook.xml', workbook_xml())
        write_static(z, 'xl/styles.xml', styles_xml())

        write_static(z, 'xl/_rels/workbook.xml.rels', b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>''')

        write_static(z, 'xl/worksheets/sheet1.xml', build_sheet_input(activities_count))
        write_static(z, 'xl/worksheets/sheet2.xml', build_sheet_catalogs())
        write_static(z, 'xl/worksheets/sheet3.xml', build_sheet_instructivo())

    print(f'Created corporate Excel template: {OUTPUT}')


if __name__ == '__main__':
    build_xlsx()
