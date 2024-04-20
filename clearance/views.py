from django.shortcuts import render
from accounts.models import StudentAccount
from clearance.pdf_generators.clearance_report import render_report
from clearance.models import Clearance
from django.http.response import FileResponse, HttpResponse
from django.core.files.base import ContentFile
from .utils import b64decode

def download_clearance_report(request):
    clearance = StudentAccount.objects.filter(registration=2018338514).first().clearance
    report_pdf = render_report(request, clearance)
    filename = f"{clearance.student.registration} Report.pdf"
    return FileResponse(ContentFile(report_pdf), filename=filename)
    

def verify_clearance(request, b64_code):
    try:
        reg, clr_pk = b64decode(b64_code).split('-')
        clearance = Clearance.objects.get(student__registation=reg, pk=clr_pk)
    except Exception as e:
        return HttpResponse('Invalid Clearance')
    
    return HttpResponse(clearance)
