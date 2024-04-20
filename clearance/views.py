from django.shortcuts import render
from accounts.models import StudentAccount
from clearance.pdf_generators.clearance_report import render_report
from clearance.models import Clearance
from django.http.response import FileResponse, HttpResponse
from django.core.files.base import ContentFile
from .utils import b64decode

def download_clearance_report(request):
    clearance = request.user.studentaccount
    if not clearance.is_all_approved:
        return HttpResponse('Clearance is not approved yet!')
    report_pdf = render_report(request, clearance)
    filename = f"{clearance.student.registration} Report.pdf"
    return FileResponse(ContentFile(report_pdf), filename=filename)
    

def verify_clearance(request, b64_code):
    try:
        reg, clr_pk = b64decode(b64_code).split('-')
    except Exception as e:
        return render(request, 'clearance/verify_clearance.html', context={'message': 'Invalid Link'})
    clearance = Clearance.objects.filter(student__registration=reg, pk=clr_pk).first()
    if clearance and not clearance.is_all_approved:
        return render(request, 'clearance/verify_clearance.html', context={'message': 'Clearance is not approved yet!'})
    return render(request, 'clearance/verify_clearance.html', context={'clearance': clearance})
