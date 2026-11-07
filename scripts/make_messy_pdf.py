# makes a 4-page pdf with the problems cleaning has to fix (repeated header, page numbers,
# broken lines, a hyphen break, extra spaces, an empty page). the facts are made up.
# python -m scripts.make_messy_pdf

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUTPUT_PATH = "data/samples/messy_report.pdf"
HEADER = "Cellula Technologies - NLP Internship Report"

PAGES = [
    [
        "Retrieval-Augmented Generation: A Short Study",
        "",
        "Retrieval-Augmented Generation (RAG) lets a language model read external",
        "documents at question time. Because the knowledge lives in the docu-",
        "ments and not in the model weights, it can be updated without retraining.",
        "The    main    risk is that a wrong chunk leads to a wrong answer.",
    ],
    [
        "2. Models and Results",
        "",
        "We compared three models on the same test set of 2,000 questions.",
        "Model | Accuracy | Parameters",
        "BERT-base | 88.4% | 110M",
        "RoBERTa-large | 91.2% | 355M",
        "DistilBERT | 85.1% | 66M",
        "The best model, RoBERTa-large, is also the",
        "largest, which makes it slower at inference time.",
    ],
    [],
    [
        "3. Scoring",
        "",
        "The final score of each model is computed with Equation 12:",
        "score = 0.7 * accuracy + 0.3 * speed",
        "where speed is the number of questions answered per",
        "second, divided by the speed of the fastest model.",
    ],
]


def make_pdf():
    pdf = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    width, height = A4
    for page_number, lines in enumerate(PAGES, start=1):
        pdf.setFont("Helvetica", 9)
        pdf.drawString(50, height - 40, HEADER)
        pdf.drawString(width - 110, 30, f"Page {page_number} of {len(PAGES)}")

        pdf.setFont("Helvetica", 11)
        y = height - 90
        for line in lines:
            pdf.drawString(50, y, line)
            y -= 18
        pdf.showPage()
    pdf.save()
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    make_pdf()
