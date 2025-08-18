from notes.views import GeneratePDFSyncView, GeneratePDFAsyncView, CheckReportStatusView
from django.urls import path

urlpatterns = [
    path("generate-sync/", GeneratePDFSyncView.as_view(), name="generate_sync"),
    path("generate-async/", GeneratePDFAsyncView.as_view(), name="generate_async"),
    path('check-report-status/', CheckReportStatusView.as_view(), name='check_report_status'),
]
