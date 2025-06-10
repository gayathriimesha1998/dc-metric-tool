import io
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


def generate_pdf(result_data):
    # Generate DC vs CC bar chart
    fig, ax = plt.subplots()
    ax.bar(['DC', 'CC'], [result_data['dc'], result_data['cc']], color=['#66c2a5', '#8da0cb'])
    ax.set_title('DC vs CC Complexity')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_reader = ImageReader(buf)

    pdf_stream = io.BytesIO()
    c = canvas.Canvas(pdf_stream, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "Complexity Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Filename: {result_data['filename']}")
    c.drawString(50, 705, f"Language: {result_data['language']}")
    c.drawString(50, 690, f"Decisional Complexity (DC): {result_data['dc']}")
    c.drawString(50, 675, f"Cyclomatic Complexity (CC): {result_data['cc']}")

    # Chart
    c.drawImage(img_reader, 50, 460, width=500, preserveAspectRatio=True)

    # Legend
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 440, "Heatmap Legend:")
    c.setFillColorRGB(1, 0.8, 0.8)  # red
    c.rect(160, 435, 10, 10, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(175, 440, "High DC (≥10)")

    c.setFillColorRGB(1, 1, 0.7)  # yellow
    c.rect(270, 435, 10, 10, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(285, 440, "Medium DC (5–9)")

    c.setFillColorRGB(0.8, 1, 0.8)  # green
    c.rect(390, 435, 10, 10, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(405, 440, "Low DC (0–4)")

    # Heatmap Code
    code_lines = result_data['code'].split('\n')
    line_scores = result_data.get('line_dc_map', {})
    y = 420
    c.setFont("Courier", 8)

    for idx, line in enumerate(code_lines):
        score = line_scores.get(idx + 1, 0)
        # Background color
        if score >= 10:
            c.setFillColorRGB(1, 0.8, 0.8)
        elif score >= 5:
            c.setFillColorRGB(1, 1, 0.7)
        else:
            c.setFillColorRGB(0.8, 1, 0.8)
        c.rect(45, y - 2, 510, 12, fill=1, stroke=0)

        # Text
        c.setFillColorRGB(0, 0, 0)
        line_text = f"{str(idx + 1).rjust(3)} | {line[:95]}"
        c.drawString(50, y, line_text)
        y -= 12

        if y < 50:
            c.showPage()
            y = 750
            c.setFont("Courier", 8)
 
    c.save()
    pdf_stream.seek(0)
    return pdf_stream
