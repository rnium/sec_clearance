from django.shortcuts import render
from accounts.models import StudentAccount
from clearance.pdf_generators.clearance_report import render_report
from django.http.response import FileResponse
from django.core.files.base import ContentFile

def download_clearance_report(request):
    clearance = StudentAccount.objects.filter(registration=2018338514).first().clearance
    report_pdf = render_report(clearance)
    filename = f"{clearance.student.registration} Report.pdf"
    return FileResponse(ContentFile(report_pdf), filename=filename)
    
    
