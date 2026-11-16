"""Builds an EDITABLE Word version of the report from the same content as build_report.py."""
import html, re
from html.parser import HTMLParser
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from reportlab.platypus import Paragraph, Table, Preformatted, Image, Spacer, PageBreak
import build_report as br

class Runs(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.b = self.i = self.mono = 0; self.out = []
    def handle_starttag(self, t, a):
        if t == "b": self.b += 1
        elif t == "i": self.i += 1
        elif t == "font" and "Courier" in dict(a).get("face", ""): self.mono += 1
        elif t == "br": self.out.append(("\n", 0, 0, 0))
    def handle_endtag(self, t):
        if t == "b": self.b -= 1
        elif t == "i": self.i -= 1
        elif t == "font": self.mono = max(0, self.mono - 1)
    def handle_data(self, d): self.out.append((d, self.b > 0, self.i > 0, self.mono > 0))

def fill(par, markup, size=None, color=None, bold=False):
    p = Runs(); p.feed(markup)
    for text, b, i, m in p.out:
        r = par.add_run(text); r.bold = bool(b) or bold; r.italic = bool(i)
        if m: r.font.name = "Consolas"; r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcolor); tcPr.append(sh)

d = Document()
sec = d.sections[0]; sec.left_margin = sec.right_margin = Cm(2); sec.top_margin = sec.bottom_margin = Cm(1.8)
d.styles["Normal"].font.name = "Calibri"; d.styles["Normal"].font.size = Pt(9.5)
for f in br.S:
    if isinstance(f, Paragraph):
        n = f.style.name
        if n == "T":
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; fill(p, f.text, 20, RGBColor(0x1F, 0x4E, 0x79), True)
        elif n in ("s", "s2"):
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; fill(p, f.text)
        elif n == "BL":
            p = d.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = Pt(2); fill(p, f.text)
        elif n == "BL2":
            p = d.add_paragraph(style="List Bullet 2"); p.paragraph_format.space_after = Pt(1); fill(p, f.text)
        elif n == "H1": fill(d.add_heading("", 1), f.text)
        elif n == "H2": fill(d.add_heading("", 2), f.text)
        else:
            p = d.add_paragraph(); p.paragraph_format.space_after = Pt(4); fill(p, f.text)
    elif isinstance(f, Table):
        rows = f._rows; t = d.add_table(rows=len(rows), cols=len(rows[0])); t.style = "Table Grid"
        for ri, r in enumerate(rows):
            for ci, txt in enumerate(r):
                cell = t.cell(ri, ci); cell.paragraphs[0].text = ""
                head = ri == 0
                fill(cell.paragraphs[0], str(txt), 9, RGBColor(255, 255, 255) if head else None, head)
                if head: shade(cell, "1F4E79")
        d.add_paragraph()
    elif isinstance(f, Preformatted):
        p = d.add_paragraph(); r = p.add_run("\n".join(f.lines)); r.font.name = "Consolas"; r.font.size = Pt(7.5)
        shade_p = OxmlElement("w:shd"); shade_p.set(qn("w:val"), "clear"); shade_p.set(qn("w:fill"), "F2F2F2"); p._p.get_or_add_pPr().append(shade_p)
    elif isinstance(f, Image):
        d.add_picture(f.filename, width=Cm(f.drawWidth / 28.35 * 1.0))
    elif isinstance(f, PageBreak): d.add_page_break()
d.save("Report_editable.docx"); print("docx built")
