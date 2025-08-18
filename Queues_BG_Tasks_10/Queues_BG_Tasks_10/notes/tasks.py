from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from .models import Note, ReportStatus
import os
from reportlab.platypus import Image as RLImage
# Matplotlib for chart
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO

User = get_user_model()


@shared_task
def generate_pdf_background(user_id):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    filename = f"notes_report_{user_id}.pdf"
    filepath = settings.MEDIA_ROOT / filename

    notes = Note.objects.filter(user_id=user_id)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=70,
        bottomMargin=50,
    )

    elements = []
    elements.append(Paragraph("My Notes Report (with chart)", styles['Title']))
    elements.append(Spacer(1, 20))

    if not notes:
        elements.append(Paragraph("No notes available.", styles['Normal']))
    else:
        for i, n in enumerate(notes, start=1):
            fig, ax = plt.subplots()
            ax.bar([0], [len(n.title)])
            ax.set_title("Title length")
            buf = BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            plt.close(fig)

            elements.append(RLImage(buf, width=200, height=140))
            text = f"<b>{n.title}</b><br/>{n.body}"
            elements.append(Paragraph(text, styles['BodyText']))
            elements.append(Spacer(1, 12))

            if i % 10 == 0:
                elements.append(PageBreak())

    doc.build(elements)
    print(f"[Celery] PDF generated for user {user_id} (with charts)")

    # After generation, update the database
    report_status, created = ReportStatus.objects.get_or_create(user_id=user_id)
    report_status.is_ready = True
    report_status.filename = filename
    report_status.save()
    return filename
