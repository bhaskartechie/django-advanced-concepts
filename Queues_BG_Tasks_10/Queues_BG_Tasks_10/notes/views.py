import os

# Matplotlib for chart generation
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO

from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


# ReportLab imports (for sync)
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image as RLImage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

from .models import Note, ReportStatus
from .tasks import generate_pdf_background
from .models import ReportStatus


# from reportlab.lib.utils import
# ------------------------------------------
# 🚫 Synchronous PDF generation (blocking)
# ------------------------------------------
class GeneratePDFSyncView(LoginRequiredMixin, TemplateView):
    template_name = "notes/generate_sync.html"

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        filepath = settings.MEDIA_ROOT / f"notes_report_{user_id}.pdf"

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
                # Generate a small chart (title length)
                fig, ax = plt.subplots()
                ax.bar([0], [len(n.title)])
                ax.set_title("Title length")
                buf = BytesIO()
                fig.savefig(buf, format="png")
                buf.seek(0)
                plt.close(fig)

                # Insert the chart image
                elements.append(RLImage(buf, width=200, height=140))
                # Insert the note text
                text = f"<b>{n.title}</b><br/>{n.body}"
                elements.append(Paragraph(text, styles['BodyText']))
                elements.append(Spacer(1, 12))

                if i % 10 == 0:
                    elements.append(PageBreak())

        doc.build(elements)

        messages.success(request, "✅ PDF generated synchronously (with charts).")
        return self.get(request, *args, **kwargs)


# ------------------------------------------
# ✅ Async PDF generation (Celery + Redis)
# ------------------------------------------


class CheckReportStatusView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            report_status = get_object_or_404(ReportStatus, user=request.user)
            if report_status.is_ready:
                message = f"Your report ({report_status.filename}) is ready!"
                report_status.is_ready = False
                report_status.save()
                return JsonResponse({'status': 'ready', 'message': message})
        except ReportStatus.DoesNotExist:
            pass

        return JsonResponse({'status': 'not_ready'})


class GeneratePDFAsyncView(LoginRequiredMixin, TemplateView):
    template_name = "notes/generate_async.html"

    def post(self, request, *args, **kwargs):
        # Reset the status and start the new task
        try:
            report_status = ReportStatus.objects.get(user=request.user)
            report_status.is_ready = False
            report_status.save()
        except ReportStatus.DoesNotExist:
            pass
        generate_pdf_background.delay(request.user.id)
        messages.success(request, "PDF generation started in background (Celery).")
        return self.get(request, *args, **kwargs)
