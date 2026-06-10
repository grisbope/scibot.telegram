"""Genera un PDF con la pregunta y la respuesta de sci-bot."""

import os

from fpdf import FPDF

FONT_PATH = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD_PATH = r"C:\Windows\Fonts\arialbd.ttf"


def build_pdf(question: str, answer: str, out_path: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", FONT_PATH)
    pdf.add_font("Arial", "B", FONT_BOLD_PATH)

    pdf.set_font("Arial", "B", 14)
    pdf.multi_cell(0, 10, question)
    pdf.ln(4)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, answer)

    pdf.output(out_path)
    return out_path
